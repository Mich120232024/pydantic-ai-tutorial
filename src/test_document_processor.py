# test_document_processor.py

import asyncio
import os
import time
from dual_api_document_processor import DocumentProcessor
from colorama import init, Fore
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, AzureCliCredential, ManagedIdentityCredential, EnvironmentCredential

# Initialize colorama
init()

class DocumentProcessor:
    def __init__(self):
        # Define credentials explicitly
        self.credential = DefaultAzureCredential(logging_enable=True)

        # Debug: Identify which credential is used
        self.identify_credential()

    def identify_credential(self):
        credentials = [
            ("EnvironmentCredential", EnvironmentCredential()),
            ("ManagedIdentityCredential", ManagedIdentityCredential()),
            ("AzureCliCredential", AzureCliCredential())
        ]

        for cred_name, cred in credentials:
            try:
                token = cred.get_token("https://management.azure.com/.default")
                print(Fore.BLUE + f"Authenticated using {cred_name}")
                print(Fore.BLUE + f"Token: {token.token[:50]}...")
                print(Fore.BLUE + f"Token Expires On: {token.expires_on}")
                break
            except Exception as e:
                print(Fore.RED + f"{cred_name} failed: {e}")

async def verify_deployment():
    """Verify Azure OpenAI deployment exists"""
    load_dotenv()
    max_retries = 3
    retry_delay = 5

    print(f"\n{Fore.YELLOW}Verifying Azure OpenAI deployment...{Fore.RESET}")
    
    # Get deployment configuration from .env
    deployment_name = os.getenv("EMBEDDING_DEPLOYMENT_NAME")
    endpoint = os.getenv("AZURE_EMBEDDING_ENDPOINT")
    api_version = os.getenv("EMBEDDING_API_VERSION")
    
    print(f"Configuration from .env:")
    print(f"Endpoint: {endpoint}")
    print(f"Deployment: {deployment_name}")
    print(f"API Version: {api_version}")
    
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_EMBEDDING_API_KEY"),
        api_version=api_version,
        azure_endpoint=endpoint
    )

    for attempt in range(max_retries):
        try:
            response = await client.embeddings.create(
                input="test",
                deployment_id=deployment_name,
                model="text-embedding-3-large"
            )
            print(f"{Fore.GREEN}✓ Deployment verified successfully{Fore.RESET}")
            return True
        except Exception as e:
            print(f"{Fore.YELLOW}Attempt {attempt + 1}/{max_retries}:")
            print(f"Error: {str(e)}{Fore.RESET}")
            if attempt < max_retries - 1:
                print(f"Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
    
    return False

async def test_processor():
    try:
        deployment_ready = await verify_deployment()
        if not deployment_ready:
            print(f"{Fore.RED}Cannot proceed - deployment not available{Fore.RESET}")
            return

        print(f"\n{Fore.CYAN}Testing Document Processor...{Fore.RESET}")
        processor = DocumentProcessor()
        print(f"{Fore.GREEN}✓ Processor initialized{Fore.RESET}")

        test_doc = {
            "Advanced Decision Engine": {
                "Price Discovery": {
                    "Multi-Venue": {
                        "Aggregation": ["Best bid/offer", "VWAP"]
                    }
                }
            }
        }

        print(f"\n{Fore.YELLOW}Processing test document...{Fore.RESET}")
        success = await processor.process_document(test_doc)

        if success:
            print(f"{Fore.GREEN}✓ Document processed successfully{Fore.RESET}")
        else:
            print(f"{Fore.RED}× Document processing failed{Fore.RESET}")

    except Exception as e:
        print(f"{Fore.RED}Error during test: {e}{Fore.RESET}")
    finally:
        if 'processor' in locals():
            processor.close()
        print(f"\n{Fore.CYAN}Test completed{Fore.RESET}")

if __name__ == "__main__":
    asyncio.run(test_processor())

import openai
import os
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Azure OpenAI configurations for embeddings
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_EMBEDDING_ENDPOINT")
openai.api_version = os.getenv("EMBEDDING_API_VERSION")

# Authenticate using managed identity
default_credential = DefaultAzureCredential()
token = default_credential.get_token("https://cognitiveservices.azure.com/.default")
openai.api_key = token.token

# Create an embedding using the deployment name from .env
response = openai.Embedding.create(
    input="Your text input",
    engine=os.getenv("EMBEDDING_DEPLOYMENT_NAME")
)

# Print the embedding result
print(response)