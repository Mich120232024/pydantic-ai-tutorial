"""
Introduction to PydanticAI with Azure AI Projects and Cosmos DB NoSQL storage.
"""

import os
import openai
import nest_asyncio
from typing import Dict, List, Optional
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.cosmos import CosmosClient
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelRetry, RunContext, Tool
from pydantic_ai.models.openai import OpenAIModel

# Enable nested event loops
nest_asyncio.apply()

# Load environment variables
load_dotenv()

try:
    # Initialize Cosmos DB client
    cosmos_client = CosmosClient(
        url=os.getenv("COSMOS_ENDPOINT"),
        credential=str(os.getenv("COSMOS_KEY"))
    )

    database = cosmos_client.get_database_client(os.getenv("DATABASE_NAME"))
    container = database.get_container_client(os.getenv("CONTAINER_NAME"))
    
    print("Successfully connected to Cosmos DB")

    # Configure OpenAI for Azure
    openai.api_type = "azure"
    openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
    openai.api_version = "2023-05-15"
    openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")

    # PydanticAI model setup with Azure configuration
    model = OpenAIModel(
        "gpt-4o",  # Using deployment ID directly
        api_key=openai.api_key
    )

    class ResponseModel(BaseModel):
        response: str
        needs_escalation: bool
        follow_up_required: bool
        sentiment: str = Field(description="Customer sentiment analysis")

    agent = Agent(
        model=model,
        result_type=ResponseModel,
        retries=3,
        system_prompt="You are an intelligent support agent. Analyze queries and provide structured responses."
    )

    def main():
        try:
            text = "How can I track my order?"
            response = agent.run_sync(text)
            print(response.data.model_dump_json(indent=2))
        except Exception as e:
            print(f"Error during agent execution: {e}")

    if __name__ == "__main__":
        main()

except Exception as e:
    print(f"Error initializing services: {e}")
