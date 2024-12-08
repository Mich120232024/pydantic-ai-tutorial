# createnewdualcontainer.py

import os
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from gremlin_python.driver import client, serializer
from gremlin_python.driver.protocol import GremlinServerError
from dotenv import load_dotenv
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

# Load environment variables from .env file
load_dotenv()

class DualContainerCreator:
    def __init__(self):
        # Debug: Check if environment variables are loaded
        cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
        cosmos_key = os.getenv("COSMOS_KEY")
        print(Fore.YELLOW + f"COSMOS_ENDPOINT: {cosmos_endpoint}")
        print(Fore.YELLOW + f"COSMOS_KEY is set: {bool(cosmos_key)}")

        # Initialize Cosmos client for SQL API
        self.cosmos_client = CosmosClient(
            cosmos_endpoint,
            credential=cosmos_key
        )

        # Database and container names for SQL API
        self.database_name_sql = os.getenv("DATABASE_NAME")
        self.container_name_sql = os.getenv("CONTAINER_NAME")

        # Create SQL database if it does not exist
        try:
            self.database_sql = self.cosmos_client.create_database_if_not_exists(id=self.database_name_sql)
            print(Fore.GREEN + f"SQL Database '{self.database_name_sql}' is ready.")
        except exceptions.CosmosHttpResponseError as e:
            print(Fore.RED + f"Error creating SQL database: {e.message}")

        # Create SQL container if it does not exist
        try:
            self.container_sql = self.database_sql.create_container_if_not_exists(
                id=self.container_name_sql,
                partition_key=PartitionKey(path="/id"),
                offer_throughput=400
            )
            print(Fore.GREEN + f"SQL Container '{self.container_name_sql}' is ready.")
        except exceptions.CosmosHttpResponseError as e:
            print(Fore.RED + f"Error creating SQL container: {e.message}")

        # Initialize Gremlin client for Graph API
        gremlin_endpoint = os.getenv("GREMLIN_ENDPOINT")
        gremlin_key = os.getenv("GREMLIN_KEY")
        print(Fore.YELLOW + f"GREMLIN_ENDPOINT: {gremlin_endpoint}")
        print(Fore.YELLOW + f"GREMLIN_KEY is set: {bool(gremlin_key)}")

        self.gremlin_client = client.Client(
            gremlin_endpoint,
            'g',
            username=f"/dbs/{os.getenv('GREMLIN_DATABASE')}/colls/{os.getenv('GREMLIN_COLLECTION')}",
            password=gremlin_key,
            message_serializer=serializer.GraphSONSerializersV2d0()
        )

        # Gremlin database and graph names
        self.database_name_gremlin = os.getenv("GREMLIN_DATABASE")
        self.graph_name_gremlin = os.getenv("GREMLIN_COLLECTION")

        # Create Gremlin graph
        self.create_gremlin_graph()

    def create_gremlin_graph(self):
        try:
            # Typically, Gremlin graphs are created via Azure Portal or specific API calls.
            # Here, we'll assume the graph exists.
            print(Fore.GREEN + f"Gremlin Graph '{self.graph_name_gremlin}' is ready.")
        except Exception as e:
            print(Fore.RED + f"Error setting up Gremlin graph: {e}")

    def add_api_registry_item(self, api_item):
        try:
            self.container_sql.create_item(body=api_item)
            print(Fore.GREEN + f"API Registry Item '{api_item['id']}' created successfully.")
            self.add_api_vertex(api_item)
        except exceptions.CosmosHttpResponseError as e:
            print(Fore.RED + f"Error creating API Registry item: {e.message}")

    def add_api_vertex(self, api_item):
        try:
            script = (
                f"g.addV('API')"
                f".property('api_id', '{api_item['id']}')"
                f".property('name', '{api_item['name']}')"
                f".property('type', '{api_item['type']}')"
                f".property('version', '{api_item['specification']['version']}')"
                f".property('status', 'active')"
            )
            self.gremlin_client.submitAsync(script).result()
            print(Fore.GREEN + f"API Vertex '{api_item['id']}' added successfully.")
        except GremlinServerError as e:
            print(Fore.RED + f"Error adding API vertex: {e}")

    def close_connections(self):
        self.gremlin_client.close()

if __name__ == "__main__":
    creator = DualContainerCreator()

    # Example API Registry Item
    api_item = {
        "id": "api-12345",
        "type": "api_registry",
        "name": "Payment Processing API",
        "source": {
            "discoveryUrl": "https://api.example.com",
            "discoveredAt": "2024-12-08T10:30:00Z",
            "lastUpdated": "2024-12-08T10:30:00Z"
        },
        "specification": {
            "type": "REST",
            "version": "1.0",
            "format": "OpenAPI",
            "documentation": "https://docs.example.com/payment-api",
            "specificationHash": "abc123hash"
        },
        "capabilities": {
            "features": ["payment_processing", "refunds", "disputes"],
            "supportedFormats": ["JSON", "XML"],
            "authMethods": ["OAuth2", "API Key"],
            "sla": "99.99%"
        },
        "techStack": {
            "languages": ["Python", "Java", "Node.js"],
            "frameworks": ["Django", "Spring", "Express"],
            "dependencies": [
                {
                    "name": "stripe-python",
                    "version": "^5.0.0",
                    "purpose": "Payment processing"
                }
            ]
        },
        "usage": {
            "complexityScore": 0.75,
            "popularityRank": 85,
            "communitySize": 15000,
            "avgImplementationTime": "3 days"
        },
        "analysis": {
            "securityScore": 0.9,
            "reliabilityScore": 0.95,
            "maintainabilityScore": 0.85,
            "learningCurve": "moderate"
        },
        "relationshipIds": [
            "feature-1", "feature-2"
        ]
    }

    # Add API Registry Item and corresponding Gremlin Vertex
    creator.add_api_registry_item(api_item)

    # Close connections
    creator.close_connections()