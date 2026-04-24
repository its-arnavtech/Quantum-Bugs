# Static Dataset Schema

This folder contains static QRated datasets that connect real quantum bug classes with artificial quantum mutation operators.

## qrated_static_bug_dataset.csv

Each row represents a normalized quantum bug class.

### Columns

- `static_bug_id`: Unique ID for the static bug dataset row.
- `bug_class_id`: Normalized bug class ID from `data/bug_classes.csv`.
- `bug_class_name`: Human-readable name of the bug class.
- `category`: High-level category such as gate-level, measurement-level, parameter-level, or compiler/platform-level.
- `description`: Short explanation of the bug class.
- `real_bug_source`: Dataset or study where this class appears.
- `real_bug_repository`: GitHub repository or source artifact connected to the real bug class.
- `mutation_supported`: Whether the class is supported by mutation tools.
- `support_level`: Direct, Partial, or Unsupported.
- `qrate`: Score from 1 to 5 showing quantum-specific usefulness.
- `quantum_specificity`: High, Medium, or Low estimate of how quantum-specific the bug class is.
- `expected_effect`: Expected behavioral impact of the bug.
- `static_detectable`: Whether static analysis may detect the bug.
- `dynamic_detectable`: Whether tests or execution may detect the bug.
- `research_notes`: Why the bug class matters.

## qrated_mutation_dataset.csv

Each row maps a static bug class to one mutation operator.

### Columns

- `mutation_dataset_id`: Unique ID for the mutation mapping row.
- `static_bug_id`: Linked static bug ID.
- `bug_class_id`: Linked normalized bug class ID.
- `bug_class_name`: Human-readable bug class.
- `mutation_tool`: Tool that supports the mutation.
- `operator_id`: Mutation operator ID.
- `operator_name`: Human-readable mutation operator name.
- `mutation_type`: Gate-level, measurement-level, parameter-level, or classical-level.
- `mutation_description`: What the mutation operator does.
- `qrate`: QRate score inherited from the bug class.
- `support_level`: Direct or Partial support.
- `example_mutation_effect`: Expected effect of applying the mutation.

## unsupported_real_bug_classes.csv

Each row represents a real quantum bug class that is not directly supported by current quantum mutation tools.

### Columns

- `unsupported_id`: Unique ID for the unsupported bug row.
- `bug_class_id`: Linked normalized bug class ID.
- `bug_class_name`: Human-readable bug class.
- `real_bug_source`: Dataset or study where the unsupported bug appears.
- `why_unsupported`: Explanation of why current tools do not support it directly.
- `research_opportunity`: Why this gap matters for future work.
- `suggested_future_mutation_operator`: Proposed new mutation operator.
- `qrate`: QRate score showing importance.

## QRate Scale

| QRate | Meaning |
|---|---|
| 5 | Strongly quantum-specific and directly useful for quantum mutation testing |
| 4 | Strongly quantum-specific but only partially supported or unsupported |
| 3 | Relevant to quantum software but partly classical/general |
| 2 | Mostly classical infrastructure or configuration issue |
| 1 | Weak relevance to quantum correctness testing |
