from landscapes import *
from metrics import *
from qnns.qnn import *
from expressibility import *
# from entanglement import *

from circuit import CircuitDescriptor

import qiskit.qasm3
from qiskit.circuit import Parameter
from subprocess import Popen, PIPE


#from qiskit_aer.noise import NoiseModel as qiskitNoiseModel
import qiskit_aer.noise as qiskitNoiseModel
from qiskit import QuantumCircuit

from flask import Flask
from flask_smorest import Api
from flask_smorest import Blueprint
import marshmallow as ma


app = Flask(__name__)

app.config.update(
    API_TITLE = "QML Toolbox",
    API_VERSION = "0.1",
    OPENAPI_VERSION = "3.0.2",
    OPENAPI_URL_PREFIX = "/api",
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui",
    OPENAPI_SWAGGER_UI_VERSION = "3.24.2",
    OPENAPI_SWAGGER_UI_URL = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.24.2/",

    API_SPEC_OPTIONS = {
        "info": {
            "description": "Toolbox for QML developement",
        },
        #"license": {"name": "Apache v2 License"},
    }
)

api = Api(app)


@app.route("/")
def heartbeat():
    return '<h1>QML-Toolbox</h1> <h3>View the API Docs <a href="/api/swagger-ui">here</a></h3>'


class MetricsRequestSchema(ma.Schema):
    num_qubits = ma.fields.Int()
    num_layers = ma.fields.Int()
    schmidt_rank = ma.fields.Int()
    num_data_points = ma.fields.Int()
    grid_size = ma.fields.Int()

class MetricsResponseSchema(ma.Schema):
    total_variation = ma.fields.Float()
    fourier_density = ma.fields.Float()
    inverse_standard_gradient_deviation = ma.fields.List(ma.fields.Float())
    scalar_curvature = ma.fields.String() #Datentyp anpassen


blp_metrics = Blueprint(
    "metrics",
    __name__,
    "calculates the metrics"
)
@blp_metrics.route("/metrics", methods=["POST"])
@blp_metrics.arguments(
    MetricsRequestSchema,
    example=dict(
        num_qubits=1,
        num_layers=1,
        schmidt_rank=2,
        num_data_points=3,
        grid_size=3,
    ),
)
@blp_metrics.response(200, MetricsResponseSchema)
def calculate_metrics(inputs: dict):
    print(inputs)
    check_metric_inputs(inputs)
    landscape = get_loss_landscape(inputs["num_qubits"], inputs["num_layers"], inputs["schmidt_rank"], inputs["num_data_points"], inputs["grid_size"])
    outputs ={"total_variation": calc_total_variation(landscape),
            "fourier_density": calc_fourier_density(landscape),
            "inverse_standard_gradient_deviation": calc_IGSD(landscape),
            "scalar_curvature": str(calc_scalar_curvature(landscape))
    }
    return outputs


@blp_metrics.route("/calculate_total_variation", methods=["POST"])
@blp_metrics.arguments(
    MetricsRequestSchema,
    example=dict(
        num_qubits=1,
        num_layers=1,
        schmidt_rank=2,
        num_data_points=3,
        grid_size=3,
    ),
)
@blp_metrics.response(200, MetricsResponseSchema)
def calculate_total_variation(inputs: dict):
    check_metric_inputs(inputs)
    landscape = get_loss_landscape(inputs["num_qubits"], inputs["num_layers"], inputs["schmidt_rank"], inputs["num_data_points"], inputs["grid_size"])
    return {"total_variation": calc_total_variation(landscape)}


@blp_metrics.route("/fourier_density", methods=["POST"])
@blp_metrics.arguments(
    MetricsRequestSchema,
    example=dict(
        num_qubits=1,
        num_layers=1,
        schmidt_rank=2,
        num_data_points=3,
        grid_size=3,
    ),
)
@blp_metrics.response(200, MetricsResponseSchema)
def calculate_fourier_density(inputs: dict):
    check_metric_inputs(inputs)
    landscape = get_loss_landscape(inputs["num_qubits"], inputs["num_layers"], inputs["schmidt_rank"], inputs["num_data_points"], inputs["grid_size"])
    return {"fourier_density": calc_fourier_density(landscape)}


@blp_metrics.route("/inverse_standard_gradient_deviation", methods=["POST"])
@blp_metrics.arguments(
    MetricsRequestSchema,
    example=dict(
        num_qubits=1,
        num_layers=1,
        schmidt_rank=2,
        num_data_points=3,
        grid_size=3,
    ),
)
@blp_metrics.response(200, MetricsResponseSchema)
def calculate_inverse_standard_gradient_deviation(inputs: dict):
    check_metric_inputs(inputs)
    landscape = get_loss_landscape(inputs["num_qubits"], inputs["num_layers"], inputs["schmidt_rank"], inputs["num_data_points"], inputs["grid_size"])
    return {"inverse_standard_gradient_deviation": calc_IGSD(landscape).tolist()}


