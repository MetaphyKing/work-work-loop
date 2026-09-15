import os
import sys
from eao_kernel_p13b_unified import (
    Journal, Prime, EAORefusal, TaskIdRejected, 
    BudgetExhausted, validate_task_id, get_effect_path, 
    append_dispatch_log_and_fsync, publish, evaluate_gate, EAOGateRefusal
)
from predicates import enforce_L1_no_skip

def run_phase(journal, prime, run_id, phase, epoch, lane_name, task_payload, root_dir):
    print(f"--- Starting Phase {phase} ({lane_name}) ---")
    
    enforce_L1_no_skip(phase - 1, phase, False)

    task_id = prime.issue()
    effect_path = get_effect_path(root_dir, task_id)
    
    try:
        journal.intent_with_budget(task_id, run_id, epoch, payload=task_payload, prime=prime)
    except Exception as e:
        print(f"Failed intent: {e}")
        return False
        
    dispatch_log = os.path.join(root_dir, "dispatch.log")
    append_dispatch_log_and_fsync(dispatch_log, task_id, f"DISPATCH_{lane_name}".encode("utf-8"))
    
    publish(effect_path, b"DUMMY_ARTIFACT_DATA")
    
    journal.terminal(task_id, payload=b"SUCCESS")
    
    dispatched_ids = []
    if os.path.exists(dispatch_log):
        with open(dispatch_log, "rb") as f:
            for line in f:
                parts = line.split(b"|")
                if len(parts) >= 2:
                    dispatched_ids.append(parts[1].decode("utf-8"))
                    
    diff = journal.reconcile(dispatched=dispatched_ids)
    
    try:
        result = evaluate_gate(diff, "SUCCESS", artifacts_verified=True, stay_ids_written=True, ledger_row_written=True)
        print(f"Phase {phase} Gate passed: {result}")
        return result
    except EAOGateRefusal as e:
        print(f"Phase {phase} Gate refused: {e}")
        return None

def main():
    root_dir = os.path.abspath(os.path.join(os.getcwd(), ".wwl_kernel_thin_run"))
    os.makedirs(root_dir, exist_ok=True)
    
    # Clean previous dispatch log if exists to not carry over state
    dispatch_log = os.path.join(root_dir, "dispatch.log")
    if os.path.exists(dispatch_log):
        os.remove(dispatch_log)
    
    run_id = "thin_run_01"
    epoch = 1
    
    journal = Journal(root_dir, writer="prime")
    journal.initialize_budget(run_id, initial_amount=1000, epoch=epoch)
    prime = Prime("p13b-kernel")
    
    res1 = run_phase(journal, prime, run_id, 1, epoch, "T0_NATIVE", b"T0_TASK", root_dir)
    if res1 != "CONTINUE":
        print("Run terminated at Phase 1.")
        return
        
    res2 = run_phase(journal, prime, run_id, 2, epoch, "T1_IFCH", b"T1_TASK", root_dir)
    if res2 == "CONTINUE":
        print("Run successfully terminated after Phase 2.")
        
if __name__ == "__main__":
    main()
