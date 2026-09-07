# WWL gating harness

Stdlib-only two-pass gate for Work Work Loop artifacts.

- Pass 1: sequence, density, anti-placeholder scan  
- Pass 1.5: `py_compile` when a Python file is supplied  
- Pass 2: weighted qualitative score must be ≥ 99  

Workspace root is `$WWL_ROOT` or `./.wwl` (created on first run). Paths outside that root are rejected.

```bash
python hybrid_gate_harness.py --help
python -m unittest test_hybrid_gate_harness test_hostile_break
```

Run the unittest commands from this directory, or from the repo root as `python -m unittest engine.test_hybrid_gate_harness engine.test_hostile_break`.
