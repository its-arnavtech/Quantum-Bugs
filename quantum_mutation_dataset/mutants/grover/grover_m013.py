from qiskit import QuantumCircuit


def build_oracle() -> QuantumCircuit:
    oracle = QuantumCircuit(2)
    oracle.cz(0, 1)
    return oracle


def build_diffuser() -> QuantumCircuit:
    diffuser = QuantumCircuit(2)
    diffuser.h([0, 1])
    diffuser.x([0, 1])
    diffuser.cz(0, 1)
    diffuser.x([0, 1])
    diffuser.h([0, 1])
    return diffuser


def build_circuit(iterations: int = 1) -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.h([0, 1])
    for _ in range(iterations):
        qc.compose(build_oracle(), inplace=True)
        assert False, "Injected runtime mutation"
    qc.measure([0, 1], [0, 1])
    return qc


def main():
    return build_circuit().count_ops()


if __name__ == "__main__":
    print(main())
