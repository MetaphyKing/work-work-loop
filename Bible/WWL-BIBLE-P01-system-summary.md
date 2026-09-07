# Operational Blueprint: Work Work Loop (WWL) v1.0.0 System Summary
**System Status:** Production v1
**Document Type:** Project Manifesto / Concept Document (summary)
**Artifact Name:** WWL-BIBLE-P01-system-summary

---

## 1. Executive Overview & Core Philosophy
The **Work Work Loop (WWL)** is a high-fidelity operating kernel designed to govern the execution of complex creative and technical tasks by artificial intelligence agents with idempotent precision [42, 100]. In standard AI agent workflows, task failure typically manifests as "AI chaos": the agent attempts to execute a complex multi-step request in a single unstructured, breathless step, merging planning and building, and hallucinating unfinished or fake "whole product" scripts [1, 4, 59]. 

The WWL serves as an aggressive, structured antidote to this chaos [2, 58]. It enforces a rigid separation of concerns and a strict "Work then Deliver" mandate [8, 43]. By isolating the core loop of execution from the pluggable task plan and the instance-specific details of a project, the system ensures that regardless of cognitive load or task complexity, agent reliability and output quality remain absolutely constant [42, 43].

---

## 2. The Conceptual Architecture (The Four Layers)
To prevent the common failure mode of jamming all standing rules, initial prompts, and planning specifications into a single chaotic context "soup," the WWL decouples the system into four independent layers [4, 6, 60, 102]:

1. **The Kernel (The Loop):** The immutable, always-running procedural wrapper. It defines the unyielding phase cycle of **Work → Deliver → Artifact → Gate** [7, 43, 100].
2. **The Spine (The Pluggable Task Plan):** The specific structural roadmap the agent runs on. The system primarily utilizes two pluggable spines: the **BIBLE Spine** (Phases 01–20) for strategic thinking and planning, and the **BUILD Spine** (Phases 21–30) for incremental technical implementation [6, 21, 65].
3. **The Locks (The Instance Constraints):** Project-specific, non-negotiable variables that belong strictly to the unique build (e.g., exact library versions, UI hex colors, API restrictions). These never pollute the general rules of the Kernel [6, 110, 111].
4. **The Harness (The Environment Adapter):** The operational layer where the WWL interfaces with a particular client or platform, modifying how deliveries and artifacts are materialized without altering the core kernel laws [34, 102].

---

## 3. The Ten Laws of Execution
The Ten Laws (L1–L10) are the non-negotiable operational constraints that govern the loop, establishing process integrity, output quality, and system authority under all conditions [44, 102]:

* **L1: One Phase at a Time (Sequence Gating):** No phase transitions or silent jumps are allowed until an explicit `CONTINUE` command is received from the user [12, 44].
* **L2: Work then Deliver (Isolation):** Reasoning and execution must be performed privately ("in the kitchen") before the user-visible plate is presented in chat ("the dining room") to prevent raw, half-formed thoughts from polluting the output [8, 9, 45].
* **L3: Dual Output (Auditability):** Every single phase must yield both a conversational chat delivery and one durable, complete artifact. If either is missing, the phase is incomplete [45, 62].
* **L4: Scoring Mandate (The Quality Bar):** Every inbound prompt and outbound delivery must be scored. If the quality score falls below 99/100, the system must self-correct privately until the threshold is met [16, 46].
* **L5: Context Management (Recursive Splitting):** When context boundaries are approached, a phase must be split into subphases (e.g., Na, Nb, Nc). Each subphase is a full, recursive cycle with its own artifact and Best Next Prompt (BNP) to prevent data loss [15, 45].
* **L6: Evidence Over Claims (Veracity):** Every claim must be strictly grounded in supplied sources or the live system. Unsupported or inferred claims must be explicitly marked as `UNGROUNDED` in all caps and cannot be treated as complete [13, 46].
* **L7: Exhaustion is Not Success (Accuracy):** Halting because of memory limits or a full context window is classified as a "SPLIT," never a completion [14, 46].
* **L8: Human Mid-Loop Authority (Control):** The human's `STOP` signal freezes the loop, while `CONTINUE` advances it. No simulated bypasses or automated jumps past human authority are allowed [8, 45].
* **L9: Linear Progression (Efficiency):** Once Spine I (BIBLE) is locked at Phase 20 (Production v1), BIBLE planning phases cannot be replayed. The agent must proceed to Spine II (BUILD) or UNLOAD [24, 47, 102].
* **L10: Intent Preservation (Alignment):** Iterative improvements must target wording, completeness, and rigor, but must never alter or compromise the user's original goal [10, 46].

---

## 4. The Six-Point Scoring Engine (S1–S6)
The Quality Gate requires that every phase's output pass a flawless 99-point threshold across six criteria before being delivered [16, 49]:

1. **S1 INTENT:** Restates the user's goal in exactly one sentence without modifying the target product [49, 103].
2. **S2 SCOPE:** Limits focus strictly to the current phase only, actively blocking silent jumps ahead [49, 103].
3. **S3 EVIDENCE:** Provides grounded citations, file paths, IDs, or mandatory `UNGROUNDED` tags [49, 103].
4. **S4 COMPLETE:** Verifies that all mandatory components—Work, Deliver, Artifact, Best Next Prompt, and Gate Line—are present [49, 103].
5. **S5 FIT:** Confirms that the output fits within the current context limits without truncation [49, 103].
6. **S6 NEXT:** Formulates a paste-ready Best Next Prompt (BNP) that guarantees safe, structured re-entry into the loop [49, 103].

