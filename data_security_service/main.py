__name__ = "Data Security Service"
__version__ = "1.1.0"

from fastapi import FastAPI, HTTPException, File, UploadFile, status
from fastapi.responses import FileResponse
import logging
from opa_client.opa import OpaClient
from typing import Union
import os
from pydantic import BaseModel
import requests
import sys
import uvicorn

## -- BEGIN CONSTANTS DECLARATION -- ##

### OPA SERVICE INFORMATION ###

OPA_HOSTNAME = os.getenv("OPA_HOSTNAME")
OPA_PORT = os.getenv("OPA_PORT") # String, will be casted to Integer when needed.

### --- ###

## -- END CONSTANTS DECLARATION -- ##

## -- BEGIN DEFINITION OF PYDANTIC MODELS -- ##

class GetPoliciesResponse(BaseModel):
    '''
    Model for GET /policies response.
    '''

    policies: list[str]

class GetPolicyResponse(BaseModel):
    '''
    Model for GET /policies/{policy_name} response.
    '''

    policy_name: str
    rego_content: str

class RegisterPolicyResponse(BaseModel):
    '''
    Model for POST /policies/{policy_name} response.
    '''

    registered_policy: str

class UpdatePolicyResponse(BaseModel):
    '''
    Model for PUT /policies/{policy_name} response.
    '''

    message: str

class DeletePolicyResponse(BaseModel):
    '''
    Model for DELETE /policies/{policy_name} response.
    '''

    message: str

## -- END DEFINITION OF PYDANTIC MODELS -- ##

# Initialize FastAPI app
app = FastAPI(
    title = __name__ + " - REST API",
    version = __version__
)

opa_client = OpaClient(host=OPA_HOSTNAME, port=int(OPA_PORT))

OPA_URL = "http://" + OPA_HOSTNAME + ":" + OPA_PORT + "/v1/policies/"

@app.get(
    path = "/policies",
    description = "Retrieve list of registered policies.",
    tags = ["Read"],
    responses = {
        status.HTTP_200_OK: {
            "model": GetPoliciesResponse
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": str
        }
    }
)
def get_policies():
    """
    Retrieves the list of registered policies.
    """
    try:
        policies = opa_client.get_policies_list()
        return {"policies": policies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    path = "/policies/{policy_name}",
    description = "Retrieve policy contents.",
    tags = ["Read"],
    responses = {
        status.HTTP_200_OK: {
            "model": GetPolicyResponse
        },
        status.HTTP_404_NOT_FOUND: {
            "model": str
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": str
        }
    }
)
def get_policy_content(policy_name: str, as_file: bool = False):
    """
    Retrieves the actual Rego content of a specific policy from OPA.
    """
    try:
        # Make a direct API call to OPA to retrieve the policy content
        response = requests.get(f"{OPA_URL}{policy_name}")
        if response.status_code == 200:
            # Return the policy content if found
            policy_data = response.json()
            rego_content = policy_data.get("result", {}).get("raw", "")
            if as_file:
                # Create a temporary .rego file to save the content
                file_path = f"/tmp/{policy_name}.rego"
                with open(file_path, "w") as rego_file:
                    rego_file.write(rego_content)
                # Return the file as a downloadable response
                return FileResponse(file_path, media_type="application/octet-stream", filename=f"{policy_name}.rego")
            else:
                return {"policy_name": policy_name, "rego_content": rego_content}
        elif response.status_code == 404:
            # If policy is not found, raise a 404 HTTPException
            raise HTTPException(status_code=404, detail=f"Policy '{policy_name}' not found.")
        else:
            # Handle any other errors
            raise HTTPException(status_code=500, detail="Failed to retrieve the policy content.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    path = "/policies/{policy_name}",
    description = "Register policy.",
    tags = ["Create"],
    responses = {
        status.HTTP_200_OK: {
            "model": RegisterPolicyResponse
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": str
        }
    }
)
async def register_policy(policy_name: str, file: UploadFile = File(...)):
    """
    Registers a policy in OPA from an uploaded Rego file.
    The policy name is provided as a path parameter.
    """
    try:
        # Read the contents of the uploaded file
        contents = await file.read()
        # Write contents to a temporary file
        with open(file.filename, "wb") as f:
            f.write(contents)
        # Update the policy in OPA from the uploaded Rego file
        response = opa_client.update_opa_policy_fromfile(file.filename, endpoint=policy_name)
        # Clean up the temporary file
        os.remove(file.filename)
        if response:
            return {"registered_policy": policy_name}
        else:
            raise HTTPException(status_code=500, detail="Failed to register policy.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put(
    path = "/policies/{policy_name}",
    description = "Update an existing policy.",
    tags = ["Update"],
    responses = {
        status.HTTP_200_OK: {
            "model": UpdatePolicyResponse
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": str
        }
    }
)
async def update_policy(policy_name: str, file: UploadFile = File(...)):
    """
    Updates an existing policy in OPA from an uploaded Rego file.
    The policy name is provided as a path parameter.
    """
    try:
        # Read the contents of the uploaded file
        contents = await file.read()
        # Write contents to a temporary file
        with open(file.filename, "wb") as f:
            f.write(contents)
        # Use the same method as POST to update the policy in OPA
        response = opa_client.update_opa_policy_fromfile(file.filename, endpoint=policy_name)
        # Clean up the temporary file
        os.remove(file.filename)
        if response:
            return {"message": f"Policy '{policy_name}' updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update policy.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete(
    path = "/policies/{policy_name}",
    description = "Delete policy.",
    tags = ["Delete"],
    responses = {
        status.HTTP_200_OK: {
            "model": DeletePolicyResponse
        },
        status.HTTP_404_NOT_FOUND: {
            "model": str
        }
    }
)
async def delete_policy(policy_name: str):
    success = opa_client.delete_opa_policy(policy_name)
    if success:
        return {"message": f"Policy '{policy_name}' deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Policy '{policy_name}' not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
