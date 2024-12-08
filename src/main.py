# main.py
import asyncio
from dual_api_document_processor import DocumentProcessor

async def main():
    try:
        # Initialize processor
        processor = DocumentProcessor()
        print("Initializing document processor...")

        # Example document structure
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

        # Process document
        print("\nProcessing document structure...")
        success = await processor.process_document(test_doc)
        
        if success:
            print("✅ Document processed successfully")
        else:
            print("❌ Document processing failed")

    except Exception as e:
        print(f"❌ Error in main: {e}")
    finally:
        processor.close()
        print("\n🔄 Connections closed")

if __name__ == "__main__":
    asyncio.run(main())