import json
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

class EAOGateRefusal(Exception): pass
class MissingReceiptField(EAOGateRefusal): pass
class OverflowRefusal(EAOGateRefusal): pass

@dataclass
class Receipt:
    run_id: str
    phase: str
    task_id: str
    lane: str
    terminal_state: str  # SUCCESS, FAILED(reason), CLEAN_NO_OP
    rung: Optional[str]
    artifact_paths: List[str]
    stay_ids: List[str]
    not_verified: List[str]
    tokens_in: int
    tokens_out: int
    apply_plan_actual: str
    next_actions: List[str]
    blocker: Optional[str]
    trust_tier: str
    write_scope_digest: str
    capability_attested_by: str
    merkle_leaf_index: int

def collect(raw_receipts: List[Dict[str, Any]]) -> List[Receipt]:
    """
    Collects raw T0/T1 receipts and validates them against the ABI schema.
    Enforces I1 Flat Prime (no body fields) and I2 Receipt Size Caps.
    """
    compiled = []
    for raw in raw_receipts:
        # Enforce exact ceiling
        if len(json.dumps(raw)) > 2048:
            raise OverflowRefusal(f"FAILED(receipt_overflow) for task {raw.get('task_id', 'unknown')}")
        
        # Enforce I1 explicitly before parsing
        if "body" in raw or "content" in raw or "payload" in raw:
             raise EAOGateRefusal("I1 Violation: Worker body/content field found in receipt.")
        
        try:
            r = Receipt(**raw)
            compiled.append(r)
        except TypeError as e:
            raise MissingReceiptField(f"FAILED(schema_invalid): {e}")
            
    return compiled

def evaluate_gate(
    reconcile_diff: Dict[str, list], 
    phase_resolution: str, 
    artifacts_verified: bool, 
    stay_ids_written: bool, 
    ledger_row_written: bool
) -> str:
    """
    Evaluates whether the phase is eligible for an auto-CONTINUE.
    Fails closed on any violation.
    """
    if reconcile_diff.get("intent_without_terminal"):
        raise EAOGateRefusal("I2 Violation: Orphan tasks exist. Phase cannot close.")
    
    if reconcile_diff.get("intent_without_dispatch"):
        raise EAOGateRefusal("C8 Violation: Journaled tasks not dispatched.")
        
    if not artifacts_verified:
        raise EAOGateRefusal("I4 Violation: Artifacts not present/verified.")
        
    if not stay_ids_written or not ledger_row_written:
        raise EAOGateRefusal("I4 Violation: Stay IDs and ledger row mandatory for continue.")
        
    if phase_resolution != "SUCCESS":
        # Note: CLEAN_NO_OP is a valid terminal state, but NOT an authority to advance (per R15).
        raise EAOGateRefusal(f"Gate blocked: Resolution must be SUCCESS, got {phase_resolution}")
        
    return "CONTINUE"

def run_tests():
    print("==================================================")
    print(" ACCEPTANCE PROOF: COLLECT (ABI ENFORCEMENT)")
    print("==================================================")
    
    # 1. Reject receipt with body (I1)
    bad_receipt_1 = {"run_id": "r1", "task_id": "t1", "body": "some text"}
    try:
        collect([bad_receipt_1])
        print("[FAIL] Collect accepted a receipt with a body.")
    except EAOGateRefusal as e:
        print(f"[PASS] Collect refused body payload: {e}")
        
    # 2. Reject missing schema fields
    bad_receipt_2 = {"run_id": "r1", "task_id": "t2"}
    try:
        collect([bad_receipt_2])
        print("[FAIL] Collect accepted incomplete schema.")
    except MissingReceiptField as e:
        print(f"[PASS] Collect enforced full schema: {str(e)[:50]}...")
        
    print("\n==================================================")
    print(" ACCEPTANCE PROOF: GATE (AUTO-CONTINUE)")
    print("==================================================")
    
    # 3. Clean Reconcile but CLEAN_NO_OP (R15)
    clean_diff = {"intent_without_terminal": [], "intent_without_dispatch": []}
    try:
        evaluate_gate(clean_diff, "CLEAN_NO_OP", True, True, True)
        print("[FAIL] Gate advanced on CLEAN_NO_OP.")
    except EAOGateRefusal as e:
        print(f"[PASS] Gate refused CLEAN_NO_OP advance (R15): {e}")
        
    # 4. Success but Orphan Tasks Exist (I2)
    orphan_diff = {"intent_without_terminal": ["task-3"], "intent_without_dispatch": []}
    try:
        evaluate_gate(orphan_diff, "SUCCESS", True, True, True)
        print("[FAIL] Gate advanced despite orphan tasks.")
    except EAOGateRefusal as e:
        print(f"[PASS] Gate refused advance due to orphans (I2): {e}")
        
    # 5. Perfect Run
    result = evaluate_gate(clean_diff, "SUCCESS", True, True, True)
    print(f"[PASS] Gate returned {result} on perfect phase conditions.")

if __name__ == "__main__":
    run_tests()
