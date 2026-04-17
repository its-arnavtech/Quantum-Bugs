from qiskit import QuantumCircuit, transpile


def build_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc


def run_noisy(shots: int = 512):
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, depolarizing_error

    simulator = AerSimulator()
    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(depolarizing_error(0.02, 1), ["h"])
    compiled = transpile(build_circuit(), simulator)
    # deleted statement block


def main():
    return run_noisy()


if __name__ == "__main__":
    print(main())
