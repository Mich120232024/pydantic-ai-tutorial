# dual_api_schema.py

import os
from azure.cosmos import CosmosClient, PartitionKey
from gremlin_python.driver import client, serializer
from dotenv import load_dotenv

class DualApiSchema:
    def __init__(self):
        load_dotenv()
        self.cosmos_client = CosmosClient(
            url=os.getenv("COSMOS_ENDPOINT"),
            credential=str(os.getenv("COSMOS_KEY"))
        )

    def create_dual_container(self):
        """Create container with dual API compatible schema"""
        try:
            # Create database
            database = self.cosmos_client.create_database_if_not_exists(
                id="DualApiDB"
            )

            # Define container with partition key that works for both APIs
            container_definition = {
                'id': 'DualApiContainer',
                'partitionKey': {
                    'paths': ['/pk'],  # Universal partition key
                    'kind': 'Hash'
                },
                'indexingPolicy': {
                    'indexingMode': 'consistent',
                    'includedPaths': [
                        {'path': '/*'},  # Index all paths
                        {'path': '/label/?'},  # For Gremlin vertex labels
                        {'path': '/id/?'},     # For vertex IDs
                        {'path': '/type/?'}    # For entity type
                    ]
                }
            }

            # Create container
            container = database.create_container_if_not_exists(
                id=container_definition['id'],
                partition_key=PartitionKey(path='/pk')
            )

            # Example vertex schema
            sample_vertex = {
                "id": "theme-1",
                "label": "Central_Theme",  # Gremlin label
                "type": "vertex",         # Entity type
                "pk": "central_theme",    # Partition key
                "properties": {
                    "name": "Economic Growth",
                    "category": "Macro",
                    "weight": 1.0
                }
            }

            # Example edge schema
            sample_edge = {
                "id": "relationship-1",
                "label": "INFLUENCES",    # Gremlin edge label
                "type": "edge",          # Entity type
                "pk": "relationship",    # Partition key
                "properties": {
                    "weight": 0.8,
                    "direction": "outbound"
                },
                "_fromId": "theme-1",    # Source vertex
                "_toId": "theme-2"       # Target vertex
            }

            # Insert samples
            container.upsert_item(sample_vertex)
            container.upsert_item(sample_edge)

            print("Dual API container created with schema")
            return container

        except Exception as e:
            print(f"Error creating schema: {e}")
            return None

    def validate_schema(self, container):
        """Validate schema works with both APIs"""
        try:
            # Test NoSQL query
            items = list(container.query_items(
                query="SELECT * FROM c WHERE c.type = 'vertex'",
                enable_cross_partition_query=True
            ))
            print(f"NoSQL API found {len(items)} vertices")

            # Test Gremlin query
            gremlin_client = client.Client(
                os.getenv("GREMLIN_ENDPOINT"),
                'g',
                username=f"/dbs/DualApiDB/colls/DualApiContainer",
                password=os.getenv("GREMLIN_PRIMARY_KEY"),
                message_serializer=serializer.GraphSONSerializersV2d0()
            )
            
            result = gremlin_client.submit("g.V().count()").all().result()
            print(f"Gremlin API found {result[0]} vertices")
            
            gremlin_client.close()
            return True

        except Exception as e:
            print(f"Schema validation failed: {e}")
            return False

if __name__ == "__main__":
    schema = DualApiSchema()
    container = schema.create_dual_container()
    if container:
        schema.validate_schema(container)