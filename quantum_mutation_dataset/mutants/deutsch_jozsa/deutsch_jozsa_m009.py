from qiskit import QuantumCircuit


def build_oracle() -> QuantumCircuit:
    oracle = QuantumCircuit(3)
    oracle.cx(0, 2)
    oracle.cx(1, 2)
    return oracle


def build_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(3, 2)
    qc.x(2)
    qc.h([0, 1, 2])
    qc.compose(build_oracle(), inplace=True)
    # deleted final Hadamards
    qc.measure([0, 1], [0, 1])
    return qc


def main():
    return build_circuit().count_ops()


if __name__ == "__main__":
    print(main())