@blp_metrics.route("/scalar_curvature", methods=["POST"])
@blp_metrics.arguments(
    MetricsRequestSchema,
    example=dict(
        num_qubits=1,
        num_layers=1,
        schmidt_rank=2,
        num_data_points=3,
        grid_size=3,
    ),
)
@blp_metrics.response(200, MetricsResponseSchema)
def calculate_scalar_curvature(inputs: dict):
    check_metric_inputs(inputs)
    landscape = get_loss_landscape(inputs["num_qubits"], inputs["num_layers"], inputs["schmidt_rank"], inputs["num_data_points"], inputs["grid_size"])
    return {"scalar_curvature": str(calc_scalar_curvature(landscape).tolist())}


blp_characteristics = Blueprint(
    "ansatz_characteristics",
    __name__,
    "calculates the ansatz_characteristics"
)


class EntanglementCapabilityRequestSchema(ma.Schema):
    qasm = ma.fields.String()
    measure = ma.fields.String()
    shots = ma.fields.Int()


class EntanglementCapabilityResponseSchema(ma.Schema):
    entanglement_capability = ma.fields.Float()

@blp_characteristics.route("/entanglement_capability", methods=["POST"])
@blp_characteristics.arguments(
    EntanglementCapabilityRequestSchema,
    example=dict(
        qasm='''OPENQASM 3;include "stdgates.inc";input float[64] a;input float[64] a1;input float[64] b;input float[64] b1;input float[64] c;qubit[4] _all_qubits;let q = _all_qubits[0:3];u3(a, b, c) q[0];cx q[0], q[1];cx q[1], q[2];cx q[2], q[3];u3(c, a1, b1) q[3];cx q[3], q[0];cx q[1], q[3];u3(b1, a1, c) q[2];''',
        measure='''scott''',
        shots = 1024


    ),
)
@blp_characteristics.response(200, EntanglementCapabilityResponseSchema)
def calculate_entanglement_capability(inputs: dict):
    
    #cricuit = CircuitDescriptor.from_qasm(inputs["qasm"],[],None,"qiskit")

    qcircuit = QuantumCircuit(2)
    phi = Parameter('phi')

    qcircuit.rx(phi, 0)

    noise_model = qiskitNoiseModel.NoiseModel()

    cricuit = CircuitDescriptor(qcircuit,[phi],None)

    entagle_calc = EntanglementCapability(cricuit, noise_model)
    return {"entanglement_capability": entagle_calc.entanglement_capability(inputs["measure"], inputs["shots"])}



class ExpressibilityRequestSchema(ma.Schema):
    num_tries = ma.fields.Int()
    num_bins = ma.fields.Int()
    num_qubits = ma.fields.Int()


class ExpressibilityResponseSchema(ma.Schema):
    expressibility = ma.fields.Float()

@blp_characteristics.route("/expressibility", methods=["POST"])
@blp_characteristics.arguments(
    ExpressibilityRequestSchema,
    example=dict(
        num_tries = 1000,
        num_bins = 50,
        num_qubits = 2
    ),
)
@blp_characteristics.response(200, ExpressibilityResponseSchema)
def calculate_expressibility(inputs:dict):
    check_expressibility_inputs(inputs)
    return {"expressibility": expressibility(inputs["num_tries"] , inputs["num_bins"], inputs["num_qubits"])}


blp_zx_calculus = Blueprint(
    "zx-calculus",
    __name__,
    "calculates ZX-Calculus"
)

class ZXCalculusRequestSchema(ma.Schema):
    ansatz = ma.fields.String()
    num_qubits = ma.fields.Int()
    num_layers = ma.fields.Int()
    hamiltonian = ma.fields.String()
    parameter = ma.fields.Int()


class ZXCalculusResponseSchema(ma.Schema):
    zx_calculus = ma.fields.String()


@blp_zx_calculus.route("/zx-calculus", methods=["POST"])
@blp_zx_calculus.arguments(
    ZXCalculusRequestSchema,
    example=dict(
        ansatz='sim1',
        num_qubits=2,
        num_layers=1,
        hamiltonian='ZZ',
        parameter=0,
    ),
)
@blp_zx_calculus.response(200, ZXCalculusResponseSchema)
def zx_calculus(inputs: dict):
    check_zx_calculus_inputs(inputs)
    binary_path = 'zx-calculus/target/release/bpdetect'
    ansatz = inputs["ansatz"]
    num_qubits = inputs["num_qubits"]
    num_layers = inputs["num_layers"]
    hamiltonian = inputs["hamiltonian"]
    parameter = inputs["parameter"]
    p = Popen([binary_path, ansatz, str(num_qubits), str(num_layers), hamiltonian, str(parameter)], stdout=PIPE, stderr=PIPE)

    variance, _ = p.communicate()

    if p.returncode != 0:
        print(_.decode('ASCII').strip())
        return {"zx_calculus": _.decode('ASCII').strip()}
    else:
        variance = variance.decode('ASCII').rstrip()
        s = f"{ansatz}-{num_qubits}-{num_layers}-{hamiltonian}-{parameter}: {variance}"
        print(s)
        return {"zx_calculus": s}


