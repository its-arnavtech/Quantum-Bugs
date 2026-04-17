from qiskit import QuantumCircuit


def build_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc


def success_probability(counts: dict[str, int]) -> float:
    total = sum(counts.values())
    success = counts.get("01", 0) + counts.get("10", 0)
    return success / total if total else 0.0


def main():
    return success_probability({"00": 512, "11": 512})


if __name__ == "__main__":
    print(main())
