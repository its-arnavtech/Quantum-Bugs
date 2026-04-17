from __future__ import annotations

import csv
import itertools
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from textwrap import dedent
from typing import Iterable


KILLABILITY = {
    "unit": "unit tests",
    "property": "property-based tests",
    "statistical": "statistical output tests",
    "equivalence": "equivalence checks",
}


@dataclass(frozen=True)
class MutationVariant:
    operator_id: str
    category: str
    subtype: str
    description: str
    relevance: str
    expected_effect: str
    difficulty: str
    killable_by: list[str]
    replacement: str
    origin: str
    quantum_specific: bool
    equivalent_candidate: bool = False


@dataclass(frozen=True)
class MutationSite:
    site_id: str
    placeholder: str
    default: str
    variants: list[MutationVariant]


@dataclass(frozen=True)
class SeedProgram:
    seed_id: str
    family: str
    name: str
    description: str
    tags: list[str]
    template: str
    sites: list[MutationSite]


@dataclass
class MutationRecord:
    mutation_id: str
    seed_id: str
    family: str
    order: str
    source_seed_path: str
    mutant_path: str
    mutation_category: str
    mutation_subtype: str
    operator_id: str
    operator_origin: str
    quantum_specific: bool
    equivalent_candidate: bool
    bug_description: str
    testing_relevance: str
    expected_effect: str
    difficulty: str
    likely_killable_by: list[str]
    primary_site: str
    secondary_sites: list[str] = field(default_factory=list)


def taxonomy() -> dict:
    return {
        "A_gate_level_quantum_bugs": {
            "label": "Gate-level quantum bugs",
            "origin": "quantum-specific",
            "subtypes": [
                "single_qubit_gate_replacement",
                "controlled_gate_replacement",
                "gate_deletion",
                "extra_gate_insertion",
                "gate_reordering",
                "wrong_qubit",
                "reversed_control_target",
                "missing_control",
                "inverse_misuse",
                "entanglement_structure_mutation",
            ],
        },
        "B_parameter_bugs": {
            "label": "Parameter bugs",
            "origin": "mixed",
            "subtypes": [
                "wrong_rotation_angle",
                "sign_error",
                "degrees_vs_radians",
                "constant_offset",
                "parameter_scaling",
                "wrong_parameter_variable",
                "binding_order_mismatch",
                "stale_parameter",
            ],
        },
        "C_measurement_bugs": {
            "label": "Measurement and classical-register bugs",
            "origin": "quantum-specific",
            "subtypes": [
                "wrong_measured_qubit",
                "wrong_classical_bit",
                "measurement_omission",
                "premature_measurement",
                "mapping_reorder",
                "endianness_postprocessing_bug",
                "wrong_success_criterion",
            ],
        },
        "D_circuit_structure_bugs": {
            "label": "Circuit structure bugs",
            "origin": "mixed",
            "subtypes": [
                "wrong_number_of_qubits",
                "missing_reset",
                "incorrect_subcircuit_composition",
                "copy_paste_wrong_block",
                "loop_range_bug",
                "off_by_one_qubit_index",
                "wrong_register_reference",
            ],
        },
        "E_algorithm_specific_quantum_bugs": {
            "label": "Algorithm-specific quantum bugs",
            "origin": "quantum-specific",
            "subtypes": [
                "broken_bell_entanglement",
                "teleportation_correction_bug",
                "superdense_encoding_bug",
                "oracle_mutation",
                "diffuser_mutation",
                "qft_angle_bug",
                "qaoa_cost_bug",
                "vqe_expectation_bug",
                "swap_test_control_bug",
            ],
        },
        "F_backend_execution_bugs": {
            "label": "Transpilation/backend/execution bugs",
            "origin": "mixed",
            "subtypes": [
                "wrong_backend",
                "wrong_shot_count",
                "missing_transpile",
                "wrong_optimization_assumption",
                "basis_gate_mismatch",
                "noise_model_misapplied",
                "result_access_bug",
            ],
        },
        "G_hybrid_bugs": {
            "label": "Hybrid classical-quantum bugs",
            "origin": "classical-mutation-inspired",
            "subtypes": [
                "optimizer_direction_bug",
                "objective_sign_flip",
                "convergence_condition_bug",
                "stale_model_outputs",
                "wrong_parameter_update",
                "wrong_loop_bounds",
                "random_seed_bug",
            ],
        },
        "H_api_misuse_bugs": {
            "label": "API misuse bugs",
            "origin": "classical-mutation-inspired",
            "subtypes": [
                "deprecated_api_usage",
                "wrong_method_name",
                "wrong_argument_order",
                "wrong_result_extraction",
                "primitive_api_misuse",
            ],
        },
        "I_classical_bugs": {
            "label": "Classical bugs embedded in quantum programs",
            "origin": "classical-mutation-inspired",
            "subtypes": [
                "off_by_one",
                "wrong_constant",
                "wrong_conditional",
                "wrong_dictionary_key",
                "wrong_list_index",
                "copy_paste_bug",
                "uninitialized_variable",
                "wrong_return_value",
                "faulty_exception_handling",
            ],
        },
        "J_research_mutation_operators": {
            "label": "Research-benchmark-inspired mutation operators",
            "origin": "classical-and-quantum",
            "subtypes": [
                "statement_deletion",
                "statement_insertion",
                "statement_replacement",
                "arithmetic_operator_replacement",
                "relational_operator_replacement",
                "logical_connector_replacement",
                "constant_replacement",
                "variable_replacement",
                "function_call_replacement",
                "argument_order_mutation",
                "conditional_negation",
                "measurement_mapping_mutation",
                "parameter_expression_mutation",
                "entanglement_structure_mutation",
            ],
        },
    }


def q_gate_variant(
    operator_id: str,
    subtype: str,
    description: str,
    replacement: str,
    expected_effect: str = "silent semantic failure",
    difficulty: str = "medium",
    killable_by: list[str] | None = None,
    equivalent_candidate: bool = False,
) -> MutationVariant:
    return MutationVariant(
        operator_id=operator_id,
        category="A_gate_level_quantum_bugs",
        subtype=subtype,
        description=description,
        relevance="Quantum state evolution is path dependent, so a small gate mutation can silently change amplitudes or entanglement.",
        expected_effect=expected_effect,
        difficulty=difficulty,
        killable_by=killable_by or [KILLABILITY["unit"], KILLABILITY["statistical"], KILLABILITY["equivalence"]],
        replacement=replacement,
        origin="quantum-specific",
        quantum_specific=True,
        equivalent_candidate=equivalent_candidate,
    )


def measurement_variant(
    operator_id: str,
    subtype: str,
    description: str,
    replacement: str,
    expected_effect: str = "wrong distribution",
    difficulty: str = "medium",
) -> MutationVariant:
    return MutationVariant(
        operator_id=operator_id,
        category="C_measurement_bugs",
        subtype=subtype,
        description=description,
        relevance="Measurement bugs often leave circuit construction intact while corrupting the observed classical evidence used by tests.",
        expected_effect=expected_effect,
        difficulty=difficulty,
        killable_by=[KILLABILITY["unit"], KILLABILITY["statistical"], KILLABILITY["equivalence"]],
        replacement=replacement,
        origin="quantum-specific",
        quantum_specific=True,
    )


def parameter_variant(
    operator_id: str,
    subtype: str,
    description: str,
    replacement: str,
    expected_effect: str = "wrong expectation value",
    difficulty: str = "hard",
) -> MutationVariant:
    return MutationVariant(
        operator_id=operator_id,
        category="B_parameter_bugs",
        subtype=subtype,
        description=description,
        relevance="Parameterized quantum circuits are highly sensitive to angle values and parameter binding semantics.",
        expected_effect=expected_effect,
        difficulty=difficulty,
        killable_by=[KILLABILITY["property"], KILLABILITY["statistical"], KILLABILITY["equivalence"]],
        replacement=replacement,
        origin="mixed",
        quantum_specific=True,
    )


