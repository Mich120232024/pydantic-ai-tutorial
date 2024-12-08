# test_dualapiconnections.py

import os
import sys
import asyncio
from colorama import init, Fore
from dotenv import load_dotenv
from azure.cosmos import CosmosClient, PartitionKey
from gremlin_python.driver import client, serializer

# Initialize colorama for Windows
init()

NOSQL_CONNECTION = {
    'endpoint': "https://cosmicdbaccount.documents.azure.com:443/",
    'database': "ProjectTechDB",
    'container': "ProjectTechContainer"
}

GREMLIN_CONNECTION = {
    'endpoint': "wss://cosmosdbgremlin.gremlin.cosmos.azure.com:443/",
    'database': "ProjectTechDB",
    'container': "ProjectTechContainer"
}

def verify_setup():
    """Verify environment setup and paths"""
    try:
        print(f"{Fore.CYAN}Starting environment verification...{Fore.RESET}")
        
        # Check Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        sys.path.append(parent_dir)
        print(f"{Fore.CYAN}Working directory: {current_dir}{Fore.RESET}")

        # Load and verify environment variables
        load_dotenv()
        
        # Verify NoSQL API connection
        try:
            cosmos_client = CosmosClient(
                url=os.getenv("COSMOS_ENDPOINT"),
                credential=str(os.getenv("COSMOS_KEY"))
            )
            database = cosmos_client.get_database_client("DualApiDB")
            container = database.get_container_client("DualApiContainer")
            print(f"{Fore.GREEN}✓ NoSQL API connection successful{Fore.RESET}")
        except Exception as e:
            print(f"{Fore.RED}× NoSQL API connection failed: {e}{Fore.RESET}")
            return False

        # Verify Gremlin API connection
        try:
            gremlin_client = client.Client(
                os.getenv("GREMLIN_ENDPOINT"),
                'g',
                username=f"/dbs/DualApiDB/colls/DualApiContainer",
                password=os.getenv("GREMLIN_PRIMARY_KEY"),
                message_serializer=serializer.GraphSONSerializersV2d0()
            )
            print(f"{Fore.GREEN}✓ Gremlin API connection successful{Fore.RESET}")
            gremlin_client.close()
        except Exception as e:
            print(f"{Fore.RED}× Gremlin API connection failed: {e}{Fore.RESET}")
            return False

        print(f"{Fore.GREEN}✓ All connections verified successfully{Fore.RESET}")
        return True

    except Exception as e:
        print(f"{Fore.RED}Setup verification failed: {e}{Fore.RESET}")
        return False

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Load environment variables
load_dotenv()

# Fix import statement
from dual_api_document_processor import DocumentProcessor

async def verify_environment():
    """Verify required environment variables"""
    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "EMBEDDING_DEPLOYMENT_NAME",
        "AZURE_API_VERSION"
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print("❌ Missing environment variables:", missing)
        return False
        
    print(f"Using deployment: {os.getenv('EMBEDDING_DEPLOYMENT_NAME')}")
    return True

async def test_connections():
    try:
        print("Starting connection tests...")
        
        # Verify environment first
        if not await verify_environment():
            return
        
        # Initialize processor
        processor = DocumentProcessor()
        
        # Simple test document
        test_doc = {
            "test_concept": {
                "child_concept": {
                    "detail": ["value1", "value2"]
                }
            }
        }
        
        # Test document processing
        print("\nTesting document processing...")
        success = await processor.process_document(test_doc)
        
        if success:
            print("✅ Test completed successfully")
        else:
            print("❌ Test failed")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
    finally:
        processor.close()
        print("\nTest completed, connections closed")

