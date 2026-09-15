"""EAO kernel P13b-prime
Includes C1-C8 + C10 + Refusal Registry.
"""
import os, re, time, sqlite3, tempfile, msvcrt, secrets, hashlib, ctypes, shutil
from ctypes import wintypes

# ----------------------------------------------------------------
# REFUSAL REGISTRY
# ----------------------------------------------------------------
class EAORefusal(Exception): pass
class TaskIdRejected(EAORefusal): pass
class E_ID_CASE_VARIANT(TaskIdRejected): pass
class E_ID_MALFORMED(TaskIdRejected): pass
class PrimeLockHeld(EAORefusal): pass
class PublishExhausted(EAORefusal): pass
class DeleteExhausted(EAORefusal): pass
class DeleteDeferred(EAORefusal): pass
class DeleteUnreconciled(EAORefusal): pass
class BudgetExhausted(EAORefusal): pass
class StateUnreadable(EAORefusal): pass
class UnattestedReceipt(EAORefusal): pass

# ----------------------------------------------------------------
# C4: Charset & Canonical Key
# ----------------------------------------------------------------
TASKID_RE = re.compile(r"\A[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}\Z")

def canonical_key(task_id: str) -> str:
    """Matches SQLite's NOCASE collation (ASCII fold only)."""
    return "".join(c.lower() if 'A' <= c <= 'Z' else c for c in task_id)

def validate_task_id(task_id: str) -> str:
    if not isinstance(task_id, str):
        raise E_ID_MALFORMED("task_id not a str")
    if not TASKID_RE.match(task_id):
        raise E_ID_MALFORMED(f"task_id charset/shape rejected: {task_id}")
    if canonical_key(task_id) != task_id.lower():
        raise E_ID_MALFORMED(f"E_ID_MALFORMED: Unicode fold divergence on {task_id}")
    return task_id

# ----------------------------------------------------------------
# C1, C3: SQLite/WAL Journal + Budget
# ----------------------------------------------------------------
DDL_JOURNAL = """
CREATE TABLE IF NOT EXISTS journal (
  row_id  INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id TEXT NOT NULL COLLATE NOCASE,
  phase   TEXT NOT NULL CHECK (phase IN ('INTENT','TERMINAL')),
  ts      REAL NOT NULL,
  writer  TEXT NOT NULL,
  payload BLOB,
  UNIQUE (task_id, phase)
);
"""

DDL_BUDGET = """
CREATE TABLE IF NOT EXISTS budget (
  run_id TEXT PRIMARY KEY,
  remaining INTEGER NOT NULL,
  fence_epoch INTEGER NOT NULL
);
"""

class Prime:
    def __init__(self, prime_id):
        self.prime_id = validate_task_id(prime_id)
        self._n = 0
        self._issued = set()
    def issue(self):
        self._n += 1
        tid = "%s-%06d-%s" % (self.prime_id, self._n, secrets.token_hex(4))
        validate_task_id(tid)
        self._issued.add(tid)
        return tid
    def is_mine(self, tid):
        return tid in self._issued