def classical_variant(
    operator_id: str,
    category: str,
    subtype: str,
    description: str,
    replacement: str,
    relevance: str,
    expected_effect: str,
    difficulty: str = "easy",
    killable_by: list[str] | None = None,
    equivalent_candidate: bool = False,
) -> MutationVariant:
    return MutationVariant(
        operator_id=operator_id,
        category=category,
        subtype=subtype,
        description=description,
        relevance=relevance,
        expected_effect=expected_effect,
        difficulty=difficulty,
        killable_by=killable_by or [KILLABILITY["unit"]],
        replacement=replacement,
        origin="classical-mutation-inspired",
        quantum_specific=False,
        equivalent_candidate=equivalent_candidate,
    )


def hadamard_site(site_id: str, qubit: int, alt_qubit: int | None = None) -> MutationSite:
    default = f"qc.h({qubit})"
    variants = [
        q_gate_variant("QGR_H_TO_X", "single_qubit_gate_replacement", f"Replace the Hadamard on qubit {qubit} with X.", f"qc.x({qubit})"),
        q_gate_variant("QGR_H_TO_Y", "single_qubit_gate_replacement", f"Replace the Hadamard on qubit {qubit} with Y.", f"qc.y({qubit})"),
        q_gate_variant("QGR_H_TO_Z", "single_qubit_gate_replacement", f"Replace the Hadamard on qubit {qubit} with Z.", f"qc.z({qubit})"),
        q_gate_variant("QGD_DELETE_H", "gate_deletion", f"Delete the Hadamard on qubit {qubit}.", "# deleted Hadamard"),
        q_gate_variant("QGI_DUPLICATE_H", "extra_gate_insertion", f"Apply two Hadamards in sequence on qubit {qubit}.", f"qc.h({qubit})\nqc.h({qubit})", expected_effect="no visible effect / equivalent mutant candidate", equivalent_candidate=True),
        q_gate_variant("QGI_H_PLUS_Z", "extra_gate_insertion", f"Insert an extra Z gate immediately after the Hadamard on qubit {qubit}.", f"qc.h({qubit})\nqc.z({qubit})"),
    ]
    if alt_qubit is not None:
        variants.append(
            q_gate_variant(
                "QQI_WRONG_H_QUBIT",
                "wrong_qubit",
                f"Move the Hadamard from qubit {qubit} to qubit {alt_qubit}.",
                f"qc.h({alt_qubit})",
            )
        )
    return MutationSite(site_id=site_id, placeholder=f"{{{{{site_id}}}}}", default=default, variants=variants)


def controlled_site(site_id: str, gate: str, control: int, target: int, alt_target: int | None = None) -> MutationSite:
    default = f"qc.{gate}({control}, {target})"
    base_name = gate.upper()
    variants = [
        q_gate_variant("QCR_SWAP_CZ", "controlled_gate_replacement", f"Replace {base_name} with CZ.", f"qc.cz({control}, {target})"),
        q_gate_variant("QCR_SWAP_CY", "controlled_gate_replacement", f"Replace {base_name} with CY.", f"qc.cy({control}, {target})"),
        q_gate_variant("QCR_DELETE_CONTROL", "missing_control", f"Drop the control and apply X directly to target {target}.", f"qc.x({target})"),
        q_gate_variant("QCR_REVERSE_CONTROL", "reversed_control_target", f"Reverse the {base_name} control/target relationship.", f"qc.{gate}({target}, {control})"),
        q_gate_variant("QCR_DELETE_ENTANGLER", "gate_deletion", f"Delete the {base_name} entangling gate.", "# deleted controlled gate"),
        q_gate_variant("QCR_SWAP_FOR_CONTROLLED", "controlled_gate_replacement", f"Replace {base_name} with SWAP.", f"qc.swap({control}, {target})"),
        q_gate_variant("QCR_DUPLICATE_ENTANGLER", "extra_gate_insertion", f"Apply the {base_name} gate twice.", f"qc.{gate}({control}, {target})\nqc.{gate}({control}, {target})", expected_effect="silent semantic failure"),
    ]
    if alt_target is not None:
        variants.append(
            q_gate_variant(
                "QQI_WRONG_TARGET",
                "wrong_qubit",
                f"Apply {base_name} to the wrong target qubit {alt_target}.",
                f"qc.{gate}({control}, {alt_target})",
            )
        )
    return MutationSite(site_id=site_id, placeholder=f"{{{{{site_id}}}}}", default=default, variants=variants)


def rotation_site(site_id: str, axis: str, parameter: str, qubit: int, alt_parameter: str | None = None) -> MutationSite:
    default = f"qc.r{axis.lower()}({parameter}, {qubit})"
    alt_parameter = alt_parameter or parameter
    variants = [
        parameter_variant("PAR_NEGATE", "sign_error", f"Negate the rotation angle for R{axis}.", f"qc.r{axis.lower()}(-({parameter}), {qubit})"),
        parameter_variant("PAR_OFFSET", "constant_offset", f"Add pi/8 to the R{axis} angle.", f"qc.r{axis.lower()}({parameter} + pi / 8, {qubit})"),
        parameter_variant("PAR_SCALE_HALF", "parameter_scaling", f"Halve the R{axis} angle.", f"qc.r{axis.lower()}({parameter} / 2, {qubit})"),
        parameter_variant("PAR_DEGREES", "degrees_vs_radians", f"Treat the R{axis} angle as degrees.", f"qc.r{axis.lower()}(({parameter}) * 180 / pi, {qubit})"),
        parameter_variant("PAR_WRONG_VARIABLE", "wrong_parameter_variable", f"Use the wrong parameter expression for R{axis}.", f"qc.r{axis.lower()}({alt_parameter}, {qubit})"),
        parameter_variant("PAR_ZERO", "stale_parameter", f"Force the R{axis} angle to zero.", f"qc.r{axis.lower()}(0.0, {qubit})"),
        parameter_variant("PAR_AXIS_SWAP", "wrong_rotation_angle", f"Apply the same parameter on the wrong rotation axis instead of R{axis}.", f"qc.rx({parameter}, {qubit})" if axis != "X" else f"qc.rz({parameter}, {qubit})"),
    ]
    return MutationSite(site_id=site_id, placeholder=f"{{{{{site_id}}}}}", default=default, variants=variants)


def measurement_site(site_id: str, qubit: int, cbit: int, alt_qubit: int | None = None, alt_cbit: int | None = None) -> MutationSite:
    default = f"qc.measure({qubit}, {cbit})"
    variants = [
        measurement_variant("MEAS_DELETE", "measurement_omission", f"Omit the measurement of qubit {qubit}.", "# deleted measurement", expected_effect="silent semantic failure"),
        measurement_variant("MEAS_WRONG_CBIT", "wrong_classical_bit", f"Measure qubit {qubit} into the wrong classical bit.", f"qc.measure({qubit}, {alt_cbit if alt_cbit is not None else cbit})"),
        measurement_variant("MEAS_PREMATURE", "premature_measurement", f"Measure qubit {qubit} and immediately apply Z, collapsing the state early.", f"qc.measure({qubit}, {cbit})\nqc.z({qubit})", expected_effect="degraded fidelity"),
        measurement_variant("MEAS_DUPLICATE", "mapping_reorder", f"Measure qubit {qubit} twice into the same classical bit.", f"qc.measure({qubit}, {cbit})\nqc.measure({qubit}, {cbit})", expected_effect="runtime failure"),
        measurement_variant("MEAS_SWAP_ORDER", "mapping_reorder", f"Add an additional measurement into a neighboring classical bit.", f"qc.measure({qubit}, {cbit})\nqc.measure({qubit}, {alt_cbit if alt_cbit is not None else cbit})", expected_effect="wrong distribution"),
    ]
    if alt_qubit is not None:
        variants.append(
            measurement_variant(
                "MEAS_WRONG_QUBIT",
                "wrong_measured_qubit",
                f"Measure the wrong qubit {alt_qubit} into classical bit {cbit}.",
                f"qc.measure({alt_qubit}, {cbit})",
            )
        )
    return MutationSite(site_id=site_id, placeholder=f"{{{{{site_id}}}}}", default=default, variants=variants)


def loop_range_site(site_id: str, default_expr: str, mutated_exprs: list[tuple[str, str]]) -> MutationSite:
    variants = [
        classical_variant(
            operator_id=operator_id,
            category="D_circuit_structure_bugs",
            subtype="loop_range_bug",
            description=description,
            replacement=expr,
            relevance="Loop-bound mutations are a classic source of off-by-one errors and are especially harmful in repeated entanglement or measurement pipelines.",
            expected_effect="silent semantic failure",
            difficulty="medium",
            killable_by=[KILLABILITY["unit"], KILLABILITY["equivalence"]],
        )
        for operator_id, description, expr in [(op, desc, expr) for op, desc, expr in mutated_exprs]
    ]
    return MutationSite(site_id=site_id, placeholder=f"{{{{{site_id}}}}}", default=default_expr, variants=variants)