def test_dual_container_access():
    # Load environment variables
    load_dotenv()
    
    print("Testing Dual API Container Access...")
    
    try:
        # Test NoSQL API access
        cosmos_client = CosmosClient(
            url=os.getenv("COSMOS_ENDPOINT"),
            credential=str(os.getenv("COSMOS_KEY"))
        )
        
        database = cosmos_client.get_database_client("DualApiDB")
        container = database.get_container_client("DualApiContainer")
        
        # Test NoSQL write
        test_item = {
            'id': 'test_item_1',
            'pk': 'test_partition',
            'name': 'Test Item'
        }
        container.upsert_item(test_item)
        print("✅ NoSQL API write successful")
        
        # Test Gremlin API access
        gremlin_client = client.Client(
            os.getenv("GREMLIN_ENDPOINT"),
            'g',
            username=f"/dbs/DualApiDB/colls/DualApiContainer",
            password=os.getenv("GREMLIN_PRIMARY_KEY"),
            message_serializer=serializer.GraphSONSerializersV2d0()
        )
        
        # Test Gremlin query
        query = "g.V().count()"
        result = gremlin_client.submit(query).all().result()
        print(f"✅ Gremlin API query successful. Vertex count: {result[0]}")
        
        gremlin_client.close()
        print("\nDual API access test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing container access: {e}")

def test_connections():
    print(f"{Fore.CYAN}Starting connection tests...{Fore.RESET}")
    
    try:
        # Load environment variables
        load_dotenv()
        
        # Test NoSQL API
        print(f"\n{Fore.YELLOW}Testing NoSQL API connection:{Fore.RESET}")
        cosmos_client = CosmosClient(
            url=os.getenv("COSMOS_ENDPOINT"),
            credential=str(os.getenv("COSMOS_KEY"))
        )
        database = cosmos_client.get_database_client("DualApiDB")
        container = database.get_container_client("DualApiContainer")
        
        # Test container read
        items = list(container.read_all_items(max_item_count=1))
        print(f"{Fore.GREEN}✓ NoSQL connection successful{Fore.RESET}")
        print(f"Found {len(items)} items in container")

        # Test Gremlin API with enhanced queries
        print(f"\n{Fore.YELLOW}Testing Gremlin API connection:{Fore.RESET}")
        gremlin_client = client.Client(
            os.getenv("GREMLIN_ENDPOINT"),
            'g',
            username=f"/dbs/DualApiDB/colls/DualApiContainer",
            password=os.getenv("GREMLIN_PRIMARY_KEY"),
            message_serializer=serializer.GraphSONSerializersV2d0()
        )

        # Run diagnostic queries
        queries = {
            "vertex_count": "g.V().count()",
            "edge_count": "g.E().count()",
            "labels": "g.V().label().dedup()",
            "sample": "g.V().limit(1).valueMap(true)"
        }

        print(f"\n{Fore.CYAN}Running Gremlin diagnostics:{Fore.RESET}")
        for name, query in queries.items():
            result = gremlin_client.submit(query).all().result()
            print(f"{Fore.GREEN}✓ {name}: {result}{Fore.RESET}")

        gremlin_client.close()
        print(f"\n{Fore.GREEN}✓ Gremlin tests completed{Fore.RESET}")
        
    except Exception as e:
        print(f"{Fore.RED}Error during connection test: {e}{Fore.RESET}")

def test_gremlin_databases():
    print(f"\n{Fore.YELLOW}Checking Gremlin Databases:{Fore.RESET}")
    try:
        gremlin_client = client.Client(
            os.getenv("GREMLIN_ENDPOINT"),
            'g',
            username=f"/dbs/{os.getenv('GREMLIN_DATABASE')}/colls/{os.getenv('GREMLIN_COLLECTION')}",
            password=os.getenv("GREMLIN_PRIMARY_KEY"),
            message_serializer=serializer.GraphSONSerializersV2d0()
        )

        # List all vertices in macrographgremlin/macrograph1
        queries = {
            "current_db": f"g.V().count()",
            "vertices": f"g.V().label().dedup()",
            "sample": f"g.V().limit(1).valueMap(true)"
        }

        print(f"\n{Fore.CYAN}Database: {os.getenv('GREMLIN_DATABASE')}{Fore.RESET}")
        print(f"{Fore.CYAN}Collection: {os.getenv('GREMLIN_COLLECTION')}{Fore.RESET}")
        
        for name, query in queries.items():
            try:
                result = gremlin_client.submit(query).all().result()
                print(f"{Fore.GREEN}✓ {name}:{Fore.RESET}")
                print(f"  {result}")
            except Exception as query_error:
                print(f"{Fore.RED}× {name} failed: {query_error}{Fore.RESET}")

        gremlin_client.close()
        
    except Exception as e:
        print(f"{Fore.RED}Error accessing Gremlin database: {e}{Fore.RESET}")

