# main.py
import asyncio
from dual_api_document_processor import DocumentProcessor

async def main():
    try:
        processor = DocumentProcessor()
        print("Initializing document processor...")

        # Example document structure from advanced-decision-engine.md
        test_doc = {
            "Advanced Decision Engine": {
                "Sophisticated Price Discovery": {
                    "Multi-Venue Price Formation": {
                        "Price Aggregation": {
                            "Cross-Venue Analysis": [
                                "Composite Price Building",
                                "Best bid/offer calculation",
                                "Depth-adjusted pricing"
                            ]
                        }
                    }
                }
            }
        }