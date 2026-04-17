from qiskit import QuantumCircuit


def build_circuit(message: str = "10") -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    if message[0] == "1":
            qc.x(0)
    if message[1] == "1":
            qc.x(0)
    qc.cx(0, 1)
    qc.h(0)
    qc.measure([0, 1], [0, 1])
    return qc


def main():
    return build_circuit().count_ops()


if __name__ == "__main__":
    print(main())
