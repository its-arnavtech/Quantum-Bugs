from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


def build_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure(0, 1)
    qc.measure(1, 1)
    return qc


def ideal_probabilities():
    circuit = build_circuit().remove_final_measurements(inplace=False)
    return Statevector.from_instruction(circuit).probabilities_dict()


def main():
    return ideal_probabilities()


if __name__ == "__main__":
    print(main())
