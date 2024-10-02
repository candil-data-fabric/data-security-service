__name__ = "Data Security Service"
__version__ = "1.0.0"

import logging
import sys

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from opa_client.opa import OpaClient 
import requests
import uvicorn
import os

# Initialize FastAPI app
app = FastAPI()

# Initialize OPA client, assuming OPA is running at http://localhost:8181
opa_client = OpaClient()

OPA_URL = "http://localhost:8181/v1/policies/"

@app.get("/policies")
def get_policies():
    """
    Retrieves the list of registered policies.
    """
    try:
        policies = opa_client.get_policies_list()
        return {"policies": policies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/policies/{policy_name}")
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


@app.post("/policies/{policy_name}")
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

@app.put("/policies/{policy_name}")
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


@app.delete("/policies/{policy_name}")
async def delete_policy(policy_name: str):

    success = opa_client.delete_opa_policy(policy_name)
    
    if success:
        return {"message": f"Policy '{policy_name}' deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Policy '{policy_name}' not found")



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
