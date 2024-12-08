# test_final_setup.py
import os
from dotenv import load_dotenv
from colorama import init, Fore
from azure.cosmos import CosmosClient
from gremlin_python.driver import client, serializer

# Initialize colorama
init()

def test_final_setup():
    try:
        load_dotenv()
        print(f"\n{Fore.CYAN}Final Setup Verification:{Fore.RESET}")
        
        # Test NoSQL Connection
        print(f"\n{Fore.YELLOW}Testing NoSQL API:{Fore.RESET}")
        cosmos_client = CosmosClient(
            url=os.getenv("COSMOS_ENDPOINT"),
            credential=str(os.getenv("COSMOS_KEY"))
        )
        database = cosmos_client.get_database_client("DualApiDB")
        container = database.get_container_client("DualApiContainer")
        
        # Insert test item via NoSQL
        test_item = {
            'id': 'test-item-1',
            'type': 'technology',
            'name': 'Test Technology',
            'category': 'testing'
        }
        container.upsert_item(test_item)
        print(f"{Fore.GREEN}✓ NoSQL Insert successful{Fore.RESET}")
        
        # Test Gremlin Connection
        print(f"\n{Fore.YELLOW}Testing Gremlin API:{Fore.RESET}")
        gremlin_client = client.Client(
            os.getenv("GREMLIN_ENDPOINT"),
            'g',
            username=f"/dbs/DualApiDB/colls/DualApiContainer",
            password=os.getenv("GREMLIN_PRIMARY_KEY"),
            message_serializer=serializer.GraphSONSerializersV2d0()
        )
        
        # Test Gremlin queries
        queries = {
            "vertex_count": "g.V().count()",
            "vertices_by_type": "g.V().groupCount().by('type')",
            "test_item": "g.V().has('type', 'technology').values('name')"
        }
        
        for name, query in queries.items():
            result = gremlin_client.submit(query).all().result()
            print(f"{Fore.GREEN}✓ {name}: {result}{Fore.RESET}")
        
        gremlin_client.close()
        print(f"\n{Fore.GREEN}Final setup verified successfully{Fore.RESET}")
        
    except Exception as e:
        print(f"\n{Fore.RED}Setup verification failed: {e}{Fore.RESET}")
        raise

if __name__ == "__main__":
    test_final_setup()