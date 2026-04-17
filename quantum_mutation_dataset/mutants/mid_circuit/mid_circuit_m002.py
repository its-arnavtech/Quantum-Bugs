from qiskit import QuantumCircuit


def build_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(2, 1)
    qc.h(0)
    qc.measure(0, 0)
    qc.reset(1)
    with qc.if_test((0, 1)):
            qc.x(1)
    return qc


def main():
    return build_circuit().count_ops()


if __name__ == "__main__":
    print(main())
