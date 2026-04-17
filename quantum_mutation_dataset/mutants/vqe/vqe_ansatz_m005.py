from math import pi
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector


def build_ansatz(theta0: float, theta1: float) -> QuantumCircuit:
    qc = QuantumCircuit(2)
    qc.ry(theta1, 0)
    qc.ry(theta1, 1)
    qc.cx(0, 1)
    return qc


def expectation(theta0: float, theta1: float) -> float:
    observable = SparsePauliOp.from_list([("ZZ", 1.0)])
    state = Statevector.from_instruction(build_ansatz(theta0, theta1))
    return float(state.expectation_value(observable).real)


def main():
    return expectation(pi / 4, pi / 7)


if __name__ == "__main__":
    print(main())
