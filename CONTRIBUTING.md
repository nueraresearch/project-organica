# Contributing to Project Organica

Thank you for your interest in contributing to **Project Organica**. 

Project Organica is an open-source developmental machine intelligence research project. We value reproducible empirical experiments, mathematical rigor, and architectural discipline.

---

## The Golden Rule: Respect the Design Laws

Before submitting an issue or pull request, review [`docs/DESIGN_LAWS.md`](docs/DESIGN_LAWS.md). Every PR must adhere to the 6 core architectural laws:
1. **Strict Upward Layer Induction**: No top-down hard-coded abstractions.
2. **100% Structural Lineage**: Every candidate must have verified `parent_ids`.
3. **Cognitive Isolation**: Internal sleep states must never pollute empirical graph edges.
4. **Grounded Dreams**: Dreams propose; reality validates. Dreams never directly alter beliefs.
5. **EIG Attention Economy**: Importance is derived from information gain, not raw confidence.
6. **Natural Selection**: Unreinforced beliefs decay and face extinction.

---

## Development Setup

Project Organica has **zero external package dependencies** beyond Python 3.10+ standard libraries (`pytest` is used for testing).

```bash
git clone https://github.com/nueraresearch/project-organica.git
cd project-organica
python -m pytest tests
```

---

## Running Benchmarks & Reproduction Packs

To verify that your environment or changes maintain developmental compliance:

```bash
# Run the 5-part growth benchmark suite
python benchmarks/benchmark_suite.py

# Run all 4 domain reproduction packs
python examples/domains/01_developer_workflow.py
python examples/domains/02_bug_tracking.py
python examples/domains/03_synthetic_ecology.py
python examples/domains/04_robot_simulation.py
```

---

## Proposing New Domains
We welcome contributions of new real-world trace datasets (e.g., biological sequences, financial transactions, server operations). Ensure your domain script includes explicit verification assertions of emergent structures.
