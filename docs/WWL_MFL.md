# WWL Mini Fix Loop (MFL)

Addendum to Work Work Loop 1.1.0. Does not replace L1–L10. Names the repair loop L4 already requires.

## Intent

After a chamber builds or tests, do not shrug and continue, and do not repair the whole product forever. WWL already counts failed gates (`failed_attempts_count`, max 3, then L5 split). MFL gives that counter two branches.

## Loop

```
build or test this chamber
        │
        ▼
       MFL
        │
   A) chamber broken ──► derive fix for THIS deliverable
        │                  apply (see plane)
        │                  test
        └── MFL            (same phase; cap 3)
        │
   B) chamber not broken ► bughunt (file only)
                           STOP the loop
                           human CONTINUE
```

## Laws

1. **Cap 3** A-cycles per chamber. Maps to harness `max_failed_attempts = 3`. Fourth attempt is L5 split (`Na > Nb`) or STOP. Not “one more try.”
2. **Scope freeze** at loop open. No new phase, no START rewrite, no lock flip.
3. **Plane.**
   - BIBLE / plan-level chambers: A may rewrite the current phase artifact only.
   - BUILD phases that named files: A may touch only those named files.
   - A composed assumptive/PAPR plane (if present) cannot apply world effects.
4. **B does not apply.** Hunt → file a bug → human `continue`. B never auto-continues.
5. **Caller-graded Pass 2 is not “nothing broken.”** Pass 1 fail or a named test red → branch A.
6. **L8.** STOP freezes MFL. CONTINUE after a green B advances the spine.

## What MFL is not

- Not a new spine.
- Not a daemon.
- Not permission to patch the runtime from a BIBLE test/break chamber.
- Not “fix every backlog bug before continue.”

## Harness mapping (already present)

| MFL | `engine/hybrid_gate_harness.py` |
|---|---|
| A-cycle | Pass 1/2 fail → `failed_attempts_count += 1` |
| Cap 3 | `max_failed_attempts` |
| Fourth | loop-breaker log + L5 suggestion |
| Green B | fail counter reset on successful gate |