def expr_site(
    site_id: str,
    default_expr: str,
    variants: list[MutationVariant],
) -> MutationSite:
    generic_variants = [
        classical_variant(
            "GEN_DELETE_STATEMENT",
            "J_research_mutation_operators",
            "statement_deletion",
            f"Delete the statement block at mutation site {site_id}.",
            "# deleted statement block",
            "Statement deletion is a canonical research mutation operator and creates controlled omissions in quantum workflows.",
            "silent semantic failure",
            difficulty="medium",
            killable_by=[KILLABILITY["unit"], KILLABILITY["equivalence"]],
        ),
        classical_variant(
            "GEN_ASSERT_TRAP",
            "J_research_mutation_operators",
            "statement_replacement",
            f"Replace the statement block at mutation site {site_id} with a runtime assertion trap.",
            'assert False, "Injected runtime mutation"',
            "Statement replacement is useful for separating parser-level validity from executable mutant handling.",
            "runtime failure",
            difficulty="easy",
            killable_by=[KILLABILITY["unit"]],
        ),
        classical_variant(
            "GEN_COPY_PASTE",
            "I_classical_bugs",
            "copy_paste_bug",
            f"Copy-paste the default block at mutation site {site_id} and repeat it twice.",
            f"{default_expr}\n{default_expr.splitlines()[0].lstrip()}",
            "Copy-paste style mutations are realistic in circuit construction and workflow orchestration code.",
            "silent semantic failure",
            difficulty="medium",
            killable_by=[KILLABILITY["unit"], KILLABILITY["equivalence"]],
        ),
        classical_variant(
            "GEN_PASS_BLOCK",
            "J_research_mutation_operators",
            "statement_replacement",
            f"Replace the statement block at mutation site {site_id} with pass.",
            "pass",
            "Replacing behavior with a no-op is a compact way to model missing logic without necessarily breaking syntax.",
            "silent semantic failure",
            difficulty="medium",
            killable_by=[KILLABILITY["unit"], KILLABILITY["equivalence"]],
        ),
        classical_variant(
            "GEN_SYNTAX_BREAK",
            "J_research_mutation_operators",
            "statement_replacement",
            f"Inject a syntax error at mutation site {site_id}.",
            "return )",
            "Mutation datasets benefit from including a small class of parse-failing mutants for tooling robustness experiments.",
            "syntax failure",
            difficulty="easy",
            killable_by=[KILLABILITY["unit"]],
        ),
    ]
    return MutationSite(site_id=site_id, placeholder=f"{{{{{site_id}}}}}", default=default_expr, variants=variants + generic_variants)


def _render(template: str, replacements: dict[str, str]) -> str:
    template_lines = dedent(template).strip("\n").splitlines()
    rendered_lines: list[str] = []

    for line in template_lines:
        replaced = False
        for placeholder, text in replacements.items():
            if line.strip() == placeholder:
                indent = line[: len(line) - len(line.lstrip())]
                block_lines = text.splitlines() or [""]
                rendered_lines.extend(f"{indent}{block_line}" if block_line else indent for block_line in block_lines)
                replaced = True
                break
        if replaced:
            continue

        updated_line = line
        for placeholder, text in replacements.items():
            updated_line = updated_line.replace(placeholder, text)
        rendered_lines.append(updated_line)

    return "\n".join(rendered_lines).strip() + "\n"


