# WWL-BIBLE-P10-shoulder-angels: Plan-Level Strategy Fork

This document outlines and resolves the second mandatory strategy fork (ShoulderAngels) for the **Work Work Loop (WWL) Operating Kernel**, focusing on the technical design of the build-plan execution engine.

---

## 1. Intent & Scope
The goal of this phase is to evaluate and lock the architectural approach for the physical execution harness (`hybrid_gate_harness.py`). We compare a **Rigid, Zero-Dependency Native Script** (enforcing absolute stability) against an **Extensible, Plugin-Based Engine** (enforcing modularity and dynamic configuration) before defining the proof and rollback contracts in Phase 11.

---

## 2. Strategy A: Safe Strategy (Zero-Dependency Native Script)
The Safe Strategy implements all validation, gating, scoring, and file-movement operations within a single, highly structured Python utility engine containing zero external runtime dependencies. 

### Core Attributes
- **Zero Imports:** Relies strictly on Python standard libraries (`json`, `sys`, `os`, `shutil`, `re`, `datetime`).
- **Monolithic Gating:** Enforces S1–S6 and Pass 1–2 validations through sequential, hard-coded execution blocks inside `hybrid_gate_harness.py`.
- **Pre-compiled Checks:** Uses local regex and syntax parsers to validate files before triggering model checks.

### Outcomes & Forecasts
- **Reliability:** 99.9% runtime stability. Absolutely zero risk of dynamic import failures or environment mismatch, particularly inside strict or offline sandbox environments.
- **Maintainability:** Moderate. The code is easy to audit and self-repair, but adapting it to non-standard environments requires modifying the core runner script itself.

---

## 3. Strategy B: Bold Strategy (Extensible Plugin-Based Hook Engine)
The Bold Strategy designs the harness as an event-driven orchestrator that loads external modules and custom plugins dynamically based on config files, acting like a lightweight local CI/CD engine (e.g., utilizing dynamic python imports or custom shell-based pre-commit hooks).

### Core Attributes
- **Dynamic Module Loading:** Programmatically inspects a plugin directory (`/plugins/`) and imports python classes on the fly.
- **Event-Driven Hook Hooks:** Allows third-party scripts to register custom pre-flight or post-publish events (e.g., Git auto-commits, Slack notifications, specialized code linters).
- **Extensible Schema:** Custom gate criteria can be registered and weighed programmatically without modifying the core kernel loop.

### Outcomes & Forecasts
- **Reliability:** 75% runtime stability. Dynamic loading introduces high failure risks in air-gapped systems due to missing python packages, path resolution bugs, and brittle module namespaces.
- **Adaptability:** Exceptional. Allows developers to plug the harness into any platform (Github Actions, local bash pipelines, VSCode extensions) seamlessly.

---

## 4. Outcome Forecasts & Risk Matrix

| Evaluation Dimension | Strategy A: Safe (Native Script) | Strategy B: Bold (Plugin Hook) | Selected Path Mitigation |
| :--- | :--- | :--- | :--- |
| **Sandbox Execution** | **Optimal** (No dynamic path breaks) | **Fragile** (Potential import errors) | Safe Path guarantees sandboxed runs |
| **Failure Diagnostics** | **Trivial** (Flat stack traces) | **Complex** (Dynamic module exceptions) | Safe Path keeps self-healing robust |
| **Extensibility** | **Low** (Hardcoded pipeline blocks) | **High** (Modular registries) | Mitigated by Config Map (Section 5) |
| **Execution Latency** | **Extremely Low** (<100ms startup) | **Moderate** (Plugin scanning overhead) | Low latency maintains user velocity |

---

## 5. The Locked Path: Zero-Dependency Native Script with Config Map
To guarantee absolute process integrity and prevent AI execution chaos under air-gapped sandbox constraints, we **definitively lock Strategy A (Zero-Dependency Native Script)**. 

### Customizability Mitigation: The Structured Configuration Map (`wwl_config.json`)
To resolve the rigidity limitations of the native script, we decouple pipeline parameters from the codebase using a static local JSON map. The harness remains zero-dependency but adapts its execution paths dynamically based on this map:

```json
{
  "project_name": "wwl_operating_kernel",
  "pipeline": {
    "syntax_check_languages": ["python", "json", "markdown"],
    "ignored_paths": ["/workspace/scratch/tmp/*"],
    "required_artifact_patterns": ["WWL-BIBLE-P[0-9]{2}-[a-z-]+\\.md"]
  },
  "peer_critic": {
    "temperature": 0.0,
    "metrics": {
      "S1_INTENT": { "weight": 0.20, "min_score": 100 },
      "S3_EVIDENCE": { "weight": 0.25, "min_score": 100 }
    }
  }
}
```

This configuration layout allows the operator to adapt the validation engine to different file layouts and requirements without editing the core `hybrid_gate_harness.py` logic, achieving the adaptability of a plugin architecture with the absolute determinism of a flat script.
