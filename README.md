# QRated Quantum Bug Dataset

This repository contains a research-oriented taxonomy of quantum computing bug classes, mutation testing tools, and real quantum bug datasets.

The goal of this project is to connect artificial quantum mutations with real bug classes found in quantum software repositories and bug benchmarks. Each bug class is assigned a QRate score that estimates its quantum-specific relevance and usefulness for testing research.

## Project Goal

The main research goal is to build a static dataset of quantum bug classes that are mapped to mutation operators and real bug datasets.

This repository answers three questions:

1. What mutation testing tools exist for quantum computing?
2. What types of bugs do these mutation tools support?
3. How do mutation-supported bugs compare to real bugs found in quantum bug repositories and datasets?

## Included Data

The repository includes:

- Quantum mutation testing tools
- Mutation operators supported by each tool
- Real quantum bug datasets and repositories
- Quantum bug classes
- A crosswalk between artificial mutations and real bugs
- QRated bug classes ranked by quantum-specific usefulness

## Main Tools Studied

- Muskit
- QMutPy
- QCRMut
- QuanForge
- QMutBench

## Main Real Bug Sources Studied

- Bugs4Q
- Qiskit bug-pattern research
- Empirical study of real-world quantum software bugs across quantum platforms

## QRate Scale

| QRate | Meaning |
|---|---|
| 5 | Strongly quantum-specific and directly supported by mutation tools |
| 4 | Strongly quantum-specific but only partially supported by mutation tools |
| 3 | Appears in quantum software but is partly classical/general software |
| 2 | Mostly classical infrastructure bug |
| 1 | Weak relevance to quantum correctness/testing |

## Repository Structure

```text
data/
  mutation_tools.csv
  mutation_operators.csv
  real_bug_datasets.csv
  bug_classes.csv
  mutation_real_bug_crosswalk.csv
  qrated_bug_classes.csv

docs/
  methodology.md
  sources.md
  taxonomy_notes.md

examples/
  example_bug_record.md
  example_mutation_record.md

presentation/
  professor_summary.md
```

## Key Finding

Current quantum mutation testing tools are strong at generating gate-level, measurement-level, and parameter-level bugs. However, they are weaker at representing real-world quantum software bugs involving register mismatch, endianness, intermediate representation errors, backend compatibility, scheduling, and unsafe uncomputation.

This gap suggests an opportunity for future research: expanding quantum mutation operators to better model real quantum software bugs.
