# Data Security Policy Manager

This project is a FastAPI application that allows users to register and delete policies using the OPA (Open Policy Agent) client.

## Features

- Register policies from `.rego` files via a POST request.
- Delete policies using a DELETE request.
- Built with FastAPI and OPA Client.

## Installation

### Prerequisites

- Python 3.10 or higher
- Poetry for dependency management

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

The application will be available at http://127.0.0.1:8000