def analyze_graph():
    print(f"{Fore.CYAN}Analyzing Graph Structure...{Fore.RESET}")
    
    try:
        load_dotenv()
        
        # Initialize Gremlin client
        gremlin_client = client.Client(
            os.getenv("GREMLIN_ENDPOINT"),
            'g',
            username=f"/dbs/{os.getenv('GREMLIN_DATABASE')}/colls/{os.getenv('GREMLIN_COLLECTION')}",
            password=os.getenv("GREMLIN_PRIMARY_KEY"),
            message_serializer=serializer.GraphSONSerializersV2d0()
        )

        # Advanced diagnostic queries
        queries = {
            "vertex_counts_by_label": "g.V().groupCount().by(label)",
            "edge_types": "g.E().label().dedup()",
            "central_themes": "g.V().hasLabel('Central_Theme').values('name').toList()",
            "theme_connections": """
                g.V().hasLabel('Central_Theme').project('theme', 'connections')
                .by('name')
                .by(both().count())
            """,
            "entity_relationships": "g.V().hasLabel('Entity').outE().label().dedup()"
        }

        print(f"\n{Fore.YELLOW}Graph Statistics:{Fore.RESET}")
        
        for name, query in queries.items():
            try:
                result = gremlin_client.submit(query).all().result()
                print(f"\n{Fore.GREEN}✓ {name}:{Fore.RESET}")
                if isinstance(result[0], dict):
                    for k, v in result[0].items():
                        print(f"  {k}: {v}")
                else:
                    print(f"  {result}")
            except Exception as query_error:
                print(f"{Fore.RED}× {name} failed: {query_error}{Fore.RESET}")

        gremlin_client.close()
        print(f"\n{Fore.GREEN}Analysis completed successfully{Fore.RESET}")
        
    except Exception as e:
        print(f"{Fore.RED}Error during analysis: {e}{Fore.RESET}")

def test_dual_api_access():
    """Test actual connections to both APIs"""
    try:
        load_dotenv()
        print(f"\n{Fore.YELLOW}Testing Dual API Access:{Fore.RESET}")

        # Test NoSQL Connection
        print(f"\n{Fore.CYAN}Testing NoSQL API:{Fore.RESET}")
        cosmos_client = CosmosClient(
            url=os.getenv("COSMOS_ENDPOINT"),
            credential=str(os.getenv("COSMOS_KEY"))
        )
        database = cosmos_client.get_database_client("DualApiDB")
        container = database.get_container_client("DualApiContainer")
        container_properties = container.read()
        print(f"{Fore.GREEN}✓ NoSQL Connection Successful{Fore.RESET}")
        print(f"Container ID: {container_properties['id']}")

        # Test Gremlin Connection
        print(f"\n{Fore.CYAN}Testing Gremlin API:{Fore.RESET}")
        gremlin_client = client.Client(
            os.getenv("GREMLIN_ENDPOINT"),
            'g',
            username=f"/dbs/DualApiDB/colls/DualApiContainer",
            password=os.getenv("GREMLIN_PRIMARY_KEY"),
            message_serializer=serializer.GraphSONSerializersV2d0()
        )
        
        result = gremlin_client.submit("g.V().count()").all().result()
        print(f"{Fore.GREEN}✓ Gremlin Connection Successful{Fore.RESET}")
        print(f"Vertex Count: {result[0]}")
        gremlin_client.close()

    except Exception as e:
        print(f"{Fore.RED}Connection test failed: {e}{Fore.RESET}")

