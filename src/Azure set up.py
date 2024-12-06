"""
Azure OpenAI Integration with Cosmos DB storage.
"""

import os
import time
from typing import Dict, List, Optional
from openai import AzureOpenAI
from azure.cosmos import CosmosClient
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

try:
    # Initialize Cosmos DB client
    cosmos_client = CosmosClient(
        url=os.getenv("COSMOS_ENDPOINT"),
        credential=str(os.getenv("COSMOS_KEY"))
    )

    database = cosmos_client.get_database_client("GroundZeroDB")
    container = database.get_container_client("GZC_IDE")
    
    print("Successfully connected to Cosmos DB")

    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2023-05-15",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    class ResponseModel(BaseModel):
        response: str
        needs_escalation: bool
        follow_up_required: bool
        sentiment: str = Field(description="Customer sentiment analysis")

    class AzureAgent:
        def __init__(self, client: AzureOpenAI, deployment_id: str = "gpt-4o-cosmic", retries: int = 3):
            self.client = client
            self.deployment_id = deployment_id
            self.max_retries = retries

        def run_sync(self, text: str) -> ResponseModel:
            attempts = 0
            while attempts < self.max_retries:
                try:
                    response = self.client.chat.completions.create(
                        model=self.deployment_id,
                        messages=[
                            {"role": "system", "content": "You are an intelligent support agent. Analyze queries and provide structured responses."},
                            {"role": "user", "content": text}
                        ],
                        temperature=0.7
                    )
                    
                    content = response.choices[0].message.content
                    return ResponseModel(
                        response=content,
                        needs_escalation=False,
                        follow_up_required=False,
                        sentiment="neutral"
                    )
                except Exception as e:
                    attempts += 1
                    if "DeploymentNotFound" in str(e):
                        print(f"Deployment {self.deployment_id} not found. Attempt {attempts}/{self.max_retries}")
                        time.sleep(5)  # Wait 5 seconds before retry
                        continue
                    print(f"Error during execution: {e}")
                    if attempts == self.max_retries:
                        raise
            return None

    # Initialize agent with correct deployment ID
    agent = AzureAgent(client)

    def main():
        try:
            text = "How can I track my order?"
            response = agent.run_sync(text)
            if response:
                print(response.model_dump_json(indent=2))
        except Exception as e:
            print(f"Error during agent execution: {e}")

    if __name__ == "__main__":
        main()

except Exception as e:
    print(f"Error initializing services: {e}")