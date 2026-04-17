from math import pi
from qiskit import QuantumCircuit


def build_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(3, 1)
    # deleted Hadamard
    qc.ry(pi / 3, 1)
    qc.ry(pi / 4, 2)
    qc.cswap(0, 1, 2)
    qc.h(0)
    qc.measure(0, 0)
    return qc


def main():
    return build_circuit().count_ops()


if __name__ == "__main__":
    print(main())