def verify_connection_details():
    """
    Verify that all required environment variables are set before attempting connections
    Returns True if all required variables are present, False otherwise
    """
    required_vars = [
        "COSMOS_ENDPOINT",
        "COSMOS_KEY",
        "DATABASE_NAME",
        "CONTAINER_NAME",
        "GREMLIN_ENDPOINT",
        "GREMLIN_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"{Fore.RED}Missing required environment variables:{Fore.RESET}")
        for var in missing_vars:
            print(f"- {var}")
        return False
    
    print(f"{Fore.GREEN}All required connection details verified✓{Fore.RESET}")
    return True

if __name__ == "__main__":
    verify_connection_details()
    test_dual_api_access()

# test_container_creation.py

import unittest
from azure.cosmos import CosmosClient
from createnewdualcontainer import DualContainerCreator
import os
from dotenv import load_dotenv

class TestDualContainer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv()
        cls.creator = DualContainerCreator()
        cls.container = cls.creator.create_container()
        
        # Initialize test client
        cls.cosmos_client = CosmosClient(
            url=os.getenv("COSMOS_ENDPOINT"),
            credential=str(os.getenv("COSMOS_KEY"))
        )
        cls.database = cls.cosmos_client.get_database_client("ProjectTechDB")
        cls.test_container = cls.database.get_container_client("ProjectTechContainer")

    def test_container_exists(self):
        """Verify container was created"""
        containers = list(self.database.list_containers())
        container_ids = [c['id'] for c in containers]
        self.assertIn("ProjectTechContainer", container_ids)

    def test_partition_key(self):
        """Verify partition key configuration"""
        container_props = self.test_container.read()
        self.assertEqual(container_props['partitionKey']['paths'][0], '/type')

    def test_indexing_policy(self):
        """Verify indexing paths"""
        container_props = self.test_container.read()
        included_paths = container_props['indexingPolicy']['includedPaths']
        expected_paths = [
            '/type/?',
            '/name/?',
            '/category/?',
            '/status/?',
            '/version/?',
            '/requirements/*/?',
            '/capabilities/*/?',
            '/relationships/*/?'
        ]
        for path in expected_paths:
            self.assertTrue(
                any(p['path'] == path for p in included_paths),
                f"Missing index path: {path}"
            )

    def test_sample_items(self):
        """Verify sample items structure"""
        query = "SELECT * FROM c WHERE c.type IN ('technology', 'project')"
        items = list(self.test_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        # Verify we have items of both types
        types = set(item['type'] for item in items)
        self.assertEqual(types, {'technology', 'project'})

if __name__ == '__main__':
    unittest.main()

import unittest
from colorama import init, Fore
from azure.cosmos import CosmosClient
from createnewdualcontainer import DualContainerCreator
import os
from dotenv import load_dotenv

# Initialize colorama for Windows
init()

class TestDualContainer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            print(f"{Fore.CYAN}Setting up test environment...{Fore.RESET}")
            load_dotenv()
            
            # Verify environment variables
            required_vars = ["COSMOS_ENDPOINT", "COSMOS_KEY"]
            missing = [var for var in required_vars if not os.getenv(var)]
            if missing:
                raise ValueError(f"Missing environment variables: {missing}")
            
            cls.creator = DualContainerCreator()
            cls.container = cls.creator.create_container()
            
            # Initialize test client
            cls.cosmos_client = CosmosClient(
                url=os.getenv("COSMOS_ENDPOINT"),
                credential=str(os.getenv("COSMOS_KEY"))
            )
            cls.database = cls.cosmos_client.get_database_client("ProjectTechDB")
            cls.test_container = cls.database.get_container_client("ProjectTechContainer")
            print(f"{Fore.GREEN}✓ Test environment ready{Fore.RESET}")
        
        except Exception as e:
            print(f"{Fore.RED}Error in test setup: {e}{Fore.RESET}")
            raise

    def test_container_exists(self):
        """Verify container was created"""
        print(f"\n{Fore.YELLOW}Testing container existence...{Fore.RESET}")
        containers = list(self.database.list_containers())
        container_ids = [c['id'] for c in containers]
        self.assertIn("ProjectTechContainer", container_ids)
        print(f"{Fore.GREEN}✓ Container exists{Fore.RESET}")

    def test_partition_key(self):
        """Verify partition key configuration"""
        print(f"\n{Fore.YELLOW}Testing partition key...{Fore.RESET}")
        container_props = self.test_container.read()
        self.assertEqual(container_props['partitionKey']['paths'][0], '/type')
        print(f"{Fore.GREEN}✓ Partition key correct{Fore.RESET}")

if __name__ == '__main__':
    unittest.main(verbosity=2)

import unittest
from colorama import init, Fore
from azure.cosmos import CosmosClient
from createnewdualcontainer import DualContainerCreator
from gremlin_python.driver import client, serializer
import os
from dotenv import load_dotenv

# Initialize colorama for Windows
init()

class TestDualContainer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            print(f"{Fore.CYAN}Setting up test environment...{Fore.RESET}")
            load_dotenv()
            cls.creator = DualContainerCreator()
            cls.container = cls.creator.create_container()
            
            # NoSQL Client
            cls.cosmos_client = CosmosClient(
                url=os.getenv("COSMOS_ENDPOINT"),
                credential=str(os.getenv("COSMOS_KEY"))
            )
            cls.database = cls.cosmos_client.get_database_client("ProjectTechDB")
            cls.test_container = cls.database.get_container_client("ProjectTechContainer")
            
            # Gremlin Client
            cls.gremlin_client = client.Client(
                os.getenv("GREMLIN_ENDPOINT"),
                'g',
                username=f"/dbs/ProjectTechDB/colls/ProjectTechContainer",
                password=os.getenv("GREMLIN_PRIMARY_KEY"),
                message_serializer=serializer.GraphSONSerializersV2d0()
            )
            print(f"{Fore.GREEN}✓ Test environment ready{Fore.RESET}")
        
        except Exception as e:
            print(f"{Fore.RED}Error in test setup: {e}{Fore.RESET}")
            raise

    def test_container_exists(self):
        """Verify container was created"""
        print(f"\n{Fore.YELLOW}Testing container existence...{Fore.RESET}")
        containers = list(self.database.list_containers())
        container_ids = [c['id'] for c in containers]
        self.assertIn("ProjectTechContainer", container_ids)
        print(f"{Fore.GREEN}✓ Container exists{Fore.RESET}")

    def test_partition_key(self):
        """Verify partition key configuration"""
        print(f"\n{Fore.YELLOW}Testing partition key...{Fore.RESET}")
        container_props = self.test_container.read()
        self.assertEqual(container_props['partitionKey']['paths'][0], '/type')
        print(f"{Fore.GREEN}✓ Partition key correct{Fore.RESET}")

    def test_indexing_policy(self):
        """Verify indexing paths"""
        print(f"\n{Fore.YELLOW}Testing indexing policy...{Fore.RESET}")
        container_props = self.test_container.read()
        included_paths = container_props['indexingPolicy']['includedPaths']
        expected_paths = [
            '/type/?',
            '/name/?',
            '/category/?',
            '/status/?',
            '/version/?',
            '/requirements/*/?',
            '/capabilities/*/?',
            '/relationships/*/?'
        ]
        for path in expected_paths:
            self.assertTrue(
                any(p['path'] == path for p in included_paths),
                f"Missing index path: {path}"
            )
        print(f"{Fore.GREEN}✓ Indexing policy correct{Fore.RESET}")

    def test_sample_items(self):
        """Verify sample items structure"""
        print(f"\n{Fore.YELLOW}Testing sample items...{Fore.RESET}")
        query = "SELECT * FROM c WHERE c.type IN ('technology', 'project')"
        items = list(self.test_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        types = set(item['type'] for item in items)
        self.assertEqual(types, {'technology', 'project'})
        print(f"{Fore.GREEN}✓ Sample items verified{Fore.RESET}")

    def test_container_data(self):
        """Verify we're accessing the correct container and data"""
        print(f"\n{Fore.YELLOW}Testing container data access...{Fore.RESET}")
        
        # Check NoSQL API
        try:
            nosql_query = "SELECT * FROM c"
            items = list(self.test_container.query_items(
                query=nosql_query,
                enable_cross_partition_query=True
            ))
            print(f"NoSQL Items found: {len(items)}")
            for item in items:
                print(f"Type: {item.get('type')}, Name: {item.get('name')}")
        
        except Exception as e:
            print(f"{Fore.RED}NoSQL query failed: {e}{Fore.RESET}")

        # Check Gremlin API
        try:
            gremlin_queries = {
                "vertices": "g.V().count()",
                "vertex_types": "g.V().label().dedup()",
                "sample": "g.V().limit(1).valueMap(true)"
            }
            
            print("\nGremlin API Check:")
            for name, query in gremlin_queries.items():
                result = self.gremlin_client.submit(query).all().result()
                print(f"{name}: {result}")
        
        except Exception as e:
            print(f"{Fore.RED}Gremlin query failed: {e}{Fore.RESET}")

    def test_connections(self):
        """Verify connection details and container access"""
        print(f"\n{Fore.CYAN}Testing Connections:{Fore.RESET}")
        
        # Verify NoSQL Connection
        try:
            print(f"\n{Fore.YELLOW}NoSQL Connection Details:{Fore.RESET}")
            print(f"Endpoint: {os.getenv('COSMOS_ENDPOINT')}")
            print(f"Database: {self.database.id}")
            print(f"Container: {self.test_container.id}")
            
            # Get container properties
            container_props = self.test_container.read()
            print(f"Partition Key: {container_props['partitionKey']['paths'][0]}")
            
        except Exception as e:
            print(f"{Fore.RED}NoSQL connection error: {e}{Fore.RESET}")

        # Verify Gremlin Connection
        try:
            print(f"\n{Fore.YELLOW}Gremlin Connection Details:{Fore.RESET}")
            print(f"Endpoint: {os.getenv('GREMLIN_ENDPOINT')}")
            print(f"Database: {os.getenv('GREMLIN_DATABASE')}")
            print(f"Collection: {os.getenv('GREMLIN_COLLECTION')}")
            
            # Test simple query
            query = "g.V().count()"
            result = self.gremlin_client.submit(query).all().result()
            print(f"Vertex Count: {result[0]}")
            
        except Exception as e:
            print(f"{Fore.RED}Gremlin connection error: {e}{Fore.RESET}")

        print(f"\n{Fore.CYAN}Connection test complete{Fore.RESET}")

    @classmethod
    def tearDownClass(cls):
        try:
            cls.gremlin_client.close()
            print(f"\n{Fore.CYAN}Test environment cleaned up{Fore.RESET}")
        except Exception as e:
            print(f"{Fore.RED}Error in cleanup: {e}{Fore.RESET}")

    def test_dual_access(self):
        # Test NoSQL Access
        items = self.container.query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True
        )
        print(f"NoSQL Items: {len(list(items))}")

        # Test Gremlin Access (same container)
        gremlin_client = client.Client(
            os.getenv("GREMLIN_ENDPOINT"),
            'g',
            username=f"/dbs/ProjectTechDB/colls/ProjectTechContainer",
            password=os.getenv("GREMLIN_PRIMARY_KEY")
        )
        
        result = gremlin_client.submit("g.V().count()").all().result()

    def test_dual_api_configuration(self):
        """Verify both APIs are accessing same container"""
        print(f"\n{Fore.CYAN}Verifying Dual API Configuration:{Fore.RESET}")
        
        try:
            # Verify NoSQL Configuration
            nosql_container = self.test_container.read()
            print(f"\n{Fore.YELLOW}NoSQL Container Configuration:{Fore.RESET}")
            print(f"Database: {NOSQL_CONNECTION['database']}")
            print(f"Container: {NOSQL_CONNECTION['container']}")
            print(f"Partition Key: {nosql_container['partitionKey']['paths'][0]}")

            # Verify Gremlin Configuration
            gremlin_query = "g.V().count()"
            gremlin_result = self.gremlin_client.submit(gremlin_query).all().result()
            print(f"\n{Fore.YELLOW}Gremlin Container Configuration:{Fore.RESET}")
            print(f"Database: {GREMLIN_CONNECTION['database']}")
            print(f"Container: {GREMLIN_CONNECTION['container']}")
            print(f"Vertex Count: {gremlin_result[0]}")

            # Verify Same Container Access
            self.assertEqual(NOSQL_CONNECTION['database'], GREMLIN_CONNECTION['database'])
            self.assertEqual(NOSQL_CONNECTION['container'], GREMLIN_CONNECTION['container'])
            print(f"{Fore.GREEN}✓ Both APIs accessing same container{Fore.RESET}")

        except Exception as e:
            print(f"{Fore.RED}Configuration verification failed: {e}{Fore.RESET}")
            raise

if __name__ == '__main__':
    unittest.main(verbosity=2)

def test_connections(self):
    """Verify connection details and container access"""
    print(f"\n{Fore.CYAN}Testing Connections:{Fore.RESET}")
    
    # Verify NoSQL Connection
    try:
        print(f"\n{Fore.YELLOW}NoSQL Connection Details:{Fore.RESET}")
        print(f"Endpoint: {os.getenv('COSMOS_ENDPOINT')}")
        print(f"Database: {self.database.id}")
        print(f"Container: {self.test_container.id}")
        
        # Get container properties
        container_props = self.test_container.read()
        print(f"Partition Key: {container_props['partitionKey']['paths'][0]}")
        
    except Exception as e:
        print(f"{Fore.RED}NoSQL connection error: {e}{Fore.RESET}")

    # Verify Gremlin Connection
    try:
        print(f"\n{Fore.YELLOW}Gremlin Connection Details:{Fore.RESET}")
        print(f"Endpoint: {os.getenv('GREMLIN_ENDPOINT')}")
        print(f"Database: {os.getenv('GREMLIN_DATABASE')}")
        print(f"Collection: {os.getenv('GREMLIN_COLLECTION')}")
        
        # Test simple query
        query = "g.V().count()"
        result = self.gremlin_client.submit(query).all().result()
        print(f"Vertex Count: {result[0]}")
        
    except Exception as e:
        print(f"{Fore.RED}Gremlin connection error: {e}{Fore.RESET}")

    print(f"\n{Fore.CYAN}Connection test complete{Fore.RESET}")

# test_configuration.py
import os
from dotenv import load_dotenv
from colorama import init, Fore
from azure.cosmos import CosmosClient
from gremlin_python.driver import client, serializer

# Initialize colorama
init()

def verify_configuration():
    """Verify environment configuration and API access"""
    try:
        print(f"{Fore.CYAN}Verifying configuration...{Fore.RESET}")
        load_dotenv()
        
        # Test NoSQL API
        cosmos_client = CosmosClient(
            url=os.getenv("COSMOS_ENDPOINT"),
            credential=str(os.getenv("COSMOS_KEY"))
        )
        
        database = cosmos_client.get_database_client("DualApiDB")
        container = database.get_container_client("DualApiContainer")
        print(f"{Fore.GREEN}✓ NoSQL connection successful{Fore.RESET}")
        
        # Test Gremlin API
        gremlin_client = client.Client(
            os.getenv("GREMLIN_ENDPOINT"),
            'g',
            username=f"/dbs/DualApiDB/colls/DualApiContainer",
            password=os.getenv("GREMLIN_PRIMARY_KEY"),
            message_serializer=serializer.GraphSONSerializersV2d0()
        )
        
        result = gremlin_client.submit("g.V().count()").all().result()
        print(f"{Fore.GREEN}✓ Gremlin connection successful{Fore.RESET}")
        gremlin_client.close()
        
        print(f"\n{Fore.GREEN}Configuration verified successfully{Fore.RESET}")
        
    except Exception as e:
        print(f"{Fore.RED}Configuration verification failed: {e}{Fore.RESET}")

if __name__ == "__main__":
    verify_configuration()
    test_dual_api_access()