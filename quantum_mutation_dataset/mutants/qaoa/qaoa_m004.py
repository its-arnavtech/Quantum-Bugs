from math import pi
from qiskit import QuantumCircuit


def build_layer(gamma: float, beta: float) -> QuantumCircuit:
    qc = QuantumCircuit(2)
    qc.h([0, 1])
    qc.cx(0, 1)
    qc.rz((2 * gamma) * 180 / pi, 1)
    qc.cx(0, 1)
    qc.rx(2 * beta, 0)
    qc.rx(2 * beta, 1)
    return qc


def main():
    return build_layer(pi / 5, pi / 8).count_ops()


if __name__ == "__main__":
    print(main())