class Journal:
    def __init__(self, root, writer="w0", sync="FULL", timeout_s=60):
        self.root = root
        os.makedirs(root, exist_ok=True)
        self.path = os.path.join(root, "eao.journal.sqlite3")
        self.writer = writer
        self.db = sqlite3.connect(self.path, timeout=timeout_s, isolation_level=None)
        self.journal_mode = self.db.execute("PRAGMA journal_mode=wal").fetchone()[0]
        self.db.execute(f"PRAGMA synchronous={sync}")
        self.db.execute("PRAGMA busy_timeout=30000")
        self.db.execute(DDL_JOURNAL)
        self.db.execute(DDL_BUDGET)
        
    def close(self):
        try: self.db.close()
        except Exception: pass

    def initialize_budget(self, run_id, initial_amount, epoch):
        self.db.execute("INSERT OR IGNORE INTO budget (run_id, remaining, fence_epoch) VALUES (?, ?, ?)", 
                        (run_id, initial_amount, epoch))

    def intent_with_budget(self, task_id, run_id, epoch, payload=b"", prime=None):
        """C3: Fused budget decrement with INTENT row."""
        validate_task_id(task_id)
        if prime is not None and not prime.is_mine(task_id):
            raise TaskIdRejected(f"task_id not issued by this Prime: {task_id}")
            
        try:
            self.db.execute("BEGIN IMMEDIATE")
            cur = self.db.execute(
                "UPDATE budget SET remaining = remaining - 1 WHERE run_id=? AND remaining > 0 AND fence_epoch <= ?",
                (run_id, epoch)
            )
            if cur.rowcount == 0:
                self.db.execute("ROLLBACK")
                raise BudgetExhausted("Phase budget exhausted or fence_epoch mismatch.")
                
            self.db.execute(
                "INSERT INTO journal (task_id,phase,ts,writer,payload) VALUES (?,?,?,?,?)",
                (task_id, "INTENT", time.time(), self.writer, payload)
            )
            self.db.execute("COMMIT")
        except sqlite3.IntegrityError as e:
            self.db.execute("ROLLBACK")
            raise TaskIdRejected(f"E_ID_CASE_VARIANT or duplicate: {e}")
        except Exception:
            self.db.execute("ROLLBACK")
            raise

    def terminal(self, task_id, payload=b"", prime=None):
        validate_task_id(task_id)
        try:
            self.db.execute(
                "INSERT INTO journal (task_id,phase,ts,writer,payload) VALUES (?,?,?,?,?)",
                (task_id, "TERMINAL", time.time(), self.writer, payload)
            )
        except sqlite3.IntegrityError as e:
            raise TaskIdRejected(f"duplicate TERMINAL: {e}")

    def ids(self, phase):
        return set(r[0] for r in self.db.execute("SELECT task_id FROM journal WHERE phase=?", (phase,)))

    def reconcile(self, dispatched=None):
        """C8: Reconcile by set-difference both ways."""
        i, t = self.ids("INTENT"), self.ids("TERMINAL")
        out = {
            "intent_without_terminal": sorted(i - t),
            "terminal_without_intent": sorted(t - i),
            "n_intent": len(i), "n_terminal": len(t),
        }
        if dispatched is not None:
            d = set(dispatched)
            out["dispatched_without_intent"] = sorted(d - i)
            out["intent_without_dispatch"] = sorted(i - d)
        return out

    def integrity(self):
        return self.db.execute("PRAGMA integrity_check").fetchone()[0]

# ----------------------------------------------------------------
# C6, C7: I6 Publish Form & Delete Ladder
# ----------------------------------------------------------------
def publish(dst, data, attempts=6, base=0.05, log=None):
    """C6: keyed temp -> fsync -> os.replace under bounded exponential backoff.
    retry-class {5} for os.replace"""
    d = os.path.dirname(os.path.abspath(dst)) or "."
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".pub-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        
        last = None
        for n in range(1, attempts + 1):
            try:
                os.replace(tmp, dst)
                if log is not None: log.append(("ok", n))
                tmp = None
                return n
            except OSError as e:
                last = e
                winerror = getattr(e, "winerror", None)
                if log is not None:
                    log.append((f"{type(e).__name__}:{winerror}", n))
                
                if n == attempts:
                    break
                time.sleep(base * (2 ** (n - 1)))
                
        raise PublishExhausted(f"os.replace exhausted after {attempts} attempts: {last}")
    finally:
        if tmp and os.path.exists(tmp):
            try: os.unlink(tmp)
            except OSError: pass

def unlink_with_backoff(path, attempts=8, base=0.05):
    """C7: Delete ladder for unlink. retry-class {32}."""
    if not os.path.exists(path):
        return
        
    last = None
    for n in range(1, attempts + 1):
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.unlink(path)
            return
        except OSError as e:
            last = e
            winerror = getattr(e, "winerror", None)
            
            # C7: WinError 5 on attempt 1 -> DeleteExhausted (NOT ENQUEUED)
            if winerror == 5 and n == 1:
                raise DeleteExhausted("WinError 5 on unlink attempt 1.")
                
            if winerror != 32:
                raise DeleteExhausted(f"Non-deferrable unlink error: {e}")
                
            if n == attempts:
                break
            time.sleep(base * (2 ** (n - 1)))
            
    # C7: Deferred after 8 attempts on WinError 32
    raise DeleteDeferred(f"Deferred unlink due to WinError 32: {last}")