def seed_programs() -> list[SeedProgram]:
    seeds: list[SeedProgram] = []

    seeds.append(
        SeedProgram(
            seed_id="bell",
            family="bell",
            name="Bell State Creation",
            description="Prepare a Bell state and inspect both the circuit and ideal statevector probabilities.",
            tags=["entanglement", "state-preparation", "qiskit"],
            template="""
            from qiskit import QuantumCircuit
            from qiskit.quantum_info import Statevector


            def build_circuit() -> QuantumCircuit:
                qc = QuantumCircuit(2, 2)
                {{bell_h}}
                {{bell_cx}}
                {{bell_measure_0}}
                {{bell_measure_1}}
                return qc


            def ideal_probabilities():
                circuit = build_circuit().remove_final_measurements(inplace=False)
                return Statevector.from_instruction(circuit).probabilities_dict()


            def main():
                return ideal_probabilities()


            if __name__ == "__main__":
                print(main())
            """,
            sites=[
                hadamard_site("bell_h", 0, alt_qubit=1),
                controlled_site("bell_cx", "cx", 0, 1),
                measurement_site("bell_measure_0", 0, 0, alt_qubit=1, alt_cbit=1),
                measurement_site("bell_measure_1", 1, 1, alt_qubit=0, alt_cbit=0),
                expr_site(
                    "bell_post",
                    "# baseline placeholder",
                    [],
                ),
            ],
        )
    )

    seeds.append(
        SeedProgram(
            seed_id="ghz",
            family="ghz",
            name="GHZ State Creation",
            description="Prepare a three-qubit GHZ state using a fanout entanglement chain.",
            tags=["entanglement", "ghz", "qiskit"],
            template="""
            from qiskit import QuantumCircuit
            from qiskit.quantum_info import Statevector


            def build_circuit() -> QuantumCircuit:
                qc = QuantumCircuit(3, 3)
                {{ghz_h}}
                for qubit in {{ghz_range}}:
                    qc.cx(qubit, qubit + 1)
                {{ghz_barrier}}
                qc.measure([0, 1, 2], [0, 1, 2])
                return qc


            def ideal_probabilities():
                circuit = build_circuit().remove_final_measurements(inplace=False)
                return Statevector.from_instruction(circuit).probabilities_dict()


            def main():
                return ideal_probabilities()


            if __name__ == "__main__":
                print(main())
            """,
            sites=[
                hadamard_site("ghz_h", 0, alt_qubit=1),
                loop_range_site(
                    "ghz_range",
                    "range(2)",
                    [
                        ("LOOP_SHORT", "Stop the entanglement chain one step early.", "range(1)"),
                        ("LOOP_LONG", "Iterate over too many control qubits.", "range(3)"),
                        ("LOOP_SKIP_ZERO", "Start entanglement from qubit 1 instead of qubit 0.", "range(1, 3)"),
                    ],
                ),
                expr_site(
                    "ghz_barrier",
                    "qc.barrier()",
                    [
                        q_gate_variant("GHZ_EXTRA_Z", "extra_gate_insertion", "Insert an unintended Z gate before measurement.", "qc.z(2)\nqc.barrier()", expected_effect="silent semantic failure"),
                        classical_variant("GHZ_DELETE_BARRIER", "D_circuit_structure_bugs", "incorrect_subcircuit_composition", "Delete the barrier placeholder.", "# deleted barrier", "Barrier mutations can expose assumptions about subcircuit boundaries and compiler behavior.", "no visible effect / equivalent mutant candidate", difficulty="hard", equivalent_candidate=True),
                    ],
                ),
            ],
        )
    )

    seeds.append(
        SeedProgram(
            seed_id="teleportation",
            family="teleportation",
            name="Quantum Teleportation",
            description="Teleport an input state from qubit 0 to qubit 2 using Bell-pair preparation and classical corrections.",
            tags=["teleportation", "corrections", "qiskit"],
            template="""
            from math import pi
            from qiskit import QuantumCircuit


            def build_circuit(theta: float = pi / 3) -> QuantumCircuit:
                qc = QuantumCircuit(3, 2)
                qc.ry(theta, 0)
                {{tele_bell_h}}
                {{tele_bell_cx}}
                qc.cx(0, 1)
                qc.h(0)
                qc.measure(0, 0)
                qc.measure(1, 1)
                {{tele_correction_z}}
                {{tele_correction_x}}
                return qc


            def main():
                return build_circuit().count_ops()


            if __name__ == "__main__":
                print(main())
            """,
            sites=[
                hadamard_site("tele_bell_h", 1, alt_qubit=0),
                controlled_site("tele_bell_cx", "cx", 1, 2, alt_target=0),
                expr_site(
                    "tele_correction_z",
                    "with qc.if_test((0, 1)):\n        qc.z(2)",
                    [
                        q_gate_variant("TEL_WRONG_Z_TARGET", "wrong_qubit", "Apply the Z correction to the wrong qubit.", "with qc.if_test((0, 1)):\n        qc.z(1)"),
                        q_gate_variant("TEL_DELETE_Z", "gate_deletion", "Delete the phase correction branch.", "# deleted Z correction", expected_effect="silent semantic failure", difficulty="hard"),
                        q_gate_variant("TEL_X_FOR_Z", "single_qubit_gate_replacement", "Use X instead of Z in the first correction branch.", "with qc.if_test((0, 1)):\n        qc.x(2)", difficulty="hard"),
                    ],
                ),
                expr_site(
                    "tele_correction_x",
                    "with qc.if_test((1, 1)):\n        qc.x(2)",
                    [
                        q_gate_variant("TEL_SWAP_CLASSICAL", "teleportation_correction_bug", "Gate the X correction on the wrong classical register index.", "with qc.if_test((0, 1)):\n        qc.x(2)", difficulty="hard"),
                        q_gate_variant("TEL_DELETE_X", "gate_deletion", "Delete the bit-flip correction branch.", "# deleted X correction", difficulty="hard"),
                        q_gate_variant("TEL_Z_FOR_X", "single_qubit_gate_replacement", "Use Z instead of X in the second correction branch.", "with qc.if_test((1, 1)):\n        qc.z(2)", difficulty="hard"),
                    ],
                ),
            ],
        )
    )

    seeds.append(
        SeedProgram(
            seed_id="superdense",
            family="superdense",
            name="Superdense Coding",
            description="Encode two classical bits into one qubit of a Bell pair and decode them with an entangling inverse.",
            tags=["superdense-coding", "communication", "qiskit"],
            template="""
            from qiskit import QuantumCircuit


            def build_circuit(message: str = "10") -> QuantumCircuit:
                qc = QuantumCircuit(2, 2)
                qc.h(0)
                qc.cx(0, 1)
                {{sd_encode_first}}
                {{sd_encode_second}}
                qc.cx(0, 1)
                qc.h(0)
                qc.measure([0, 1], [0, 1])
                return qc


            def main():
                return build_circuit().count_ops()


            if __name__ == "__main__":
                print(main())
            """,
            sites=[
                expr_site(
                    "sd_encode_first",
                    'if message[0] == "1":\n        qc.z(0)',
                    [
                        classical_variant("SD_WRONG_INDEX", "I_classical_bugs", "wrong_list_index", "Read the wrong message bit when applying Z.", 'if message[1] == "1":\n        qc.z(0)', "Classical indexing bugs are realistic in hybrid encoders that map bits to gates.", "silent semantic failure", difficulty="medium"),
                        q_gate_variant("SD_Z_TO_X", "superdense_encoding_bug", "Use X instead of Z for the first encoded bit.", 'if message[0] == "1":\n        qc.x(0)', difficulty="hard"),
                        q_gate_variant("SD_DELETE_FIRST", "gate_deletion", "Delete the first encoding branch.", "# deleted first encoding branch", difficulty="hard"),
                    ],
                ),
                expr_site(
                    "sd_encode_second",
                    'if message[1] == "1":\n        qc.x(0)',
                    [
                        classical_variant("SD_WRONG_CONST", "I_classical_bugs", "wrong_constant", "Check for the wrong literal in the second encoding branch.", 'if message[1] == "0":\n        qc.x(0)', "Wrong constants in classical decision logic frequently invert expected quantum behavior.", "wrong distribution", difficulty="easy"),
                        q_gate_variant("SD_X_TO_Y", "single_qubit_gate_replacement", "Use Y instead of X for the second encoded bit.", 'if message[1] == "1":\n        qc.y(0)'),
                        q_gate_variant("SD_WRONG_QUBIT", "wrong_qubit", "Apply the second encoding gate to Bob's qubit instead of Alice's.", 'if message[1] == "1":\n        qc.x(1)'),
                    ],
                ),
            ],
        )
    )

    seeds.append(
        SeedProgram(
            seed_id="deutsch_jozsa",
            family="deutsch_jozsa",
            name="Deutsch-Jozsa",
            description="Construct a Deutsch-Jozsa circuit with a simple balanced oracle.",
            tags=["oracle", "deutsch-jozsa", "qiskit"],
            template="""
            from qiskit import QuantumCircuit


            def build_oracle() -> QuantumCircuit:
                oracle = QuantumCircuit(3)
                {{dj_oracle}}
                return oracle


            def build_circuit() -> QuantumCircuit:
                qc = QuantumCircuit(3, 2)
                qc.x(2)
                qc.h([0, 1, 2])
                qc.compose(build_oracle(), inplace=True)
                {{dj_final_h}}
                qc.measure([0, 1], [0, 1])
                return qc


            def main():
                return build_circuit().count_ops()


            if __name__ == "__main__":
                print(main())
            """,
            sites=[
                expr_site(
                    "dj_oracle",
                    "oracle.cx(0, 2)\noracle.cx(1, 2)",
                    [
                        q_gate_variant("DJ_DELETE_ORACLE_ARM", "oracle_mutation", "Delete one oracle arm from the balanced Deutsch-Jozsa oracle.", "oracle.cx(0, 2)", difficulty="hard"),
                        q_gate_variant("DJ_CZ_ORACLE", "controlled_gate_replacement", "Use CZ instead of CX in the oracle.", "oracle.cz(0, 2)\noracle.cx(1, 2)", difficulty="hard"),
                        q_gate_variant("DJ_REVERSE_ORACLE", "reversed_control_target", "Reverse the control and target in one oracle interaction.", "oracle.cx(2, 0)\noracle.cx(1, 2)", difficulty="hard"),
                    ],
                ),
                expr_site(
                    "dj_final_h",
                    "qc.h([0, 1])",
                    [
                        q_gate_variant("DJ_DELETE_FINAL_H", "oracle_mutation", "Delete the final Hadamards used for interference.", "# deleted final Hadamards", difficulty="hard"),
                        q_gate_variant("DJ_PARTIAL_FINAL_H", "oracle_mutation", "Apply the final Hadamard to only one query qubit.", "qc.h([0])", difficulty="hard"),
                        q_gate_variant("DJ_X_FOR_H", "single_qubit_gate_replacement", "Replace the final Hadamards with X gates.", "qc.x([0, 1])"),
                    ],
                ),
            ],
        )
    )

    seeds.append(
        SeedProgram(
            seed_id="bernstein_vazirani",
            family="bernstein_vazirani",
            name="Bernstein-Vazirani",
            description="Encode a secret string into a BV oracle and recover it via interference.",
            tags=["oracle", "bernstein-vazirani", "qiskit"],
            template="""
            from qiskit import QuantumCircuit


            SECRET = "101"


            def build_oracle(secret: str = SECRET) -> QuantumCircuit:
                oracle = QuantumCircuit(4)
                for idx, bit in enumerate(secret):
                    if bit == "1":
                        oracle.cx(idx, 3)
                return oracle


            def build_circuit(secret: str = SECRET) -> QuantumCircuit:
                qc = QuantumCircuit(4, 3)
                qc.x(3)
                qc.h([0, 1, 2, 3])
                qc.compose(build_oracle(secret), inplace=True)
                qc.h([0, 1, 2])
                {{bv_measure}}
                return qc


            def main():
                return build_circuit().count_ops()


            if __name__ == "__main__":
                print(main())
            """,
            sites=[
                expr_site(
                    "bv_measure",
                    "qc.measure([0, 1, 2], [0, 1, 2])",
                    [
                        measurement_variant("BV_REVERSE_MEASURE", "mapping_reorder", "Reverse the BV measurement map and induce an endianness bug.", "qc.measure([0, 1, 2], [2, 1, 0])"),
                        measurement_variant("BV_MEASURE_ANCILLA", "wrong_measured_qubit", "Accidentally read the oracle ancilla instead of the last query qubit.", "qc.measure([0, 1, 3], [0, 1, 2])"),
                    ],
                ),
                expr_site(
                    "bv_secret_logic",
                    "# baseline placeholder",
                    [],
                ),
            ],
        )
    )

    seeds.append(
        SeedProgram(
            seed_id="grover",
            family="grover",
            name="Grover Search",
            description="Run a one-iteration Grover search for target state 11 on two qubits.",
            tags=["grover", "oracle", "diffuser", "qiskit"],
            template="""
            from qiskit import QuantumCircuit


            def build_oracle() -> QuantumCircuit:
                oracle = QuantumCircuit(2)
                {{grover_oracle}}
                return oracle


            def build_diffuser() -> QuantumCircuit:
                diffuser = QuantumCircuit(2)
                diffuser.h([0, 1])
                diffuser.x([0, 1])
                diffuser.cz(0, 1)
                diffuser.x([0, 1])
                diffuser.h([0, 1])
                return diffuser


            def build_circuit(iterations: int = 1) -> QuantumCircuit:
                qc = QuantumCircuit(2, 2)
                qc.h([0, 1])
                for _ in range(iterations):
                    qc.compose(build_oracle(), inplace=True)
                    {{grover_diffuser}}
                qc.measure([0, 1], [0, 1])
                return qc


            def main():
                return build_circuit().count_ops()


            if __name__ == "__main__":
                print(main())
            """,
            sites=[
                expr_site(
                    "grover_oracle",
                    "oracle.cz(0, 1)",
                    [
                        q_gate_variant("GROVER_CX_ORACLE", "oracle_mutation", "Use CX instead of a phase-flip oracle.", "oracle.cx(0, 1)", difficulty="hard"),
                        q_gate_variant("GROVER_DELETE_ORACLE", "oracle_mutation", "Delete the Grover oracle phase flip.", "# deleted oracle", difficulty="hard"),
                        q_gate_variant("GROVER_EXTRA_X", "extra_gate_insertion", "Insert an unintended X gate into the oracle.", "oracle.x(0)\noracle.cz(0, 1)", expected_effect="wrong distribution"),
                    ],
                ),
                expr_site(
                    "grover_diffuser",
                    "qc.compose(build_diffuser(), inplace=True)",
                    [
                        q_gate_variant("GROVER_DELETE_DIFFUSER", "diffuser_mutation", "Delete the Grover diffuser.", "# deleted diffuser", difficulty="hard"),
                        q_gate_variant("GROVER_INVERSE_DIFFUSER", "inverse_misuse", "Use the inverse diffuser unexpectedly.", "qc.compose(build_diffuser().inverse(), inplace=True)", expected_effect="wrong distribution"),
                        classical_variant("GROVER_APPEND_ORACLE", "D_circuit_structure_bugs", "append_wrong_subroutine", "Compose the oracle twice instead of the diffuser.", "qc.compose(build_oracle(), inplace=True)", "Subroutine composition errors can silently preserve valid syntax while invalidating the algorithmic fixed point.", "wrong distribution", difficulty="hard", killable_by=[KILLABILITY["statistical"], KILLABILITY["equivalence"]]),
                    ],
                ),
            ],
        )
    )

    seeds.append(
        SeedProgram(
            seed_id="qft",
            family="qft",
            name="Quantum Fourier Transform",
            description="Build a three-qubit QFT circuit with controlled phases and terminal swaps.",
            tags=["qft", "phase", "qiskit"],
            template="""
            from math import pi
            from qiskit import QuantumCircuit


            def build_circuit() -> QuantumCircuit:
                qc = QuantumCircuit(3)
                qc.h(2)
                qc.cp(pi / 2, 1, 2)
                {{qft_cp_small}}
                qc.h(1)
                qc.cp(pi / 2, 0, 1)
                qc.h(0)
                {{qft_swap}}
                return qc


            def main():
                return build_circuit().count_ops()


            if __name__ == "__main__":
                print(main())
            """,
            sites=[
                expr_site(
                    "qft_cp_small",
                    "qc.cp(pi / 4, 0, 2)",
                    [
                        parameter_variant("QFT_WRONG_ANGLE", "qft_angle_bug", "Use pi/2 instead of pi/4 in the long-range QFT phase.", "qc.cp(pi / 2, 0, 2)", expected_effect="wrong distribution"),
                        parameter_variant("QFT_NEGATIVE_ANGLE", "sign_error", "Negate the long-range QFT phase.", "qc.cp(-pi / 4, 0, 2)", expected_effect="wrong distribution"),
                        q_gate_variant("QFT_CX_FOR_CP", "controlled_gate_replacement", "Use CX instead of controlled phase in the QFT core.", "qc.cx(0, 2)", expected_effect="wrong distribution", difficulty="hard"),
                    ],
                ),
                expr_site(
                    "qft_swap",
                    "qc.swap(0, 2)",
                    [
                        q_gate_variant("QFT_DELETE_SWAP", "entanglement_structure_mutation", "Delete the final swap pattern.", "# deleted swap", expected_effect="wrong distribution", difficulty="hard"),
                        q_gate_variant("QFT_CX_FOR_SWAP", "controlled_gate_replacement", "Replace the final swap with a single CX.", "qc.cx(0, 2)", expected_effect="wrong distribution"),
                        q_gate_variant("QFT_WRONG_SWAP", "wrong_qubit", "Swap the wrong pair of qubits at the end of QFT.", "qc.swap(0, 1)", expected_effect="wrong distribution"),
                    ],
                ),
            ],
        )
    )

    seeds.append(
        SeedProgram(
            seed_id="vqe_ansatz",
            family="vqe",
            name="VQE-Style Ansatz",
            description="Build a lightweight two-qubit hardware-efficient ansatz and estimate a simple Z expectation.",
            tags=["vqe", "variational", "parameterized", "qiskit"],
            template="""
            from math import pi
            from qiskit import QuantumCircuit
            from qiskit.quantum_info import SparsePauliOp, Statevector


            def build_ansatz(theta0: float, theta1: float) -> QuantumCircuit:
                qc = QuantumCircuit(2)
                {{vqe_rot_0}}
                {{vqe_rot_1}}
                {{vqe_entangler}}
                return qc


            def expectation(theta0: float, theta1: float) -> float:
                observable = SparsePauliOp.from_list([("ZZ", 1.0)])
                state = Statevector.from_instruction(build_ansatz(theta0, theta1))
                return float(state.expectation_value(observable).real)


            def main():
                return expectation(pi / 4, pi / 7)


            if __name__ == "__main__":
                print(main())
            """,
            sites=[
                rotation_site("vqe_rot_0", "Y", "theta0", 0, alt_parameter="theta1"),
                rotation_site("vqe_rot_1", "Y", "theta1", 1, alt_parameter="theta0"),
                controlled_site("vqe_entangler", "cx", 0, 1),
            ],
        )
    )

    seeds.append(
        SeedProgram(
            seed_id="qaoa",
            family="qaoa",
            name="QAOA-Style Layer",
            description="Construct a single-layer QAOA circuit for a ZZ cost term with X mixers.",
            tags=["qaoa", "variational", "parameterized", "qiskit"],
            template="""
            from math import pi
            from qiskit import QuantumCircuit


            def build_layer(gamma: float, beta: float) -> QuantumCircuit:
                qc = QuantumCircuit(2)
                qc.h([0, 1])
                qc.cx(0, 1)
                {{qaoa_cost}}
                qc.cx(0, 1)
                {{qaoa_mixer_0}}
                {{qaoa_mixer_1}}
                return qc


            def main():
                return build_layer(pi / 5, pi / 8).count_ops()


            if __name__ == "__main__":
                print(main())
            """,
            sites=[
                rotation_site("qaoa_cost", "Z", "2 * gamma", 1, alt_parameter="2 * beta"),
                rotation_site("qaoa_mixer_0", "X", "2 * beta", 0, alt_parameter="2 * gamma"),
                rotation_site("qaoa_mixer_1", "X", "2 * beta", 1, alt_parameter="2 * gamma"),
            ],
        )
    )

    seeds.append(
        SeedProgram(
            seed_id="swap_test",
            family="swap_test",
            name="Swap Test",
            description="Estimate overlap between two one-qubit states using a swap test with an ancilla.",
            tags=["swap-test", "ancilla", "qiskit"],
            template="""
            from math import pi
            from qiskit import QuantumCircuit


            def build_circuit() -> QuantumCircuit:
                qc = QuantumCircuit(3, 1)
                {{swap_h_start}}
                qc.ry(pi / 3, 1)
                qc.ry(pi / 4, 2)
                {{swap_controlled}}
                {{swap_h_end}}
                qc.measure(0, 0)
                return qc


            def main():
                return build_circuit().count_ops()


            if __name__ == "__main__":
                print(main())
            """,
            sites=[
                hadamard_site("swap_h_start", 0, alt_qubit=1),
                expr_site(
                    "swap_controlled",
                    "qc.cswap(0, 1, 2)",
                    [
                        q_gate_variant("SWAPTEST_DELETE_CSWAP", "swap_test_control_bug", "Delete the controlled swap in the swap test.", "# deleted controlled swap", difficulty="hard"),
                        q_gate_variant("SWAPTEST_CX_FOR_CSWAP", "controlled_gate_replacement", "Replace the controlled swap with a single CX.", "qc.cx(1, 2)", expected_effect="wrong distribution", difficulty="hard"),
                        q_gate_variant("SWAPTEST_WRONG_CONTROL", "wrong_qubit", "Use the wrong ancilla/data qubit as the controlled-swap control.", "qc.cswap(1, 0, 2)", expected_effect="wrong distribution", difficulty="hard"),
                    ],
                ),
                hadamard_site("swap_h_end", 0, alt_qubit=2),
            ],
        )
    )

    seeds.append(
        SeedProgram(
            seed_id="measurement_pipeline",
            family="measurement_pipeline",
            name="Measurement Pipeline",
            description="Measure a circuit and post-process counts into a success probability.",
            tags=["measurement", "post-processing", "qiskit"],
            template="""
            from qiskit import QuantumCircuit


            def build_circuit() -> QuantumCircuit:
                qc = QuantumCircuit(2, 2)
                qc.h(0)
                qc.cx(0, 1)
                qc.measure([0, 1], [0, 1])
                return qc


            def success_probability(counts: dict[str, int]) -> float:
                total = sum(counts.values())
                {{measure_success}}


            def main():
                return success_probability({"00": 512, "11": 512})


            if __name__ == "__main__":
                print(main())
            """,
            sites=[
                expr_site(
                    "measure_success",
                    'success = counts.get("00", 0) + counts.get("11", 0)\nreturn success / total if total else 0.0',
                    [
                        classical_variant("MEAS_ENDIANNESS", "C_measurement_bugs", "endianness_postprocessing_bug", "Use the wrong Bell-state bitstrings during post-processing.", 'success = counts.get("01", 0) + counts.get("10", 0)\nreturn success / total if total else 0.0', "Bitstring ordering bugs are common because many SDKs use little-endian conventions.", "wrong distribution", difficulty="medium", killable_by=[KILLABILITY["unit"], KILLABILITY["statistical"]]),
                        classical_variant("MEAS_WRONG_KEY", "I_classical_bugs", "wrong_dictionary_key", "Read a wrong dictionary key from the counts table.", 'success = counts.get("001", 0) + counts.get("11", 0)\nreturn success / total if total else 0.0', "Classical result-decoding bugs can hide behind otherwise correct quantum execution.", "silent semantic failure", difficulty="easy"),
                        classical_variant("MEAS_RETURN_TOTAL", "I_classical_bugs", "wrong_return_value", "Return the raw success count instead of a normalized probability.", 'success = counts.get("00", 0) + counts.get("11", 0)\nreturn success', "Wrong return-value mutants are useful for separating classical assertion strength from quantum correctness.", "silent semantic failure", difficulty="easy"),
                    ],
                ),
            ],
        )
    )

    seeds.append(
        SeedProgram(
            seed_id="noise_workflow",
            family="noise",
            name="Noise Simulation Workflow",
            description="Run a Bell-state circuit through an Aer noise model when Aer is installed.",
            tags=["noise", "aer", "backend", "qiskit"],
            template="""
            from qiskit import QuantumCircuit, transpile


            def build_circuit() -> QuantumCircuit:
                qc = QuantumCircuit(2, 2)
                qc.h(0)
                qc.cx(0, 1)
                qc.measure([0, 1], [0, 1])
                return qc


            def run_noisy(shots: int = 512):
                from qiskit_aer import AerSimulator
                from qiskit_aer.noise import NoiseModel, depolarizing_error

                simulator = {{noise_backend}}
                noise_model = NoiseModel()
                noise_model.add_all_qubit_quantum_error(depolarizing_error(0.02, 1), ["h"])
                compiled = transpile(build_circuit(), simulator)
                {{noise_run}}


            def main():
                return run_noisy()


            if __name__ == "__main__":
                print(main())
            """,
            sites=[
                expr_site(
                    "noise_backend",
                    "AerSimulator()",
                    [
                        classical_variant("NOISE_DENSITY_BACKEND", "F_backend_execution_bugs", "wrong_backend", "Use a statevector simulator while still assuming noisy counts.", "AerSimulator(method=\"statevector\")", "Backend selection bugs can invalidate the experimental assumptions of a mutation-testing benchmark.", "runtime failure", difficulty="medium", killable_by=[KILLABILITY["unit"]]),
                        classical_variant("NOISE_MISSING_BACKEND", "H_api_misuse_bugs", "wrong_method_name", "Instantiate a misspelled simulator class.", "AerSimulatr()", "API misuse mutants model realistic breakages caused by SDK churn and typo-level mistakes.", "runtime failure", difficulty="easy"),
                    ],
                ),
                expr_site(
                    "noise_run",
                    "result = simulator.run(compiled, noise_model=noise_model, shots=shots).result()\nreturn result.get_counts()",
                    [
                        classical_variant("NOISE_DELETE_MODEL", "F_backend_execution_bugs", "noise_model_misapplied", "Forget to pass the noise model to the backend run call.", "result = simulator.run(compiled, shots=shots).result()\nreturn result.get_counts()", "Misapplied noise models are research-relevant because they change the fault model rather than the circuit.", "degraded fidelity", difficulty="hard", killable_by=[KILLABILITY["statistical"], KILLABILITY["equivalence"]]),
                        classical_variant("NOISE_WRONG_RESULT_ACCESS", "F_backend_execution_bugs", "result_access_bug", "Use the wrong result accessor after a noisy run.", "result = simulator.run(compiled, noise_model=noise_model, shots=shots).result()\nreturn result.get_statevector()", "Result-object misuse is common when switching between statevector and shot-based execution APIs.", "runtime failure", difficulty="easy"),
                        classical_variant("NOISE_ONE_SHOT", "F_backend_execution_bugs", "wrong_shot_count", "Collapse the shot count to one sample.", "result = simulator.run(compiled, noise_model=noise_model, shots=1).result()\nreturn result.get_counts()", "Shot-count changes alter the statistical strength of assertions and can make flaky mutants harder to kill.", "wrong distribution", difficulty="medium", killable_by=[KILLABILITY["statistical"]]),
                    ],
                ),
            ],
        )
    )

    seeds.append(
        SeedProgram(
            seed_id="transpile_workflow",
            family="transpile",
            name="Transpilation and Backend Workflow",
            description="Transpile a parameterized circuit for a backend and return the transpiled depth.",
            tags=["transpile", "backend", "qiskit"],
            template="""
            from math import pi
            from qiskit import QuantumCircuit, transpile


            def build_circuit() -> QuantumCircuit:
                qc = QuantumCircuit(2)
                qc.h(0)
                qc.cx(0, 1)
                qc.rz(pi / 7, 1)
                return qc


            def compile_for_backend():
                from qiskit.providers.fake_provider import GenericBackendV2

                backend = GenericBackendV2(num_qubits=2, basis_gates=["rz", "sx", "x", "cx"])
                {{transpile_call}}


            def main():
                return compile_for_backend()


            if __name__ == "__main__":
                print(main())
            """,
            sites=[
                expr_site(
                    "transpile_call",
                    "compiled = transpile(build_circuit(), backend=backend, optimization_level=1)\nreturn compiled.depth()",
                    [
                        classical_variant("TRANSPILE_SKIP", "F_backend_execution_bugs", "missing_transpile", "Skip transpilation and return the uncompiled depth directly.", "compiled = build_circuit()\nreturn compiled.depth()", "Skipping transpilation changes backend assumptions and can mask layout or basis issues.", "silent semantic failure", difficulty="medium", killable_by=[KILLABILITY["unit"], KILLABILITY["equivalence"]]),
                        classical_variant("TRANSPILE_OPT3", "F_backend_execution_bugs", "wrong_optimization_assumption", "Assume optimization level 3 when baseline uses level 1.", "compiled = transpile(build_circuit(), backend=backend, optimization_level=3)\nreturn compiled.depth()", "Optimization level affects circuit structure and may break structural regression tests.", "silent semantic failure", difficulty="medium"),
                        classical_variant("TRANSPILE_RESULT_ACCESS", "H_api_misuse_bugs", "wrong_result_extraction", "Return an operation count mapping instead of the transpiled depth.", "compiled = transpile(build_circuit(), backend=backend, optimization_level=1)\nreturn compiled.count_ops()", "API-result misreads often happen when developers switch test or reporting objectives midstream.", "silent semantic failure", difficulty="easy"),
                    ],
                ),
            ],
        )
    )

    seeds.append(
        SeedProgram(
            seed_id="hybrid_loop",
            family="hybrid",
            name="Hybrid Quantum-Classical Loop",
            description="Optimize a simple angle parameter using finite-difference updates against a quantum expectation.",
            tags=["hybrid", "optimizer", "qiskit"],
            template="""
            from math import pi
            from qiskit import QuantumCircuit
            from qiskit.quantum_info import SparsePauliOp, Statevector


            def expectation(theta: float) -> float:
                qc = QuantumCircuit(1)
                qc.ry(theta, 0)
                observable = SparsePauliOp.from_list([("Z", 1.0)])
                return float(Statevector.from_instruction(qc).expectation_value(observable).real)


            def optimize(steps: int = 8, lr: float = 0.2) -> float:
                theta = pi / 8
                for _ in range(steps):
                    eps = 1e-3
                    grad = (expectation(theta + eps) - expectation(theta - eps)) / (2 * eps)
                    {{hybrid_update}}
                return theta


            def main():
                return optimize()


            if __name__ == "__main__":
                print(main())
            """,
            sites=[
                expr_site(
                    "hybrid_update",
                    "theta -= lr * grad",
                    [
                        classical_variant("HYBRID_ASCEND", "G_hybrid_bugs", "optimizer_direction_bug", "Perform gradient ascent instead of descent.", "theta += lr * grad", "Hybrid optimizers are a major source of silent failures because the classical loop appears valid while converging in the wrong direction.", "wrong expectation value", difficulty="medium", killable_by=[KILLABILITY["property"], KILLABILITY["equivalence"]]),
                        classical_variant("HYBRID_STALE", "G_hybrid_bugs", "stale_model_outputs", "Ignore the gradient and keep theta fixed.", "theta -= lr * 0.0", "Stale optimizer-state bugs are common in iterative quantum-classical workloads.", "wrong expectation value", difficulty="medium", killable_by=[KILLABILITY["property"], KILLABILITY["equivalence"]]),
                        classical_variant("HYBRID_DOUBLE_STEP", "G_hybrid_bugs", "wrong_parameter_update", "Take an oversized double learning-rate step.", "theta -= 2 * lr * grad", "Update-step mutations stress numerical robustness in hybrid testing pipelines.", "wrong expectation value", difficulty="hard", killable_by=[KILLABILITY["property"], KILLABILITY["equivalence"]]),
                    ],
                ),
            ],
        )
    )

    seeds.append(
        SeedProgram(
            seed_id="parameterized_circuit",
            family="parameterized",
            name="Parameterized Circuit Binding",
            description="Create a small circuit with Qiskit Parameters and bind numerical values.",
            tags=["parameters", "binding", "qiskit"],
            template="""
            from qiskit import QuantumCircuit
            from qiskit.circuit import Parameter


            THETA = Parameter("theta")
            PHI = Parameter("phi")


            def build_template() -> QuantumCircuit:
                qc = QuantumCircuit(2)
                qc.ry(THETA, 0)
                qc.rz(PHI, 1)
                qc.cx(0, 1)
                return qc


            def bind_values(theta: float, phi: float) -> QuantumCircuit:
                {{bind_logic}}


            def main():
                return bind_values(0.2, 0.3).count_ops()


            if __name__ == "__main__":
                print(main())
            """,
            sites=[
                expr_site(
                    "bind_logic",
                    "return build_template().assign_parameters({THETA: theta, PHI: phi})",
                    [
                        parameter_variant("BIND_SWAP", "binding_order_mismatch", "Swap theta and phi during parameter binding.", "return build_template().assign_parameters({THETA: phi, PHI: theta})"),
                        parameter_variant("BIND_STALE", "stale_parameter", "Ignore the incoming theta argument and keep a stale constant.", "return build_template().assign_parameters({THETA: 0.0, PHI: phi})"),
                        classical_variant("BIND_WRONG_METHOD", "H_api_misuse_bugs", "wrong_method_name", "Call a nonexistent parameter-binding helper.", "return build_template().bind_paramaters({THETA: theta, PHI: phi})", "API misuse around parameter binding is common because helper names differ across SDK versions.", "runtime failure", difficulty="easy"),
                    ],
                ),
            ],
        )
    )

    seeds.append(
        SeedProgram(
            seed_id="controlled_ops",
            family="controlled_ops",
            name="Controlled Operations",
            description="Demonstrate controlled operations and a derived multi-control helper.",
            tags=["controlled-gates", "entanglement", "qiskit"],
            template="""
            from qiskit import QuantumCircuit


            def build_circuit() -> QuantumCircuit:
                qc = QuantumCircuit(3)
                qc.h(0)
                {{ctrl_cx}}
                {{ctrl_cz}}
                return qc


            def main():
                return build_circuit().count_ops()


            if __name__ == "__main__":
                print(main())
            """,
            sites=[
                controlled_site("ctrl_cx", "cx", 0, 1, alt_target=2),
                expr_site(
                    "ctrl_cz",
                    "qc.cz(1, 2)",
                    [
                        q_gate_variant("CTRL_Z_TO_CX", "controlled_gate_replacement", "Replace CZ with CX in the second controlled operation.", "qc.cx(1, 2)"),
                        q_gate_variant("CTRL_DELETE_CZ", "gate_deletion", "Delete the terminal CZ gate.", "# deleted controlled Z"),
                        q_gate_variant("CTRL_REVERSE_CZ", "reversed_control_target", "Reverse the CZ control and target order.", "qc.cz(2, 1)", expected_effect="no visible effect / equivalent mutant candidate", equivalent_candidate=True),
                    ],
                ),
            ],
        )
    )

    seeds.append(
        SeedProgram(
            seed_id="mid_circuit",
            family="mid_circuit",
            name="Mid-Circuit Measurement and Conditional Logic",
            description="Measure a qubit mid-circuit, reset it, and branch conditionally on the observed outcome.",
            tags=["mid-circuit-measurement", "conditional", "qiskit"],
            template="""
            from qiskit import QuantumCircuit


            def build_circuit() -> QuantumCircuit:
                qc = QuantumCircuit(2, 1)
                qc.h(0)
                qc.measure(0, 0)
                {{mid_reset}}
                {{mid_conditional}}
                return qc


            def main():
                return build_circuit().count_ops()


            if __name__ == "__main__":
                print(main())
            """,
            sites=[
                expr_site(
                    "mid_reset",
                    "qc.reset(0)",
                    [
                        classical_variant("MID_DELETE_RESET", "D_circuit_structure_bugs", "missing_reset", "Delete the reset after the mid-circuit measurement.", "# deleted reset", "Missing reset changes the semantics of qubit reuse and is especially relevant on hardware-constrained circuits.", "silent semantic failure", difficulty="hard", killable_by=[KILLABILITY["unit"], KILLABILITY["equivalence"]]),
                        q_gate_variant("MID_RESET_WRONG_QUBIT", "wrong_qubit", "Reset the wrong qubit after the mid-circuit measurement.", "qc.reset(1)", expected_effect="silent semantic failure", difficulty="hard"),
                    ],
                ),
                expr_site(
                    "mid_conditional",
                    "with qc.if_test((0, 1)):\n        qc.x(1)",
                    [
                        q_gate_variant("MID_Z_FOR_X", "single_qubit_gate_replacement", "Use Z instead of X in the mid-circuit conditional branch.", "with qc.if_test((0, 1)):\n        qc.z(1)", difficulty="hard"),
                        q_gate_variant("MID_WRONG_CONDITION", "wrong_qubit", "Trigger the branch on classical value 0 instead of 1.", "with qc.if_test((0, 0)):\n        qc.x(1)", expected_effect="silent semantic failure"),
                        q_gate_variant("MID_DELETE_BRANCH", "gate_deletion", "Delete the conditional correction branch.", "# deleted conditional branch", difficulty="hard"),
                    ],
                ),
            ],
        )
    )

    return seeds


