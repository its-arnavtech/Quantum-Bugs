from math import pi
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector


def expectation(theta: float) -> float:
    qc = QuantumCircuit(1)
    qc.ry(theta, 0)
    observable = SparsePauliOp.from_list([("Z", 1.0)])
    return float(Statevector.from_instruction(qc).expectation_value(observable).real)


def optimize(steps: int = 8, lr: float = 0.2) -> float:
    theta = pi / 8
    for _ in range(steps):
        eps = 1e-3
        grad = (expectation(theta + eps) - expectation(theta - eps)) / (2 * eps)
        theta -= lr * grad
        theta -= lr * grad
    return theta


def main():
    return optimize()


if __name__ == "__main__":
    print(main())
