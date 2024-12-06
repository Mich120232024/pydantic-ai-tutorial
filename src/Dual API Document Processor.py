"""
Dual API Document Processor for Advanced Decision Engine
"""

import os
import asyncio
from typing import Dict, List
from openai import AzureOpenAI
from azure.cosmos import CosmosClient
from gremlin_python.driver import client, serializer
from dotenv import load_dotenv

class DocumentProcessor:
    def __init__(self):
        load_dotenv()
        
        # NoSQL Client
        self.cosmos_client = CosmosClient(
            url=os.getenv("COSMOS_ENDPOINT"),
            credential=str(os.getenv("COSMOS_KEY"))
        )
        self.database = self.cosmos_client.get_database_client("GroundZeroDB")
        self.container = self.database.get_container_client("GZC_IDE")

        # Gremlin Client 
        self.gremlin_client = client.Client(
            os.getenv("GREMLIN_ENDPOINT"),
            'g',
            username=f"/dbs/{os.getenv('GREMLIN_DATABASE')}/colls/{os.getenv('GREMLIN_COLLECTION')}",
            password=os.getenv("GREMLIN_PRIMARY_KEY"),
            message_serializer=serializer.GraphSONSerializersV2d0()
        )

        # Azure OpenAI Client
        self.openai_client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2023-05-15", 
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )

    async def generate_embedding(self, text: str):
        """Generate embeddings for text using Azure OpenAI"""
        try:
            response = await self.openai_client.embeddings.create(
                input=text,
                model=os.getenv("EMBEDDING_DEPLOYMENT_NAME")
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None

    async def store_document(self, content: Dict):
        """Store document in both NoSQL and Gremlin"""
        try:
            # Generate embedding
            text = str(content)
            embedding = await self.generate_embedding(text)

            # Store in NoSQL
            doc_id = str(hash(text))
            doc = {
                "id": doc_id,
                "content": content,
                "embedding": embedding,
                "type": "document"
            }
            self.container.upsert_item(doc)

            # Store in Gremlin
            self._store_relationships(content, doc_id)
            return True
        except Exception as e:
            print(f"Error storing document: {e}")
            return False

    def _store_relationships(self, content: Dict, parent_id: str = None):
        """Extract and store relationships in Gremlin"""
        for key, value in content.items():
            current_id = str(hash(key))
            
            # Add vertex
            vertex_query = (
                f"g.addV('concept')"
                f".property('id', '{current_id}')"
                f".property('name', '{key}')"
                f".property('pk', 'concept')"
            )
            self.gremlin_client.submit(vertex_query).all().result()

            # Add edge if parent exists
            if parent_id:
                edge_query = (
                    f"g.V().has('id', '{parent_id}')"
                    f".addE('contains')"
                    f".to(g.V().has('id', '{current_id}'))"
                )
                self.gremlin_client.submit(edge_query).all().result()

            # Process nested content
            if isinstance(value, dict):
                self._store_relationships(value, current_id)

    def close(self):
        """Close connections"""
        self.gremlin_client.close()