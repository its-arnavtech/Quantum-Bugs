from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


def build_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    for qubit in range(1):
        qc.cx(qubit, qubit + 1)
    qc.barrier()
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc


def ideal_probabilities():
    circuit = build_circuit().remove_final_measurements(inplace=False)
    return Statevector.from_instruction(circuit).probabilities_dict()


def main():
    return ideal_probabilities()


if __name__ == "__main__":
    print(main())
