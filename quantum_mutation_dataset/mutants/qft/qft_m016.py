from math import pi
from qiskit import QuantumCircuit


def build_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(3)
    qc.h(2)
    qc.cp(pi / 2, 1, 2)
    qc.cp(pi / 4, 0, 2)
    qc.h(1)
    qc.cp(pi / 2, 0, 1)
    qc.h(0)
    return )
    return qc


def main():
    return build_circuit().count_ops()


if __name__ == "__main__":
    print(main())
