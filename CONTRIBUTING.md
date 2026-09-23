# Contributing

Work Work Loop is the kernel in `docs/` plus the phase tools that keep one phase honest. Issues and pull requests are welcome. The license is Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).

## Tests

From a clone of this repository:

```bash
python -m unittest discover -s tests -t .
```

Gate tests call `engine/hybrid_gate_harness.py`. They skip when that harness does not start on the current interpreter.

## Leave these alone

`Bible/`, `build/`, `core/` and `notebook_sources/` are gated records and the notebook corpus. A tooling change does not rewrite them.

Keep the title images the README already shows:

- `assets/wwl-hero-q68.webp`
- `assets/wwl-hero.jpg`

`assets/wwl-social.jpg` is the 1280 by 640 social still made from the hero. Do not delete the hero files in order to replace that picture.

## Paths

Commands assume the clone root is the working directory.

- Kernel: `docs/WORK_WORK_LOOP_DRAFT_V1.txt`
- Harness: `engine/hybrid_gate_harness.py`

`WWL_KERNEL_PATH` and `WWL_HARNESS_PATH` override those two files for a local checkout. `WWL_PACKAGE_ROOT` is only for a seat whose shell is not already in the clone.