def render_seed(seed: SeedProgram) -> str:
    replacements = {site.placeholder: site.default for site in seed.sites}
    return _render(seed.template, replacements)


def render_mutant(seed: SeedProgram, selected: dict[str, MutationVariant]) -> str:
    replacements = {}
    for site in seed.sites:
        variant = selected.get(site.site_id)
        replacements[site.placeholder] = variant.replacement if variant else site.default
    return _render(seed.template, replacements)


def generate_metadata_schema() -> dict:
    return {
        "fields": [
            "mutation_id",
            "seed_id",
            "family",
            "order",
            "source_seed_path",
            "mutant_path",
            "mutation_category",
            "mutation_subtype",
            "operator_id",
            "operator_origin",
            "quantum_specific",
            "equivalent_candidate",
            "bug_description",
            "testing_relevance",
            "expected_effect",
            "difficulty",
            "likely_killable_by",
            "primary_site",
            "secondary_sites",
        ]
    }


def build_dataset(output_root: Path, higher_order_per_seed: int = 2) -> dict:
    output_root.mkdir(parents=True, exist_ok=True)
    seeds_dir = output_root / "seeds"
    mutants_dir = output_root / "mutants"
    metadata_dir = output_root / "metadata"
    seeds_dir.mkdir(exist_ok=True)
    mutants_dir.mkdir(exist_ok=True)
    metadata_dir.mkdir(exist_ok=True)

    records: list[MutationRecord] = []
    seed_summary: list[dict] = []
    seed_payloads: list[dict] = []
    mutant_payloads: list[dict] = []
    seeds = seed_programs()

    for seed in seeds:
        family_dir = mutants_dir / seed.family
        family_dir.mkdir(parents=True, exist_ok=True)
        seed_path = seeds_dir / f"{seed.seed_id}.py"
        seed_code = render_seed(seed)
        seed_path.write_text(seed_code, encoding="utf-8")
        seed_payloads.append(
            {
                "seed_id": seed.seed_id,
                "family": seed.family,
                "name": seed.name,
                "description": seed.description,
                "tags": seed.tags,
                "path": str(seed_path.as_posix()),
                "code": seed_code,
            }
        )
        seed_mutant_count = 0

        for index, site in enumerate(seed.sites, start=1):
            for variant_idx, variant in enumerate(site.variants, start=1):
                mutation_id = f"{seed.seed_id.upper()}_M{seed_mutant_count + 1:03d}"
                mutant_path = family_dir / f"{mutation_id.lower()}.py"
                mutant_code = render_mutant(seed, {site.site_id: variant})
                mutant_path.write_text(mutant_code, encoding="utf-8")
                record = MutationRecord(
                    mutation_id=mutation_id,
                    seed_id=seed.seed_id,
                    family=seed.family,
                    order="first_order",
                    source_seed_path=str(seed_path.as_posix()),
                    mutant_path=str(mutant_path.as_posix()),
                    mutation_category=variant.category,
                    mutation_subtype=variant.subtype,
                    operator_id=variant.operator_id,
                    operator_origin=variant.origin,
                    quantum_specific=variant.quantum_specific,
                    equivalent_candidate=variant.equivalent_candidate,
                    bug_description=variant.description,
                    testing_relevance=variant.relevance,
                    expected_effect=variant.expected_effect,
                    difficulty=variant.difficulty,
                    likely_killable_by=variant.killable_by,
                    primary_site=site.site_id,
                )
                records.append(record)
                mutant_payloads.append(
                    {
                        **asdict(record),
                        "mutant_code": mutant_code,
                        "source_seed_code": seed_code,
                    }
                )
                seed_mutant_count += 1

        candidate_sites = [site for site in seed.sites if site.variants]
        ho_count = 0
        for first, second in itertools.combinations(candidate_sites[: min(len(candidate_sites), 5)], 2):
            if ho_count >= higher_order_per_seed:
                break
            first_variant = first.variants[0]
            second_variant = second.variants[0]
            mutation_id = f"{seed.seed_id.upper()}_HO{ho_count + 1:03d}"
            mutant_path = family_dir / f"{mutation_id.lower()}.py"
            mutant_code = render_mutant(seed, {first.site_id: first_variant, second.site_id: second_variant})
            mutant_path.write_text(mutant_code, encoding="utf-8")
            record = MutationRecord(
                mutation_id=mutation_id,
                seed_id=seed.seed_id,
                family=seed.family,
                order="higher_order",
                source_seed_path=str(seed_path.as_posix()),
                mutant_path=str(mutant_path.as_posix()),
                mutation_category=f"{first_variant.category}+{second_variant.category}",
                mutation_subtype=f"{first_variant.subtype}+{second_variant.subtype}",
                operator_id=f"{first_variant.operator_id}+{second_variant.operator_id}",
                operator_origin=f"{first_variant.origin}+{second_variant.origin}",
                quantum_specific=first_variant.quantum_specific or second_variant.quantum_specific,
                equivalent_candidate=first_variant.equivalent_candidate or second_variant.equivalent_candidate,
                bug_description=f"Higher-order mutant combining: {first_variant.description} AND {second_variant.description}",
                testing_relevance="Higher-order mutants stress fault interactions and help evaluate robustness beyond one-bug-per-mutant cases.",
                expected_effect="silent semantic failure",
                difficulty="hard",
                likely_killable_by=[KILLABILITY["statistical"], KILLABILITY["equivalence"]],
                primary_site=first.site_id,
                secondary_sites=[second.site_id],
            )
            records.append(record)
            mutant_payloads.append(
                {
                    **asdict(record),
                    "mutant_code": mutant_code,
                    "source_seed_code": seed_code,
                }
            )
            ho_count += 1
            seed_mutant_count += 1

        seed_summary.append(
            {
                "seed_id": seed.seed_id,
                "family": seed.family,
                "name": seed.name,
                "tags": seed.tags,
                "mutant_count": seed_mutant_count,
                "site_count": len(seed.sites),
            }
        )

    metadata_json = metadata_dir / "mutants.json"
    metadata_csv = metadata_dir / "mutants.csv"
    catalog_json = metadata_dir / "mutation_catalog.json"
    schema_json = metadata_dir / "metadata_schema.json"
    summary_json = metadata_dir / "seed_summary.json"
    bundle_json = metadata_dir / "dataset_bundle.json"

    metadata_json.write_text(json.dumps([asdict(record) for record in records], indent=2), encoding="utf-8")
    with metadata_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(records[0]).keys()))
        writer.writeheader()
        for record in records:
            row = asdict(record)
            row["likely_killable_by"] = "|".join(record.likely_killable_by)
            row["secondary_sites"] = "|".join(record.secondary_sites)
            writer.writerow(row)
    catalog_json.write_text(
        json.dumps(
            {
                "taxonomy": taxonomy(),
                "operators": sorted({record.operator_id for record in records}),
                "seed_programs": seed_summary,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    schema_json.write_text(json.dumps(generate_metadata_schema(), indent=2), encoding="utf-8")
    summary_json.write_text(json.dumps(seed_summary, indent=2), encoding="utf-8")
    bundle_json.write_text(
        json.dumps(
            {
                "dataset_name": "quantum_mutation_dataset",
                "target_stack": ["python", "qiskit"],
                "taxonomy": taxonomy(),
                "metadata_schema": generate_metadata_schema(),
                "seed_summary": seed_summary,
                "seeds": seed_payloads,
                "mutants": mutant_payloads,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    return {
        "seed_count": len(seeds),
        "mutant_count": len(records),
        "metadata_json": str(metadata_json),
        "metadata_csv": str(metadata_csv),
        "catalog_json": str(catalog_json),
        "bundle_json": str(bundle_json),
    }


def iter_python_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if path.is_dir():
            yield from path.rglob("*.py")
        elif path.suffix == ".py":
            yield path
