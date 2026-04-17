from qiskit import QuantumCircuit


def build_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(0, 1)
    qc.cz(1, 2)
    return qc


def main():
    return build_circuit().count_ops()


if __name__ == "__main__":
    print(main())
