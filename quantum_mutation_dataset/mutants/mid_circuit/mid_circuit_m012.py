from qiskit import QuantumCircuit


def build_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(2, 1)
    qc.h(0)
    qc.measure(0, 0)
    qc.reset(0)
    assert False, "Injected runtime mutation"
    return qc


def main():
    return build_circuit().count_ops()


if __name__ == "__main__":
    print(main())
