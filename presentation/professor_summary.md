# Professor Summary

## Project Title

QRated Quantum Bug Dataset: Mapping Real Quantum Bugs to Mutation Operators

## Goal

The goal of this project is to build a static research dataset that connects real quantum software bug classes with artificial quantum mutation operators.

## What Was Collected

This project collects:

* Quantum mutation testing tools
* Mutation operators supported by each tool
* Real quantum bug datasets and empirical studies
* Bug classes found in real quantum software
* A mapping between real bug classes and mutation-supported bug classes
* QRate scores for each bug class

## Main Mutation Tools Studied

* Muskit
* QMutPy
* QCRMut
* QuanForge
* QMutBench

## Main Real Bug Sources Studied

* Bugs4Q
* Qiskit bug-pattern research
* Empirical study of real-world quantum software bugs

## Key Finding

Existing quantum mutation tools strongly support gate-level bugs, measurement bugs, and parameter bugs.

However, real quantum bug datasets contain additional classes that are not well supported by current mutation tools, including:

* MSB/LSB convention mismatch
* Classical and quantum register mismatch
* Unsafe uncomputation
* Incorrect intermediate representation
* Incorrect scheduling
* Backend and simulator compatibility bugs

## Research Value

This dataset helps identify the gap between artificial quantum mutants and real quantum software bugs.

The dataset can be used to:

* Compare mutation testing tools
* Design new mutation operators
* Build stronger quantum testing benchmarks
* Evaluate how realistic artificial quantum bugs are
