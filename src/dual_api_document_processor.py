"""
Dual API Document Processor for Advanced Decision Engine
"""

import os
import asyncio
from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient, PartitionKey
from gremlin_python.driver import client, serializer
from colorama import Fore, init
from dotenv import load_dotenv
import sys

# Initialize colorama for colored output
init()

# Load environment variables from .env file
load_dotenv()

class DocumentProcessor:
    def __init__(self):
        # Managed Identity Credential
        self.credential = DefaultAzureCredential()

        # Debug and print token details and managed identity client ID
        try:
            token = self.credential.get_token("https://management.azure.com/.default")
            print(Fore.BLUE + f"Using Managed Identity: {token.token}")
            print(Fore.BLUE + f"Token Expires On: {token.expires_on}")
        except Exception as e:
            print(Fore.RED + f"Error acquiring token: {e}")

        # Connecting to Cosmos DB
        try:
            self.cosmos_client = CosmosClient(
                url=os.getenv("COSMOS_ENDPOINT"),
                credential=self.credential
            )
            self.database_name = os.getenv('DATABASE_NAME')
            self.container_name = os.getenv('CONTAINER_NAME')
            self.database = self.cosmos_client.get_database_client(self.database_name)
            self.container = self.database.get_container_client(self.container_name)
            print(Fore.GREEN + f"Successfully connected to Cosmos DB: {self.container_name}")
        except Exception as e:
            print(Fore.RED + f"Error connecting to Cosmos DB: {e}")
            sys.exit(1)

        # Connecting to Gremlin Client
        try:
            self.gremlin_endpoint = os.getenv("GREMLIN_ENDPOINT")
            self.gremlin_auth_uri = os.getenv("GREMLIN_AUTH_URI")
            self.gremlin_database = os.getenv("GREMLIN_DATABASE")
            self.gremlin_collection = os.getenv("GREMLIN_COLLECTION")

            self.gremlin_client = client.Client(
                self.gremlin_endpoint,
                "g",
                username=f"/dbs/{self.gremlin_database}/colls/{self.gremlin_collection}",
                password=self._get_gremlin_password(),
                message_serializer=serializer.GraphSONMessageSerializer()
            )
            print(Fore.GREEN + "Successfully connected to Gremlin API")
        except Exception as e:
            print(Fore.RED + f"Error connecting to Gremlin API: {e}")
            sys.exit(1)

    def _get_gremlin_password(self):
        # Use managed identity to acquire the token for the Gremlin API
        token = self.credential.get_token(self.gremlin_auth_uri).token
        return f"Bearer {token}"

    async def process_documents(self):
        try:
            # Create a container if it does not exist
            container = self.database.create_container_if_not_exists(
                id=self.container_name,
                partition_key=PartitionKey(path=os.getenv("PARTITION_KEY"))
            )
            print(Fore.GREEN + f"Container created or already exists: {self.container_name}")
        except Exception as e:
            print(Fore.RED + f"Error creating container: {e}")
            sys.exit(1)

        try:
            # Load documents from Cosmos DB
            query = "SELECT * FROM c"
            documents = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            print(Fore.BLUE + f"Processing {len(documents)} documents...")
        except Exception as e:
            print(Fore.RED + f"Error querying documents: {e}")
            sys.exit(1)

        # Process each document
        for document in documents:
            self.process_gremlin(document)

    def process_gremlin(self, document):
        # Interaction with Gremlin API
        gremlin_queries = [
            ("g.addV('person').property('id', '{id}').property('name', '{name}')"
             ".property('age', {age}).property('pk', '{pk}')"
            ).format(**document)
        ]
        for query in gremlin_queries:
            callback = self.gremlin_client.submitAsync(query)
            if callback.result() is not None:
                print(Fore.GREEN + f"Result: {callback.result().all().result()}")
            else:
                print(Fore.RED + "Query failed to execute")

        # Sample additional Gremlin query
        gremlin_query = "g.V().has('pk', 'value')"
        result = self.gremlin_client.submit(gremlin_query).all().result()
        print(Fore.GREEN + f"Gremlin query result: {result}")

    def run(self):
        asyncio.run(self.process_documents())

if __name__ == "__main__":
    processor = DocumentProcessor()
    processor.run()