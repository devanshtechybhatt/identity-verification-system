import requests
import time
import os

# Configuration
BASE_URL = "http://localhost:8000"
TEST_IMAGE_DIR = "dataset"  # Ensure you have images here
ID_CARD_IMAGE = "dataset/sample_id.jpg" # Replace with actual file if needed
SELFIE_IMAGE = "dataset/sample_selfie.jpg" # Replace with actual file if needed

def create_dummy_images():
    """Create dummy images if they don't exist for the demo to run."""
    if not os.path.exists("dataset"):
        os.makedirs("dataset")
    
    # We need real images for face recognition to work, 
    # but for the script to not crash we check existence.
    # PLEASE MANUALLY PLACE 'sample_id.jpg' and 'sample_selfie.jpg' in 'dataset/' folder.
    if not os.path.exists(ID_CARD_IMAGE) or not os.path.exists(SELFIE_IMAGE):
        print(f"  [WARNING]  MISSING IMAGES: Please put {ID_CARD_IMAGE} and {SELFIE_IMAGE} in the folder.")
        print("   The demo needs real faces to show 'Success'.")
        return False
    return True

def run_demo():
    print("  [DEMO] Starting Identity Verification System Demo...\n")
    
    if not create_dummy_images():
        return

    # 1. Health Check
    print(f"  [1]  Checking System Health...")
    start = time.time()
    try:
        requests.get(BASE_URL)
        print(f"   [SUCCESS] System is UP (Time: {time.time() - start:.4f}s)")
    except Exception as e:
        print(f"   [FAILURE] System is DOWN. Is Docker running? ({e})")
        return

    # 2. Enrollment
    print(f"\n  [2]  Enrolling User 'Student Demo'...")
    start = time.time()
    files = {'file': open(ID_CARD_IMAGE, 'rb')}
    data = {'name': 'Student Demo'}
    response = requests.post(f"{BASE_URL}/enroll", files=files, data=data)
    print(f"   [TIME]  Time Taken: {time.time() - start:.4f}s")
    print(f"   Result: {response.json()}")

    # 3. Verification (1:1)
    print(f"\n  [3]  Verifying Identity (1:1 Match)...")
    start = time.time()
    files = {
        'id_card': open(ID_CARD_IMAGE, 'rb'),
        'selfie': open(SELFIE_IMAGE, 'rb')
    }
    response = requests.post(f"{BASE_URL}/verify", files=files)
    result = response.json()
    print(f"   [TIME]  Time Taken: {time.time() - start:.4f}s")
    print(f"   Result: {result}")
    
    if result.get('verified'):
        print("\n  [SUCCESS] DEMO PASSED: Identity Verified!")
    else:
        print("\n  [FAILURE]  DEMO RESULT: Not Verified (Check images)")

if __name__ == "__main__":
    run_demo()
