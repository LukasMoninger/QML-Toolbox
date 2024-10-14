from landscapes import *
from metrics import *
from qnns.cuda_qnn import *
from qnns.qnn import *


def calculate_metrics(landscape):
    scalar_curvature = calc_scalar_curvature(landscape)
    print("Scalar Curvature: " + str(scalar_curvature))

    total_variation = calc_total_variation(landscape)
    print("Total Variation: " + str(total_variation))

    fourier_density = calc_fourier_density(landscape)
    print("Fourier Density: " + str(fourier_density))

    inverse_standard_gradient_deviation = calc_IGSD(landscape)
    print("Inverse Standard Gradient Deviation: " + str(inverse_standard_gradient_deviation))


def test_one_qubit():
    '''
    Test landscape generation and metric calculation for QNNs with one qubit
    '''
    qnn = get_qnn(qnn_name="CudaU2", x_wires=[0], num_layers=1, device="cpu")
    print(f"Number of parameters: {str(len(qnn.params))}")

    U = torch.tensor(data=np.array([[1, 1], [1, -1]]) / np.sqrt(2), dtype=torch.complex128, device="cpu")

    inputs = generate_random_datapoints(numb_points=2, s_rank=1, U=U)

    loss_landscape = generate_2d_loss_landscape(grid_size=50, inputs=inputs, U=U, qnn=qnn)

    calculate_metrics(loss_landscape)


def test_two_qubits():
    '''
    Test landscape generation and metric calculation for QNNs with two qubits
    '''
    num_qubits = 2
    qnn = CudaPennylane(num_wires=num_qubits, num_layers=1, device='cpu')
    print(f"Number of parameters: {str(len(qnn.params))}")

    U = torch.tensor(data=np.array(random_unitary_matrix(num_qubits)), dtype=torch.complex128, device="cpu")

    inputs = generate_random_datapoints(numb_points=3, s_rank=num_qubits, U=U)

    loss_landscape = generate_loss_landscape(grid_size=3, dimensions=6, inputs=inputs, U=U, qnn=qnn)

    calculate_metrics(loss_landscape)


def test(qnn_type, num_qubits, num_layers, unitary):
    qnn = get_qnn("CudaU2", list(range(num_qubits)), num_layers, device="cpu")
    random_unitary = torch.tensor(np.array(random_unitary_matrix(2)), dtype=torch.complex128, device="cpu")
    inputs = generate_random_datapoints(3, num_qubits, random_unitary)

    dimensions = len(qnn.params)
    landscape = generate_loss_landscape(10, dimensions, inputs, unitary, qnn)
    calculate_metrics(landscape)


matrix = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]])
unitary = torch.tensor(matrix, dtype=torch.complex128, device="cpu")
# test("Pennylane", 2, 3, unitary)


if __name__ == "__main__":
    print("\nOne qubit:")
    test_one_qubit()

    print("\nTwo qubits:")
    test_two_qubits()