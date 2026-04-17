from qiskit import QuantumCircuit
from qiskit.circuit import Parameter


THETA = Parameter("theta")
PHI = Parameter("phi")


def build_template() -> QuantumCircuit:
    qc = QuantumCircuit(2)
    qc.ry(THETA, 0)
    qc.rz(PHI, 1)
    qc.cx(0, 1)
    return qc


def bind_values(theta: float, phi: float) -> QuantumCircuit:
    assert False, "Injected runtime mutation"


def main():
    return bind_values(0.2, 0.3).count_ops()


if __name__ == "__main__":
    print(main())
