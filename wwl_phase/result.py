"""Shared success and error objects for every phase boundary."""


def fail(error, retryable, action="stop", **extra):
    out = {
        "success": False,
        "error": error,
        "retryable": bool(retryable),
        "action": action,
    }
    out.update(extra)
    return out


def ok(**extra):
    out = {"success": True, "error": "", "retryable": False}
    out.update(extra)
    return out
