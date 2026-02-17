import os
import argparse
from verifier import IdentityVerifier
from tqdm import tqdm

def ingest_data(data_dir, model_name='ArcFace'):
    print(f"🚀 Starting Data Ingestion from {data_dir}...")
    
    verifier = IdentityVerifier(model_name=model_name)
    
    if not os.path.exists(data_dir):
        print(f"❌ Data directory '{data_dir}' not found.")
        print("Please create the directory and add images (e.g., data/lfw/Person_Name/image.jpg)")
        return

    # Walk through the directory
    # Structure expected: data_dir/User_ID/image.jpg OR data_dir/User_ID_001.jpg
    
    supported_exts = ['.jpg', '.jpeg', '.png']
    files_to_process = []
    
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in supported_exts):
                full_path = os.path.join(root, file)
                # Infer User ID: 
                # If inside a subdirectory, use subdirectory name.
                # If in root, use filename without extension.
                if root == data_dir:
                    user_id = os.path.splitext(file)[0]
                else:
                    user_id = os.path.basename(root)
                
                files_to_process.append((full_path, user_id))

    print(f"Found {len(files_to_process)} images to process.")
    
    success_count = 0
    fail_count = 0
    
    for img_path, user_id in tqdm(files_to_process, desc="Enrolling Faces"):
        success, message = verifier.enroll_identity(img_path, user_id)
        if success:
            success_count += 1
        else:
            fail_count += 1
            print(f"Failed to enroll {user_id} ({os.path.basename(img_path)}): {message}")

    print("-" * 30)
    print(f"✅ Ingestion Complete.")
    print(f"Successful Enrollments: {success_count}")
    print(f"Failed Enrollments: {fail_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest images into the Identity Verification System")
    parser.add_argument("--data_dir", type=str, default="data", help="Path to the directory containing images")
    args = parser.parse_args()
    
    ingest_data(args.data_dir)