# ----------------------------------------------------------------
# C5, C8: Dispatch log and Digest-keyed paths
# ----------------------------------------------------------------
def get_effect_path(root_dir, task_id):
    """C5: Digest-keyed effect paths."""
    digest = hashlib.sha256(b"eao-effect-v1\x00" + task_id.encode('utf-8')).hexdigest()[:32]
    return os.path.join(root_dir, digest + ".eff")

def append_dispatch_log_and_fsync(log_path, task_id, payload):
    """C8: dispatch.log must be write + flush + fsync outside the journal"""
    with open(log_path, "ab") as f:
        f.write(f"{time.time()}|{task_id}|{payload}\n".encode('utf-8'))
        f.flush()
        os.fsync(f.fileno())

# ----------------------------------------------------------------
# C10: ADS Observer
# ----------------------------------------------------------------
kernel32 = ctypes.windll.kernel32

class WIN32_FIND_STREAM_DATA(ctypes.Structure):
    _fields_ = [
        ("StreamSize", wintypes.LARGE_INTEGER),
        ("cStreamName", wintypes.WCHAR * 296)
    ]

def iter_streams(filepath):
    """C10: FindFirstStreamW wrapper to enumerate streams on files AND directories."""
    data = WIN32_FIND_STREAM_DATA()
    # FindExInfoStandard = 0
    handle = kernel32.FindFirstStreamW(str(filepath), 0, ctypes.byref(data), 0)
    
    if handle == wintypes.HANDLE(-1).value:
        err = ctypes.GetLastError()
        # ERROR_HANDLE_EOF (38) or ERROR_FILE_NOT_FOUND (2)
        if err in (2, 38):
            return
        raise ctypes.WinError(err)
    
    try:
        while True:
            yield data.cStreamName
            if not kernel32.FindNextStreamW(handle, ctypes.byref(data)):
                break
    finally:
        kernel32.FindClose(handle)

def validate_ads(filepath):
    """C10: Diff differentially, never flag presence. Allow-list exactly three natural names."""
    ALLOWED_STREAMS = {":Zone.Identifier:$DATA", ":SmartScreen:$DATA", ":BDU:$DATA"}
    for stream_name in iter_streams(filepath):
        if stream_name == "::$DATA":
            continue
        if stream_name not in ALLOWED_STREAMS:
            raise CapabilityViolation(f"Non-allow-listed ADS detected: {stream_name} on {filepath}")
        # Note: A real diff implementation would hash the content of allowed streams 
        # to ensure they haven't been tampered with between manifest points.

# ----------------------------------------------------------------
# Putting it all together: Execution Shape
# ----------------------------------------------------------------
def execute_task(journal, task_id, run_id, epoch, payload, log_path, effect_dir):
    validate_task_id(task_id)
    
    # 1. INTENT must be committed BEFORE dispatch (C2) and fused with budget (C3)
    journal.intent_with_budget(task_id, run_id, epoch, payload=payload)
    
    # 2. Dispatch log outside the journal + fsync (C8)
    append_dispatch_log_and_fsync(log_path, task_id, payload)
    
    # 3. Work happens (Mocked here)
    effect_data = b"WORK_DONE"
    
    # 4. Digest-keyed paths (C5) 
    effect_path = get_effect_path(effect_dir, task_id)
    
    # 5. Publish under bounded backoff (C6, C7)
    publish(effect_path, effect_data)
    
    # 6. Validate ADS (C10)
    validate_ads(effect_path)
    
    # 7. TERMINAL state committed
    journal.terminal(task_id, payload=b"SUCCESS")

if __name__ == "__main__":
    scratch_root = os.path.abspath(r"D:\BEACON_HQ\PROJECTS\00_ACTIVE\eao-kernel\.p13b-scratch")
    os.makedirs(scratch_root, exist_ok=True)
    
    j = Journal(scratch_root)
    print("Journal initialized with WAL:", j.journal_mode)
    print("P13b-prime setup complete.")
