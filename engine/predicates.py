import re
import os
from typing import Dict, List, Optional
from eao_kernel_p13b_unified import EAOGateRefusal

class WWLLawViolation(EAOGateRefusal): pass

def enforce_L1_no_skip(current_phase: int, target_phase: int, has_skip_flag: bool):
    """L1: target_phase == current + 1 strict, and no skip affordance exists."""
    if target_phase != current_phase + 1:
        raise WWLLawViolation(f"L1 Violation: Target phase {target_phase} is not consecutive to {current_phase}.")
    if has_skip_flag:
        raise WWLLawViolation("I5/L1 Violation: Skip affordance detected in execution parameters.")

def enforce_L2_work_then_deliver(artifact_mtime: float, gate_emission_time: float):
    """L2: artifact mtime precedes gate-line emission."""
    if artifact_mtime > gate_emission_time:
        raise WWLLawViolation("L2 Violation: Artifact modified after gate emission.")

def enforce_L3_chat_plus_artifact(has_chat: bool, has_artifact: bool):
    """L3: both present, else refuse."""
    if not (has_chat and has_artifact):
        raise WWLLawViolation("L3 Violation: Both chat delivery and named artifact are required.")

def enforce_L4_score_all_six(scores: Dict[str, float]):
    """L4: all six axes required present; missing is refusal, not 0.0."""
    required = ["S1_intent", "S2_scope", "S3_evidence", "S4_completeness", "S5_fit", "S6_next"]
    for axis in required:
        if axis not in scores:
            raise WWLLawViolation(f"L4 Violation: Missing score for axis {axis}. Refusing.")
        if scores[axis] < 0.99: # Allowing float precision matching >= 99%
            raise WWLLawViolation(f"L4 Violation: Score for {axis} is below 99%.")

def enforce_L5_context_ceiling(current_tokens: int, ceiling: int):
    """L5: context-budget predicate; over ceiling triggers auto-split."""
    if current_tokens > ceiling:
        raise WWLLawViolation(f"L5 Violation: Context budget exceeded ({current_tokens} > {ceiling}). Auto-split required.")

def enforce_L6_evidence_over_claims(claims: List[Dict[str, str]]):
    """L6: every claim carries a path, id, or URL, or is tagged UNGROUNDED."""
    for claim in claims:
        has_evidence = any(k in claim for k in ["path", "id", "url"])
        if not has_evidence and claim.get("tag") != "UNGROUNDED":
            raise WWLLawViolation("L6 Violation: Claim lacks evidence (path/id/url) and is not tagged UNGROUNDED.")

def enforce_L7_exhaustion_is_split(terminal_state: str):
    """L7: EXHAUSTED can never map to SUCCESS."""
    if terminal_state == "EXHAUSTED":
        raise WWLLawViolation("L7 Violation: EXHAUSTED state cannot map to SUCCESS; it must yield a split.")

def enforce_L8_human_stop(stop_signal_present: bool):
    """L8: human STOP pre-empts always."""
    if stop_signal_present:
        raise WWLLawViolation("L8 Violation: Human STOP signal detected. Halting.")

def enforce_L9_no_replay_after_P20(current_phase: int, target_phase: int):
    """L9: spine transition guard."""
    if current_phase >= 20 and target_phase <= 20:
        raise WWLLawViolation("L9 Violation: Replay of P01-P20 not permitted after crossing P20 spine transition.")

def enforce_L10_improve_wording_never_goal(start_intent_hash: str, current_intent_hash: str):
    """L10: intent hash pinned at START, compared at every gate."""
    if start_intent_hash != current_intent_hash:
        raise WWLLawViolation("L10 Violation: Intent hash drift detected. Improving wording is never the goal.")

def enforce_artifact_naming_grammar(filename: str, run_slug: str):
    """artifact naming grammar WWL-<spine>-P<N><sub>-<slug> / EAO-<run>-P<N>-<lane>-<slug> enforced."""
    wwl_pattern = re.compile(r"^WWL-[A-Za-z0-9]+-P[0-9]{2}[a-z]?-[A-Za-z0-9\-]+\.md$")
    eao_pattern = re.compile(rf"^EAO-{run_slug}-P[0-9]{2}[a-z]?-[A-Za-z0-9\-]+-[A-Za-z0-9\-]+\.md$")
    if not (wwl_pattern.match(filename) or eao_pattern.match(filename)):
        raise WWLLawViolation(f"Naming Grammar Violation: {filename} does not match WWL/EAO artifact grammar.")

def enforce_gate_line_byte_exact(gate_line: str):
    """gate line byte-exact; TOKENIZED_BNP is the last block; nothing after END_WWL."""
    if not gate_line.endswith("END_WWL"):
        raise WWLLawViolation("Gate Line Violation: Gate line must end exactly with END_WWL, nothing after.")
    if "TOKENIZED_BNP" not in gate_line: # simplified check
        raise WWLLawViolation("Gate Line Violation: TOKENIZED_BNP block missing from gate line.")

def enforce_token_counts_not_estimated(count_source: str):
    """token counts are agent-reported or UNKNOWN -- never estimated."""
    if count_source not in ["AGENT_REPORTED", "UNKNOWN"]:
        raise WWLLawViolation(f"Token Count Violation: Source '{count_source}' is invalid. Must be AGENT_REPORTED or UNKNOWN.")
