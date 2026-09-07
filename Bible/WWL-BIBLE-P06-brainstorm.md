# WWL Operating Kernel Specification: Phase 06 BRAINSTORM
**Status:** Approved Draft  
**Locked Decision Context:** Strategy A (The Safe Path: Local Deterministic Gating + Hybrid Qualitative Hooks)  

---

## 1. Intent & Scope
This artifact details the brainstorming and evaluation of three distinct technical approaches to implement the deterministic programmatic validation engine and its hybrid qualitative gating hook for the Work Work Loop (WWL) operating kernel. All approaches are constrained by the Strategy A decision locked in Phase 05.

---

## 2. Approach 1: Plain-Text JSON-Schema Interceptor (`wwl_validator.py`)
This approach implements a deterministic Python validation script that parses a physical state file (`wwl_state.json`) and the generated markdown assets prior to delivery.

### System Architecture
```
[Private WORK Phase] ──> writes draft md/json ──> [wwl_validator.py]
                                                          │
          ┌───────────────────────────────────────────────┴──────────────┐
          ▼ (PASS)                                                       ▼ (FAIL)
[Publish to /workspace/out/]                                     [Halt & Self-Correct]
```

### Key Validation Routines
1. **Schema Check:** Validates that `wwl_state.json` contains exact fields: `version`, `spine`, `phase`, `locks`, and `bnp_fenced`.
2. **Sequential Phase Enforcement (L1):** Reads the last recorded phase on disk and verifies that the new phase is exactly $N+1$.
3. **Artifact Size & Integrity Check (L3):** Checks that the artifact named `WWL-<spine>-P<N>-<slug>` exists in `/workspace/scratch/` and has a file size $> 100$ bytes.
4. **Anti-Placeholder Scanner:** Runs string searches for suspicious comments (e.g., `# TODO`, `// insert code here`, `...`, `[rest of code]`) to block fake whole-product scripts.

### Pros & Cons
*   **Pros:** Zero token overhead; execution halts in milliseconds; 100% deterministic.
*   **Cons:** Highly vulnerable to manual syntax changes; a single missing comma in a state file triggers execution deadlock.

---

## 3. Approach 2: Directory State Hash Engine (`dir_hash_monitor.py`)
This approach monitors physical disk changes across the `/workspace/scratch/` and `/workspace/out/` directories, creating hash trees to track state modifications.

### System Architecture
```
[Turn Begins] ──> takes Dir Hash Map ──> [WORK / DELIVER] ──> takes New Hash Map
                                                                      │
        ┌─────────────────────────────────────────────────────────────┴────────┐
        ▼ (Single New Artifact & Verified Path)                                ▼ (Violation)
  [Validate State]                                                     [Trigger Rollback]
```

### Key Validation Routines
1. **Durable File Hash Matching:** Evaluates folder hashes to ensure only a single file matching the pattern `/workspace/out/WWL-<spine>-P<N>-<slug>.<ext>` has been added.
2. **Directory Isolation Enforcement:** Instantly raises a violation if any baseline code files outside the scoped "missing list" have been modified (enforcing Grail-style precision and the "No New Stack" rule of BUILD).
3. **Binary Asset Integrity:** Generates checksum verifications for compiled PDFs, Word files, or image layouts to ensure they are static and structurally uncorrupted.

### Pros & Cons
*   **Pros:** Format-agnostic (works for images, PDFs, binary files); provides bulletproof protection against accidental code corruption or stack pollution.
*   **Cons:** Incapable of validating qualitative or semantic criteria (e.g., whether S1 Intent is correctly restated or if S3 citations are mathematically accurate).

---

## 4. Approach 3: Two-Pass Peer Gating Harness (`hybrid_gate_harness.py`)
This approach implements the true Hybrid Gating Hook proposed in Phase 05 by combining a deterministic local validator script with a lightweight qualitative second-pass.

### System Architecture
```
[Private WORK Output]
         │
         ▼
 1. DETERMINISTIC CHECKS  ──(Pass)──>  2. SEMANTIC AUDITOR  ──(Score >= 99)──> [Publish]
 (wwl_validator.py)                   (peer_eval_agent)
         │                                    │
       (Fail)                               (Fail)
         │                                    │
         └─────────> [Self-Correct Engine] <──┘
```

### Key Validation Routines
1. **Pass 1: Programmatic Validation (Deterministic):**
    * Runs structural validation (correct naming conventions, correct BNP template presence).
2. **Pass 2: Peer Semantic Auditor (Qualitative):**
    * Spasms a separate internal prompt block acting as a strict, independent auditor.
    * Scores S1 (Intent restatement), S3 (Evidence / Citation validity), and L10 (Original goal preservation) from 0 to 100.
3. **Automated Gating:**
    * If programmatic checks succeed AND the semantic auditor returns $\ge 99$ on all counts, the file is automatically published to `/workspace/out/`.
    * If any gate fails, the precise traceback is logged to `/workspace/scratch/gate_failures.log` and fed back to the working instance for private self-correction.

### Pros & Cons
*   **Pros:** The most complete representation of the WWL's 99-point scoring engine; eliminates both structural mistakes and LLM self-grading collusion.
*   **Cons:** Slower performance; introduces a minor token overhead due to the double-pass inference call.

---

## 5. Comparative Evaluation Matrix

| Metric / Dimension | Approach 1: JSON Schema | Approach 2: Directory Hash | Approach 3: Two-Pass Hybrid |
| :--- | :--- | :--- | :--- |
| **Deterministic Reliability** | High (100%) | Exceptional (100%) | Moderate-High (90% programmatic, 10% LLM) |
| **Prevention of Collusion** | High (Hard Parser) | High (Disk-Locked) | Absolute (Decoupled Peer Auditor) |
| **Semantic Intelligence** | Low (None) | Low (None) | Exceptional (Understands context/intent) |
| **Implementation Complexity**| Low | Moderate | Moderate-High |
| **Token Cost Overhead** | Zero | Zero | Minimal (Second pass query) |
| **Recovery Path Handling** | Outputs hard exit code | Outputs hard rollback | Generates structured error log |

---

## 6. Synthesis and Selected Direction
We select **Approach 3: Two-Pass Peer Gating Harness** as our implementation target. It is the only architecture that fully satisfies the **Hybrid Gating Hook** specified in Phase 05 without compromising either structural compliance or contextual alignment. 

To mitigate complexity and performance bottlenecks:
1.  **Fail-Fast Circuit:** The deterministic programmatic checks run first. If programmatic checks fail, the system exits immediately without running the semantic pass, saving token cost.
2.  **Stateless Execution:** The peer agent reads only the current phase draft and the original user intent, keeping its context window tiny and execution speed optimal.
