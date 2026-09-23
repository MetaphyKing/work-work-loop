"""Map hybrid-harness stdout and stderr onto the structured error contract."""

from wwl_phase.result import fail, ok


def classify(exit_code, output, dry_run=False):
    text = output or ""
    lowered = text.lower()
    if exit_code == 0:
        action = "dry_run" if dry_run else "publish"
        return ok(action=action, exit_code=0)

    error = " ".join(text.split())
    if len(error) > 500:
        error = error[:500]

    if "security violation" in lowered:
        return fail(error or "path outside WWL_ROOT", False, action="stop", exit_code=exit_code)
    if "phase sequence jump" in lowered:
        return fail(error or "phase sequence jump", False, action="stop", exit_code=exit_code)
    if "loop-breaker" in lowered:
        return fail(error or "loop-breaker", False, action="split", exit_code=exit_code)
    if "malformed qualitative" in lowered:
        return fail(error or "malformed scores", True, action="rewrite", exit_code=exit_code)
    if "lazy placeholder" in lowered:
        return fail(error or "lazy placeholder", True, action="rewrite", exit_code=exit_code)
    if "minimum content density" in lowered or "draft file not found" in lowered:
        return fail(error or "draft rejected", True, action="rewrite", exit_code=exit_code)
    if "syntax compile failure" in lowered or "preflight target file" in lowered:
        return fail(error or "syntax failure", True, action="rewrite", exit_code=exit_code)
    if "under acceptable gating threshold" in lowered:
        return fail(error or "score under 99", True, action="rewrite", exit_code=exit_code)
    if "failed atomic publication" in lowered or "failed engine initialization" in lowered:
        return fail(error or "publication failed", True, action="publish", exit_code=exit_code)
    if "unexpected" in lowered:
        return fail(error or "unexpected harness failure", True, action="rewrite", exit_code=exit_code)
    return fail(error or "harness failed", False, action="stop", exit_code=exit_code)
