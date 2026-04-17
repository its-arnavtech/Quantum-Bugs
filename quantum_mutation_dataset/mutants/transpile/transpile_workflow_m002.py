from math import pi
from qiskit import QuantumCircuit, transpile


def build_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.rz(pi / 7, 1)
    return qc


def compile_for_backend():
    from qiskit.providers.fake_provider import GenericBackendV2

    backend = GenericBackendV2(num_qubits=2, basis_gates=["rz", "sx", "x", "cx"])
    compiled = transpile(build_circuit(), backend=backend, optimization_level=3)
    return compiled.depth()


def main():
    return compile_for_backend()


if __name__ == "__main__":
    print(main())
