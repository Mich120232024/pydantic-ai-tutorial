# verify_configuration.py

import os
from dotenv import load_dotenv
from colorama import init, Fore
from azure.cosmos import CosmosClient
from gremlin_python.driver import client, serializer

# Initialize colorama for Windows
init()

def verify_connection_details():
    """Verify connection details for both APIs"""
    try:
        load_dotenv()
        print(f"\n{Fore.YELLOW}Current Connection Details:{Fore.RESET}")
        
        # Expected values
        expected_db = "DualApiDB"
        expected_container = "DualApiContainer"
        
        # NoSQL Configuration
        print(f"\n{Fore.CYAN}NoSQL Configuration:{Fore.RESET}")
        print(f"Endpoint: {os.getenv('COSMOS_ENDPOINT')}")
        print(f"Database (Expected): {expected_db}")
        print(f"Database (Actual): {os.getenv('DATABASE_NAME')}")
        print(f"Container (Expected): {expected_container}")
        print(f"Container (Actual): {os.getenv('CONTAINER_NAME')}")
        print(f"Partition Key: {os.getenv('PARTITION_KEY')}")
        
        # Gremlin Configuration
        print(f"\n{Fore.CYAN}Gremlin Configuration:{Fore.RESET}")
        print(f"Endpoint: {os.getenv('GREMLIN_ENDPOINT')}")
        print(f"Database (Expected): {expected_db}")
        print(f"Database (Actual): {os.getenv('GREMLIN_DATABASE')}")
        print(f"Container (Expected): {expected_container}")
        print(f"Container (Actual): {os.getenv('GREMLIN_COLLECTION')}")
        
        # Verify Gremlin connection string
        gremlin_username = f"/dbs/{expected_db}/colls/{expected_container}"
        print(f"\nGremlin Username (Expected): {gremlin_username}")
        print(f"Gremlin Username (Actual): /dbs/{os.getenv('GREMLIN_DATABASE')}/colls/{os.getenv('GREMLIN_COLLECTION')}")
        
        # Configuration check result
        if (os.getenv('DATABASE_NAME') == expected_db and 
            os.getenv('CONTAINER_NAME') == expected_container and
            os.getenv('GREMLIN_DATABASE') == expected_db and
            os.getenv('GREMLIN_COLLECTION') == expected_container):
            print(f"\n{Fore.GREEN}✓ Configuration is correct{Fore.RESET}")
        else:
            print(f"\n{Fore.RED}× Configuration mismatch - Update .env file{Fore.RESET}")
        
        return True
        
    except Exception as e:
        print(f"\n{Fore.RED}Error verifying configuration: {e}{Fore.RESET}")
        return False

def test_gremlin_connection():
    """Test Gremlin connection with new configuration"""
    try:
        load_dotenv()
        
        # Create Gremlin client with new settings
        gremlin_client = client.Client(
            os.getenv("GREMLIN_ENDPOINT"),
            'g',
            username=f"/dbs/DualApiDB/colls/DualApiContainer",
            password=os.getenv("GREMLIN_PRIMARY_KEY"),
            message_serializer=serializer.GraphSONSerializersV2d0()
        )

        # Test queries
        queries = {
            "count": "g.V().count()",
            "labels": "g.V().label().dedup()",
            "partition_keys": "g.V().values('pk').dedup()"
        }

        print(f"{Fore.CYAN}Testing Gremlin Connection with new configuration:{Fore.RESET}")
        print(f"Database: DualApiDB")
        print(f"Container: DualApiContainer")
        print(f"Partition Key: /type")

        for name, query in queries.items():
            result = gremlin_client.submit(query).all().result()
            print(f"\n{Fore.GREEN}✓ {name}:{Fore.RESET}")
            print(f"  {result}")

        gremlin_client.close()
        print(f"\n{Fore.GREEN}Connection test completed successfully{Fore.RESET}")

    except Exception as e:
        print(f"{Fore.RED}Connection test failed: {e}{Fore.RESET}")

if __name__ == "__main__":
    verify_connection_details()
    test_gremlin_connection()