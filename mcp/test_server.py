from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

TEST_TOKEN = "test_token_123"

security = HTTPBearer(auto_error=False) # Allow manual handling of missing token

class TestDataModel(BaseModel):
    some_value: str

async def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)): # Made credentials Optional
    """Dependency to verify the authentication token."""
    if credentials is None: # Check if token is missing
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if credentials.scheme != "Bearer" or credentials.credentials != TEST_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired token",
        )
    return credentials.credentials

@app.get("/test_data")
async def get_test_data(token: str = Depends(verify_token)):
    """Returns test data if authenticated."""
    return {"message": "Hello from test data!", "user_token": token}

@app.post("/submit_data")
async def submit_data(data: TestDataModel, token: str = Depends(verify_token)):
    """Accepts and returns submitted data if authenticated."""
    return {"message": "Data submitted successfully!", "received_data": data.dict()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
