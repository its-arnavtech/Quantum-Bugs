# Taxonomy Notes

## Main Observation

Existing quantum mutation tools are strongest at generating gate-level bugs. These include missing gates, extra gates, and wrong gates.

Newer tools such as QCRMut and QuanForge expand support to target-qubit bugs, gate-position bugs, and parameter bugs.

## Measurement Bugs

Measurement bugs are especially important because measurement changes quantum state through collapse. QMutPy directly supports measurement deletion and measurement insertion.

However, repeated measurement and incorrect operations after measurement are not fully covered by current mutation tools.

## Parameterized Circuit Bugs

Parameterized circuit and QNN bugs are best represented by QuanForge. Its parameter mutation operators cover fuzzing, sign flips, and parameter switches.

These are especially useful for testing quantum neural networks and variational quantum algorithms.

## Real Bug Gaps

Real quantum bug datasets include several bug classes that are not well covered by mutation tools:

* MSB/LSB convention mismatch
* Classical and quantum register mismatch
* Unsafe uncomputation
* Incorrect intermediate representation
* Backend and simulator compatibility bugs
* Incorrect scheduling

These unsupported classes represent good future research opportunities.
