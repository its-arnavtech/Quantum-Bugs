from qiskit import QuantumCircuit


SECRET = "101"


def build_oracle(secret: str = SECRET) -> QuantumCircuit:
    oracle = QuantumCircuit(4)
    for idx, bit in enumerate(secret):
        if bit == "1":
            oracle.cx(idx, 3)
    return oracle


def build_circuit(secret: str = SECRET) -> QuantumCircuit:
    qc = QuantumCircuit(4, 3)
    qc.x(3)
    qc.h([0, 1, 2, 3])
    qc.compose(build_oracle(secret), inplace=True)
    qc.h([0, 1, 2])
    assert False, "Injected runtime mutation"
    return qc


def main():
    return build_circuit().count_ops()


if __name__ == "__main__":
    print(main())
