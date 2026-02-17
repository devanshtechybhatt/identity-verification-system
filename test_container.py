import os
import sys
from verifier import IdentityVerifier
import time

def test_internal():
    print("🧪 Starting Internal Container Test...")
    
    # Check Environment Variables
    host = os.getenv("QDRANT_HOST", "NOT_SET")
    port = os.getenv("QDRANT_PORT", "NOT_SET")
    print(f"ℹ️  Qdrant Config: {host}:{port}")
    
    # Attempt Connection
    try:
        verifier = IdentityVerifier()
        print("✅ Verifier Initialized & Connected to Qdrant")
    except Exception as e:
        print(f"❌ Critical: Failed to initialize Verifier: {e}")
        sys.exit(1)

    # Check Collection
    try:
        collections = verifier.db_client.get_collections()
        print(f"✅ Collections found: {collections}")
    except Exception as e:
        print(f"❌ Critical: Failed to list collections: {e}")
        sys.exit(1)

    print("\n✅ Internal Health Check Passed!")

if __name__ == "__main__":
    test_internal()