*If any criterion falls short, the Fail Path Protocol is triggered: the agent rewrites the output, lists the changes, rescores, and delivers only when >= 99 is achieved [50, 104].*

---

## 5. The Pluggable Spines and Their Phases

### Spine I: The BIBLE (Thinking & Planning) [51, 104]
A 20-phase strategic engine designed to audit, deconstruct, and architect an idea before a single line of production code is written [51, 66]:
* **01 IDEA:** Verbose summary of the system and conceptualization [51].
* **02 BREAK_OLD:** Deconstruction of existing solutions to find real-world failure points [51, 92].
* **03 BREAK_NEW:** Hostile internal audit of the new idea operating at its best [51, 93].
* **04 RESEARCH_HUNT:** Information gathering from external and supplied sources [51, 93].
* **05 SHOULDER_ANGELS (Mandatory Fork):** Evaluates a safe strategy vs. a bold strategy, forecasts outcomes, and locks one definitive path [27, 51, 93].
* **06 BRAINSTORM:** Develops multiple approaches strictly under the locked path of Phase 05 [51, 93].
* **07 DESIGN:** Establishes the architectural and structural blueprint of the solution [51, 93].
* **08 IMPROVE:** Tightens design against the failures identified in 02, 03, and 05 [51, 93].
* **09 PLAN:** Step-by-step ordered build plan, identifying dependencies and risks [51, 94].
* **10 SHOULDER_ANGELS (Plan Fork):** A second strategic fork applied directly to the build plan rather than the idea [51, 94].
* **11 HUNDRED_GUARANTEE (Mandatory Gate):** Checklist verifying what exists, how it is verified, and rollback procedures [24, 51, 94].
* **12 SPEC:** Final implementation-ready technical specifications serving as the project's ground truth [51, 94].
* **13 BUILD:** Initial coding/creation of the core assets or BIBLE-spine prototype [51, 94].
* **14 TEST:** Establishes functional test plans and cases [51, 95].
* **15 BUG_HUNT:** Audits current work and hunts for bugs against the Phase 12 specification [51, 95].
* **16 BREAK:** Hostile stress-testing to find failure modes in the planned architecture [51, 95].
* **17 OPTIMIZE:** Measures performance constraints including cost, latency, context, and complexity [51, 95].
* **18 ALPHA:** Defines the Minimum Viable Product (MVP) scope [51, 96].
* **19 BETA:** Documents scale and hardening requirements [51, 96].
* **20 PRODUCTION_V1 (Terminal planning gate):** Locks the BIBLE. No loopbacks to 01 are allowed [24, 51, 96].

### Spine II: The BUILD (Technical Execution) [53, 105]
Begins only after Phase 20 is complete, focusing entirely on incremental, disciplined implementation [52, 66]:
* **21 INVENTORY:** Maps BIBLE specs to existing files; identifies gaps only. **No new stack allowed** [25, 53, 96].
* **22 ENGINE:** Develops core runtime and logic deltas [53, 96].
* **23 INTERFACE:** Builds HUD, UX, or API surface areas as defined in DESIGN [53, 97].
* **24 SURFACES:** Detailed development of user-facing UI/UX components [53, 97].
* **25 TESTS:** Creation of executable tests [53, 97].
* **26 VERIFY:** Live, simulated, or replay verification of the build [53, 97].
* **27 BUG_HUNT_LIVE:** Real-time bug detection in the active running environment [53, 97].
* **28 BREAK_HOSTILE:** Attempt to break the implementation patch [53, 97].
* **29 OPTIMIZE:** Measurable performance and code optimization [53, 97].
* **30 PRODUCTION_PATCH:** Final delivery. Produces a unified diff, file list, and rollback plan [53, 98].

---

## 6. The Six-Step Phase Lifecycle (The Heartbeat)
Each individual phase $N$ of a spine must execute through the following six steps to guarantee process compliance and auditability [64, 106]:
1. **Restate Intent:** Present a one-line summary of the phase goal.
2. **Work (Private):** Perform internal reasoning, information gathering, and scoring.
3. **Deliver (Chat):** Present the user-visible conversational output for this phase only.
4. **Artifact:** Output a single, durable file named `WWL-<spine>-P<N><sub>-<slug>` (e.g., `WWL-BIBLE-P01-system-summary.md`). *Never a fake, truncated "whole product" script* [31, 106].
5. **Gate Line:** Output the exact gating string: `"Phase N of Y. Prompt continue to proceed to the next phase."` [106]
6. **Best Next Prompt (BNP):** Render a fenced, paste-ready block containing the next phase, locked decisions, and the proceed command to enable seamless loop re-entry [32, 106].

---

## 7. Supported Harnesses & Integration
The WWL kernel easily adapts to various target execution environments [34, 109]:
* **Gemini Notebook:** Chat serves as Delivery; the Studio panel serves as the permanent home for Artifacts. The user advances the loop by typing `continue` or pasting the BNP [34, 109].
* **Grail CLI:** The "missing list" of files between the BIBLE and the current repository defines the exclusive scope of work. The system never reads past a `STOP` command [35, 109].
* **IFCH:** Automates loop re-entry via self-tokenized `@mention` hooks of the BNP [36, 109].
* **Generic Agent:** Kernel + START is used, with artifacts written directly as files into the local repository [34, 109].
