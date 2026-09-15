import time
import os
import sys
from eao_kernel_p13b_unified import (
    Journal, Prime, EAORefusal, TaskIdRejected, 
    E_ID_CASE_VARIANT, E_ID_MALFORMED, BudgetExhausted, 
    validate_task_id, get_effect_path, append_dispatch_log_and_fsync, 
    publish, unlink_with_backoff, evaluate_gate, EAOGateRefusal
)
from predicates import enforce_L1_no_skip, enforce_artifact_naming_grammar

def run_eao_kernel_loop(run_id: str, phase_number: int, epoch: int, task_payload: bytes):
    root_dir = os.path.abspath(os.path.join(os.getcwd(), ".wwl_kernel"))
    os.makedirs(root_dir, exist_ok=True)

    # STEP 1: Schema + open (C1, C4 together)
    # Journal initializes WAL, sets COLLATE NOCASE, and UNIQUE(task_id, phase)
    print("[1] Opening Journal (C1, C4 schema enforced)")
    journal = Journal(root_dir, writer="prime")
    journal.initialize_budget(run_id, initial_amount=999, epoch=epoch)

    prime = Prime("p13b-kernel")
    task_id = prime.issue()

    # STEP 2: Digest-keyed effect naming (C5)
    effect_path = get_effect_path(root_dir, task_id)
    print(f"[2] Computed digest-keyed effect path: {effect_path}")

    # STEP 3 & 4: Fused budget transaction (C3) and INTENT row
    print(f"[3/4] Fusing budget transaction and writing INTENT row for {task_id}")
    try:
        journal.intent_with_budget(task_id, run_id, epoch, payload=task_payload, prime=prime)
    except BudgetExhausted as e:
        print(f"[-] Budget Exhausted: {e}")
        return
    except TaskIdRejected as e:
        print(f"[-] Task ID Rejected: {e}")
        return

    # STEP 5: Dispatch (subagent)
    # Write to external dispatch log (C8 requirement)
    dispatch_log = os.path.join(root_dir, "dispatch.log")
    append_dispatch_log_and_fsync(dispatch_log, task_id, b"DISPATCH_T0_NATIVE")
    print(f"[5] Dispatched native task {task_id}")

    # (Simulated native subagent work)
    worker_result_data = b"WORKER_OUTPUT_MOCKED"

    # STEP 6: Publish the effect (C6) + delete ladder (C7)
    # The worker publishes the result to the effect path
    print("[6] Publishing effect via I6 bounded retry (C6)")
    publish(effect_path, worker_result_data)

    # Simulated worker receipts terminal delivery
    print("[7] Writing TERMINAL row")
    journal.terminal(task_id, payload=b"SUCCESS")
    
    # Clean up effect safely via C7 delete ladder if needed
    # For now, leaving the effect file since it represents the output.

    # STEP 8: Reconcile both ways (C8)
    print("[8] Reconciling intent vs terminal and dispatch vs intent")
    # Read dispatched from dispatch.log
    dispatched_ids = []
    if os.path.exists(dispatch_log):
        with open(dispatch_log, "rb") as f:
            for line in f:
                parts = line.split(b"|")
                if len(parts) >= 2:
                    dispatched_ids.append(parts[1].decode("utf-8"))
                    
    diff = journal.reconcile(dispatched=dispatched_ids)
    
    # Gate Evaluation
    try:
        print("[*] Evaluating EAO Gate...")
        result = evaluate_gate(diff, "SUCCESS", True, True, True)
        print(f"[+] Gate passed: {result}")
    except EAOGateRefusal as e:
        print(f"[-] Gate Refused: {e}")

    # STEP 9: Oracle (C9) - (Handled externally via JSONL parse, out of band)
    print("[9] Oracle telemetry ready for external parsing.")

if __name__ == "__main__":
    run_eao_kernel_loop("run_test_01", 1, 0, b"compile_spec")
