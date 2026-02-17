import os
import pandas as pd
from deepface import DeepFace
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid

class IdentityVerifier:
    def __init__(self, model_name='ArcFace', detector_backend='opencv', db_collection='face_embeddings', embedding_dim=512):
        self.model_name = model_name
        self.detector_backend = detector_backend
        self.embedding_dim = embedding_dim
        self.db_collection = db_collection
        
        # 1. Initialize Vector Database Client (local file-based, no Docker needed)
        qdrant_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qdrant_data")
        os.makedirs(qdrant_path, exist_ok=True)
        
        self.db_client = QdrantClient(path=qdrant_path)
        
        # 2. Ensure Collection Exists
        try:
            if not self.db_client.collection_exists(collection_name=self.db_collection):
                self.db_client.create_collection(
                    collection_name=self.db_collection,
                    vectors_config=VectorParams(size=self.embedding_dim, distance=Distance.COSINE)
                )
        except Exception as e:
            print(f"[WARNING] Warning: Could not check/create collection: {e}")

    ## --- Database Operations ---

    def enroll_identity(self, img_path: str, user_id: str):
        """Generates an embedding and stores it in the vector database (1:N setup)."""
        try:
            # DeepFace.represent returns a list of dictionaries
            embedding_results = DeepFace.represent(
                img_path=img_path, 
                model_name=self.model_name, 
                detector_backend=self.detector_backend,
                enforce_detection=True
            )
            
            if not embedding_results:
                return False, "No face detected."

            # Take the first face found
            embedding = embedding_results[0]['embedding']
            
            # Create a unique ID for the point if user_id is not a valid UUID or integer
            # Qdrant requires point IDs to be integers or UUIDs. 
            # We'll generate a UUID based on the user_id string for consistency if needed, 
            # but for simplicity let's generate a random UUID and store user_id in payload.
            point_id = str(uuid.uuid4())

            point = PointStruct(
                id=point_id, 
                payload={"user_id": user_id, "source_image": img_path},
                vector=embedding
            )
            
            self.db_client.upsert(collection_name=self.db_collection, wait=True, points=[point])
            return True, f"User {user_id} enrolled successfully."
            
        except Exception as e:
            return False, f"Enrollment Error: {str(e)}"

    ## --- Verification/Identification Logic ---

    def identify_from_database(self, img_path: str, threshold: float = 0.75):
        """Performs 1:N Identification against the database."""
        try:
            # 1. Get embedding for the query image
            embedding_results = DeepFace.represent(
                img_path=img_path, 
                model_name=self.model_name, 
                detector_backend=self.detector_backend,
                enforce_detection=False
            )
            
            if not embedding_results:
                return False, None, "No face detected in query image."

            target_embedding = embedding_results[0]['embedding']
            
            # 2. Query the vector database
            results = self.db_client.query_points(
                collection_name=self.db_collection,
                query=target_embedding,
                limit=1,
                score_threshold=threshold
            )

            if results.points:
                best_match = results.points[0]
                print(f"   [SEARCH] Best match: {best_match.payload['user_id']} (score: {best_match.score:.4f}, threshold: {threshold})")
                return True, best_match.payload['user_id'], best_match.score
            else:
                # Debug: search without threshold to see what scores we're getting
                debug_results = self.db_client.query_points(
                    collection_name=self.db_collection,
                    query=target_embedding,
                    limit=1
                )
                if debug_results.points:
                    print(f"   [SEARCH] Closest match: {debug_results.points[0].payload['user_id']} (score: {debug_results.points[0].score:.4f}, needed: {threshold})")
                else:
                    print(f"   [SEARCH] No faces in collection '{self.db_collection}'")
                return False, None, 0.0
            
        except Exception as e:
            print(f"Identification Error: {str(e)}")
            return False, None, 0.0

    def verify_1_to_1(self, img1_path: str, img2_path: str):
        """Original 1:1 verification."""
        try:
            result = DeepFace.verify(
                img1_path=img1_path, 
                img2_path=img2_path,
                model_name=self.model_name,
                detector_backend=self.detector_backend,
                enforce_detection=True
            )
            # Convert numpy types to native python types for JSON serialization
            if isinstance(result, dict):
                for key, value in result.items():
                    if hasattr(value, 'item'):  # Checks for numpy types
                        result[key] = value.item()
            return result
        except Exception as e:
            return {"verified": False, "error": str(e)}
