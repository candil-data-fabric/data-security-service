# Data Security Service

This project is a FastAPI application that allows users to manage policies using the OPA (Open Policy Agent) client. It provides functionality to register, update, delete, and retrieve policies, including the option to download policies as .rego files.

## Features

- Register policies from .rego files via a POST request.
- Retrieve a policy's Rego content via a GET request, with an option to download it as a .rego file.
- List all registered policies.
- Update existing policies without needing to delete and re-upload them.
- Delete policies using a DELETE request.
- Built with FastAPI and OPA Client.

### Environmental variables

These are the environmental variables that can be configured:

|  **Variable**  |                            **Description**                           |
|:--------------:|:--------------------------------------------------------------------:|
| `OPA_HOSTNAME` |       Hostname where the OPA service is running and reachable.       |
|   `OPA_PORT`   | Port number (String) where the OPA service is running and reachable. |

When installing the Helm Chart, upgrade it with a custom `myvalues.yaml` file where you define the environmental variables that you wish to override.

## Installation

### Prerequisites

- Python 3.10 or higher
- Poetry for dependency management
- Docker (optional, if you want to run the app in a container)

### Setup

1. Clone the repository:

   ```bash
   git clone <your-gitlab-repo-url>
   cd <your-repo-name>

2. Install dependencies using Poetry:

   ```bash
    poetry install

3. Run the application:

   ```bash
    poetry run uvicorn datasecurity.main:app --reload

The application will be available at http://127.0.0.1:8001

### Docker Setup (Optional)
You can also run the application in a Docker container:

1. Build the Docker image:

   ```bash
    docker build -t data_security_service .

2. Run the container:

   ```bash
    docker run -d -p 8001:8001 data_security_service

## Usage

### List policies
To get a list of all registered policies, send a GET request.

**Endpoint:** `GET /policies`

### Get Policy Content
Retrieve the content of a specific policy. Optionally, download it as a .rego file by setting the as_file parameter to true.

**Endpoint:** `GET /policies/{policy_name}/?as_file={true|false}`

### Register a Policy
You can register a new policy by sending a POST request with the `.rego` file as form data.

**Endpoint:** `POST /policies/{policy_name}`

### Update a Policy
You can update an existing policy by uploading a new .rego file with the same policy name.

**Endpoint:** `PUT /policies/{policy_name}`

### Delete a Policy
To delete a policy, send a DELETE request with the policy name.

**Endpoint:** `DELETE /{policy_name}`


## Documentation
You can consult the automatically generated API documentation at:

- Swagger UI: http://127.0.0.1:8001/docs
- ReDoc: http://127.0.0.1:8001/redoc

## Acknowledgements

This work was partially supported by the following projects:

- **UNICO 5G I+D 6G-DATADRIVEN**: Redes de próxima generación (B5G y 6G) impulsadas por datos para la fabricación sostenible y la respuesta a emergencias. Ministerio de Asuntos Económicos y Transformación Digital. European Union NextGenerationEU.

![UNICO](./images/ack-logo.png)
