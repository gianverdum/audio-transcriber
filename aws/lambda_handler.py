"""
AWS Lambda Handler
Adapts FastAPI to work on Lambda using Mangum
"""

import os
from mangum import Mangum  # type: ignore[import]
from dotenv import load_dotenv  # type: ignore[import]

# Load environment variables
load_dotenv()

# Import the FastAPI application
from audio_transcriber.api.main import app  # type: ignore[import-untyped]

# Create Lambda handler
lambda_handler = Mangum(app, lifespan="off")

# For local testing
if __name__ == "__main__":
    # Simulate Lambda event for testing
    event = {
        "httpMethod": "GET",
        "path": "/health",
        "headers": {},
        "body": None
    }
    context = {}
    
    result = lambda_handler(event, context)
    print(result)
