# Methodology

This project builds a taxonomy of quantum software bug classes by comparing artificial mutation operators with real-world quantum bug datasets.

## Step 1: Identify Quantum Mutation Testing Tools

The first step was to identify tools that generate quantum program mutants. The tools included in this repository are:

* Muskit
* QMutPy
* QCRMut
* QuanForge
* QMutBench

For each tool, the supported mutation operators were extracted and normalized into common bug classes.

## Step 2: Identify Real Quantum Bug Datasets

The second step was to identify real bug repositories, benchmarks, and empirical studies involving quantum software bugs. The real bug sources included:

* Bugs4Q
* Qiskit bug-pattern research
* Empirical quantum platform bug study
* QMutBench as a mutation benchmark

## Step 3: Normalize Bug Classes

Mutation operators and real bug labels often use different terminology. For example:

* Gate deletion, remove gate, and random gate deletion were normalized as Missing gate.
* Gate insertion and random gate addition were normalized as Extra gate.
* Gate replacement and gate name modification were normalized as Wrong gate.

This normalization allows mutation-supported bugs and real bugs to be compared directly.

## Step 4: Create a Crosswalk

Each bug class was mapped to:

* Real bug datasets where the bug class appears
* Mutation tools that can generate the bug
* Support level: Direct, Partial, or Unsupported

## Step 5: Assign QRate Scores

Each bug class was assigned a QRate score from 1 to 5.

The score estimates how useful and quantum-specific the bug class is for quantum mutation testing research.

A high QRate means the bug class is highly relevant to quantum correctness and is either directly supported by mutation tools or represents an important gap in existing tools.
