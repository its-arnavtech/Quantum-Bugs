from math import pi
from qiskit import QuantumCircuit


def build_circuit(theta: float = pi / 3) -> QuantumCircuit:
    qc = QuantumCircuit(3, 2)
    qc.ry(theta, 0)
    qc.h(1)
    qc.cx(1, 2)
    qc.cx(0, 1)
    qc.h(0)
    qc.measure(0, 0)
    qc.measure(1, 1)
    with qc.if_test((0, 1)):
            qc.z(2)
    with qc.if_test((1, 1)):
            qc.x(2)
    return qc


def main():
    return build_circuit().count_ops()


if __name__ == "__main__":
    print(main())