def get_loss_landscape(num_qubits, num_layers, schmidt_rank, num_data_points, grid_size):
    qnn = get_qnn("CudaU2", list(range(num_qubits)), num_layers, device="cpu")
    unitary = torch.tensor(data=np.array(random_unitary_matrix(num_qubits)), dtype=torch.complex128, device="cpu")
    inputs = generate_data_points(type_of_data=1, schmidt_rank=schmidt_rank, num_data_points=num_data_points, U=unitary, num_qubits=num_qubits)
    dimensions = num_qubits * num_layers * 3
    loss_landscape = generate_loss_landscape(grid_size=grid_size, dimensions=dimensions, inputs=inputs, U=unitary, qnn=qnn)
    return loss_landscape


class InvalidInputError(Exception):
    pass

@app.errorhandler(InvalidInputError)
def handle_invalid_input(error):
    response = {"error": str(error)}
    return response, 400


def check_metric_inputs(inputs):
    if inputs["num_qubits"] < 1:
        raise InvalidInputError("The number of qubits (num_qubits) must be at least 1.")
    elif inputs["num_layers"] < 1:
        raise InvalidInputError("The number of layers (num_layers) must be at least 1.")
    elif inputs["schmidt_rank"] < 1:
        raise InvalidInputError("The Schmidt rank (schmidt_rank) must be at least 1.")
    elif inputs["schmidt_rank"] > 2**inputs["num_qubits"]:
        raise InvalidInputError("The Schmidt rank (schmidt_rank) has to be equal or less than 2^num_qubits.")
    elif inputs["num_data_points"] < 1:
        raise InvalidInputError("The number of data points (num_data_points) must be at least 1.")
    elif inputs["grid_size"] < 1:
        raise InvalidInputError("The grid size (grid_size) must be at least 1.")


def check_entanglement_capability_inputs(inputs):
    if inputs["shots"] < 1:
        raise InvalidInputError("The number of shots (shots) must be at least 1.")


def check_expressibility_inputs(inputs):
    if inputs["num_tries"] < 1:
        raise InvalidInputError("The number of tries (num_tries) must be at least 1.")
    elif inputs["num_bins"] < 1:
        raise InvalidInputError("The number of bins (num_bins) must be at least 1.")
    elif inputs["num_qubits"] < 1:
        raise InvalidInputError("The number of qubits (num_qubits) must be at least 1.")


def check_zx_calculus_inputs(inputs):
    if inputs["num_qubits"] < 1:
        raise InvalidInputError("The number of qubits (num_qubits) must be at least 1.")
    elif inputs["num_layers"] < 1:
        raise InvalidInputError("The number of layers (num_layers) must be at least 1.")
    elif inputs["parameter"] < 0:
        raise InvalidInputError("The parameter (parameter) must be at least 0.")


def test_qnn_generation():
    for num_qubits in range(1, 10):
        for num_layers in range(1,10):
            qnn = get_qnn("CudaU2", list(range(num_qubits)), num_layers, device="cpu")
            print(qnn.params)


def test_input_generation():
    # schmidt_rank <= 2^(num_qubits)
    for num_qubits in range(1, 6):
        for s_rank in range(1, 2**num_qubits+1):
            unitary = torch.tensor(data=np.array(random_unitary_matrix(num_qubits)), dtype=torch.complex128, device="cpu")
            inputs = generate_data_points(type_of_data=1, schmidt_rank=4, num_data_points=100, U = unitary, num_qubits=6)
            print(inputs.shape)


def test_loss_landscape_calculation():
    for num_qubits in range (1, 4):
        num_layers = 1
        qnn = get_qnn("CudaU2", list(range(num_qubits)), num_layers, device="cpu")
        unitary = torch.tensor(data=np.array(random_unitary_matrix(num_qubits)), dtype=torch.complex128, device="cpu")
        inputs = generate_data_points(type_of_data=1, schmidt_rank=2, num_data_points=3, U=unitary, num_qubits=num_qubits)
        dimensions = num_qubits * num_layers * 3
        loss_landscape = generate_loss_landscape(grid_size=3, dimensions=dimensions, inputs=inputs, U=unitary, qnn=qnn)
        print(loss_landscape)


def test_api():
    with app.test_client() as client:
        inputs = {
            "num_qubits": 1,
            "num_layers": 1,
            "schmidt_rank": 2,
            "num_data_points": 3,
            "grid_size": 3
        }
        response = client.post("/calculate_total_variation", json=inputs)

        print("Status Code:", response.status_code)
        print("Response JSON:", response.get_json())


api.register_blueprint(blp_metrics)
api.register_blueprint(blp_characteristics)
api.register_blueprint(blp_zx_calculus)


if __name__ == "__main__":
    # test_qnn_generation()
    # test_input_generation()
    # test_loss_landscape_calculation()
    # test_api()
    # zx_calculus(ansatz='sim1', qubits=2, layers=1, hamiltonian='ZZ', parameter=0)

    # print("Starting Server")

    app.run(host="0.0.0.0", port=8000)