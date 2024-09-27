__name__ = "Data Security"
__version__ = "1.0.0"

import logging
import os
import sys

from fastapi import FastAPI, HTTPException, File, UploadFile
from opa_client.opa import OpaClient  # Import the OPA client library
import uvicorn
import os

# Initialize FastAPI app
app = FastAPI()

# Initialize OPA client, assuming OPA is running at http://localhost:8181
opa_client = OpaClient()


@app.get("/")
def read_root():
    return {"message": "Welcome to the Data Security"}


@app.post("/policies/")
async def register_policy(file: UploadFile = File(...)):
    """
    Registers a policy in OPA from an uploaded Rego file.
    """
    try:
        # Read the contents of the uploaded file
        contents = await file.read()
        # Write contents to a temporary file
        with open(file.filename, "wb") as f:
            f.write(contents)

        # Update the policy in OPA from the uploaded Rego file
        response = opa_client.update_opa_policy_fromfile(file.filename, endpoint="aerOS")
        
        # Clean up the temporary file
        os.remove(file.filename)

        if response:
            return {"message": "Policy successfully registered", "registered_policy": "aerOS"}
        else:
            raise HTTPException(status_code=500, detail="Failed to register policy.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/policies/")
def get_policies():
    """
    Retrieves the list of registered policies.
    """
    try:
        policies = opa_client.get_policies_list()
        return {"policies": policies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/policies/{policy_name}")
async def delete_policy(policy_name: str):
    # Use the client to delete the policy; adjust this according to your OPA client implementation
    success = opa_client.delete_opa_policy(policy_name)
    
    if success:
        return {"message": f"Policy '{policy_name}' deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Policy '{policy_name}' not found")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8007)
