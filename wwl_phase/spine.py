"""BIBLE and BUILD phase table. Jobs match Work Work Loop v1.1.0."""

KERNEL_PATH = r"C:\dev\wwl\docs\WORK_WORK_LOOP_DRAFT_V1.txt"
HARNESS_PATH = r"C:\dev\wwl\engine\hybrid_gate_harness.py"

# phase -> (name, slug, one-line job)
BIBLE = {
    1: ("IDEA", "system-summary", "Verbose summary of the system as specified."),
    2: ("BREAK_OLD", "break-old", "Where the best old solution dies in the real world."),
    3: ("BREAK_NEW", "break-new", "Hostile audit of this idea at its best."),
    4: ("RESEARCH_HUNT", "precedent-hunt", "External and supplied-source hunt."),
    5: ("SHOULDER_ANGELS", "shoulder-angels", "Safe versus bold, forecast, lock one path."),
    6: ("BRAINSTORM", "brainstorm", "Multiple approaches under the locked path."),
    7: ("DESIGN", "design", "Interface and architecture blueprint."),
    8: ("IMPROVE", "improve", "Tighten the design against the break and angel locks."),
    9: ("PLAN", "plan", "Ordered build plan, dependencies, and risks."),
    10: ("SHOULDER_ANGELS", "shoulder-angels", "Second fork on the plan, not the idea."),
    11: ("HUNDRED_GUARANTEE", "hundred-guarantee", "Proof checklist: what exists, how verified, rollback."),
    12: ("SPEC", "spec", "Implementation-ready spec."),
    13: ("BUILD", "prototype-build", "Plan-level build. Not a whole-product dump."),
    14: ("TEST", "test", "Test plan and cases."),
    15: ("BUG_HUNT", "bug-hunt", "Hunt against the spec."),
    16: ("BREAK", "break", "Hostile break of the planned system."),
    17: ("OPTIMIZE", "optimize", "Cost, latency, context, and complexity."),
    18: ("ALPHA", "alpha", "Smallest shippable definition."),
    19: ("BETA", "beta", "Hardening definition."),
    20: ("PRODUCTION_V1", "production-v1", "Locked bible. Stop. Do not return to phase 01."),
}

BUILD = {
    21: ("INVENTORY", "inventory", "Map the bible onto existing files. Gaps only."),
    22: ("ENGINE", "engine", "Runtime and core deltas."),
    23: ("INTERFACE", "interface", "HUD, UX, and API surface."),
    24: ("SURFACES", "surfaces", "Each user-facing surface."),
    25: ("TESTS", "tests", "Executable tests."),
    26: ("VERIFY", "verify", "Build, live, or replay verify."),
    27: ("BUG_HUNT_LIVE", "bug-hunt-live", "Hunt against running constraints."),
    28: ("BREAK_HOSTILE", "break-hostile", "Try to break the patch."),
    29: ("OPTIMIZE", "optimize", "Measurable cost, latency, and complexity."),
    30: ("PRODUCTION_PATCH", "production-patch", "Unified diff, file list, and rollback."),
}

PHASES = {}
PHASES.update(BIBLE)
PHASES.update(BUILD)

AXES = (
    "S1_intent",
    "S2_scope",
    "S3_evidence",
    "S4_completeness",
    "S5_fit",
    "S6_next",
)


def spine_for(phase):
    if 1 <= phase <= 20:
        return "BIBLE"
    if 21 <= phase <= 30:
        return "BUILD"
    return ""


def of_for(phase):
    if phase <= 20:
        return 20
    return 30


def artifact_name(spine, phase, slug, sub=""):
    return "WWL-{0}-P{1:02d}{2}-{3}.md".format(spine, phase, sub or "", slug)
