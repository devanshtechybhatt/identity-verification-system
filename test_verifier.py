import os
import time
from verifier import IdentityVerifier
import numpy as np
from PIL import Image

def create_dummy_image(filename):
    # Create a random noise image just to have a file if none exists
    # Note: DeepFace will fail to detect a face in noise, so this is just for file existence checks
    # In a real test, we need real face images.
    img = Image.fromarray(np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8))
    img.save(filename)
    return filename

def test_system():
    print("🧪 Starting System Verification...")
    
    # Initialize Verifier
    try:
        verifier = IdentityVerifier(model_name='ArcFace')
        print("✅ Verifier Initialized")
    except Exception as e:
        print(f"❌ Verifier Initialization Failed: {e}")
        return

    # We need real face images for this to work. 
    # Since we can't generate a real face programmatically without a GAN, 
    # we will check if we have the LFW dataset or similar.
    # For now, we will just print instructions if no images are found.
    
    print("\n--- Test 1: Enrollment ---")
    # Placeholder for user to manually test or if they have images
    print("ℹ️  To test enrollment, ensure you have an image at 'test_face.jpg'")
    
    print("\n--- Test 2: Identification ---")
    print("ℹ️  To test identification, ensure you have enrolled a user.")

    print("\n--- Test 3: 1:1 Verification ---")
    # We can try to run a verification on two dummy files just to see if the pipeline runs (it will fail detection)
    create_dummy_image("dummy1.jpg")
    create_dummy_image("dummy2.jpg")
    
    print("Running 1:1 verification pipeline on dummy images (expecting 'Face could not be detected' error)...")
    result = verifier.verify_1_to_1("dummy1.jpg", "dummy2.jpg")
    print(f"Result: {result}")
    
    # Clean up
    if os.path.exists("dummy1.jpg"): os.remove("dummy1.jpg")
    if os.path.exists("dummy2.jpg"): os.remove("dummy2.jpg")

    print("\n✅ Verification Script Completed (Check logs for details)")

if __name__ == "__main__":
    test_system()
