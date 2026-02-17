"""
# Identity Verification System - One-Click Launcher
=====================================================
Flow:
  1. First run: Enroll yourself via webcam (saves to separate auth database)
  2. Face Scan Agent authenticates ONLY against YOUR enrolled face
  3. If verified → localhost website opens automatically

Run:   python launch.py
Re-enroll: python launch.py --enroll
"""

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # Suppress TF info/warning messages

import subprocess
import sys
import time
import webbrowser
import threading
import hashlib

# ─── Configuration ────────────────────────────────────
PORT = 8000
URL = f"http://localhost:{PORT}"
AUTH_COLLECTION = "authorized_faces"       # Separate collection — ONLY your face
MAIN_COLLECTION = "face_embeddings"        # Main collection for the web dashboard
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AUTHORIZED_DIR = os.path.join(SCRIPT_DIR, "dataset", "authorized_users")
PASSWORD_FILE = os.path.join(AUTHORIZED_DIR, ".backup_pass")
THRESHOLD_FILE = os.path.join(AUTHORIZED_DIR, ".adaptive_threshold")
QDRANT_PATH = os.path.join(SCRIPT_DIR, "qdrant_data")

# Global shared verifier — avoids Qdrant file lock conflicts
_auth_verifier = None


def get_auth_verifier():
    """Get or create the shared auth verifier (single Qdrant client instance)."""
    global _auth_verifier
    if _auth_verifier is None:
        from verifier import IdentityVerifier
        _auth_verifier = IdentityVerifier(db_collection=AUTH_COLLECTION)
    return _auth_verifier


def close_auth_verifier():
    """Close the shared auth verifier to release Qdrant file lock."""
    global _auth_verifier
    if _auth_verifier is not None:
        try:
            _auth_verifier.db_client.close()
        except Exception:
            pass
        _auth_verifier = None


def print_banner():
    print()
    print("================================================================")
    print("                                                          ")
    print("      IDENTITY VERIFICATION SYSTEM                      ")
    print("   ---------------------------------                      ")
    print("   Step 1: Biometric authentication (face scan)           ")
    print("   Step 2: Dashboard opens in browser if verified         ")
    print("                                                          ")
    print("================================================================")
    print()


# ═══════════════════════════════════════════════════════
#  AUTH DATABASE — Enroll authorized user photos
# ═══════════════════════════════════════════════════════

def enroll_authorized_photos():
    """Enroll all photos in authorized_users/ into the auth collection."""
    if not os.path.isdir(AUTHORIZED_DIR):
        return 0

    photos = [f for f in os.listdir(AUTHORIZED_DIR) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    if not photos:
        return 0

    user_name = "Authorized User"
    name_file = os.path.join(AUTHORIZED_DIR, "name.txt")
    if os.path.exists(name_file):
        with open(name_file, "r") as f:
            user_name = f.read().strip()

    print(f"   [INFO] Enrolling {len(photos)} photos into auth database...")
    verifier = get_auth_verifier()

    enrolled = 0
    for photo in photos:
        img_path = os.path.join(AUTHORIZED_DIR, photo)
        success, msg = verifier.enroll_identity(img_path, user_name)
        if success:
            enrolled += 1
            print(f"   [SUCCESS] Enrolled: {photo}")
        else:
            print(f"   [WARNING]  Failed: {photo} — {msg}")

    print(f"   [SUCCESS] Auth database ready: {enrolled} photos for '{user_name}'")
    return enrolled


def seed_main_database():
    """Seed LFW faces into the main collection (for the web dashboard)."""
    # Must close auth verifier first to release Qdrant lock
    close_auth_verifier()

    try:
        from verifier import IdentityVerifier
        verifier = IdentityVerifier(db_collection=MAIN_COLLECTION)

        try:
            info = verifier.db_client.get_collection(MAIN_COLLECTION)
            if info.points_count > 0:
                print(f"   [SUCCESS] Main DB has {info.points_count} faces.")
                verifier.db_client.close()
                return
        except Exception:
            pass

        dataset_dir = os.path.join(SCRIPT_DIR, "dataset", "lfw-deepfunneled")
        if not os.path.isdir(dataset_dir):
            print("   [WARNING]  No LFW dataset found. Skipping.")
            verifier.db_client.close()
            return

        print("   [INFO] Seeding LFW faces into main database...")

        count = 0
        for person_dir in sorted(os.listdir(dataset_dir)):
            person_path = os.path.join(dataset_dir, person_dir)
            if not os.path.isdir(person_path):
                continue
            images = [f for f in os.listdir(person_path) if f.endswith(('.jpg', '.png', '.jpeg'))]
            if images:
                img_path = os.path.join(person_path, images[0])
                name = person_dir.replace("_", " ")
                success, _ = verifier.enroll_identity(img_path, name)
                if success:
                    count += 1
                if count >= 15:
                    break
        print(f"   [SUCCESS] Seeded {count} LFW faces into main DB.")
        verifier.db_client.close()

    except Exception as e:
        print(f"   [WARNING]  Could not seed main database: {e}")


# ═══════════════════════════════════════════════════════
#  SELF-ENROLLMENT — Capture face via webcam
# ═══════════════════════════════════════════════════════

def enroll_self_via_webcam():
    """Open webcam, capture 3 photos, save and enroll into auth database."""
    import cv2

    print()
    print("-" * 55)
    print("  [CAMERA]  BIOMETRIC ENROLLMENT")
    print("  -------------------------")
    print("  Capture 3 photos to create your authentication")
    print("  profile. This only needs to be done once.")
    print("-" * 55)
    print()

    user_name = input("  Enter your full name: ").strip()
    if not user_name:
        user_name = "Authorized User"

    # Set backup password
    print()
    print("  [KEY] Set a backup password (in case face scan fails):")
    while True:
        pw = input("  Password: ")
        pw2 = input("  Confirm:  ")
        if pw == pw2 and len(pw) >= 1:
            break
        print("  [WARNING]  Passwords don't match or empty. Try again.")

    os.makedirs(AUTHORIZED_DIR, exist_ok=True)
    pw_hash = hashlib.sha256(pw.encode()).hexdigest()
    with open(PASSWORD_FILE, "w") as f:
        f.write(pw_hash)
    print("  [SUCCESS] Backup password saved.")
    print()

    with open(os.path.join(AUTHORIZED_DIR, "name.txt"), "w") as f:
        f.write(user_name)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("  [ERROR] Cannot open webcam!")
        return False

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    win_name = "Biometric Enrollment"
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(win_name, cv2.WND_PROP_TOPMOST, 1)
    cv2.resizeWindow(win_name, 640, 480)

    photos_taken = 0
    target_photos = 3
    last_capture_time = 0

    print(f"\n  [CAMERA] Press SPACE to capture ({target_photos} photos needed)")
    print("  [CANCEL] Press ESC to cancel\n")

    while photos_taken < target_photos:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        display = frame.copy()
        h, w = display.shape[:2]

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        # Header
        cv2.rectangle(display, (0, 0), (w, 52), (12, 12, 20), -1)
        cv2.putText(display, f"ENROLLMENT: {user_name.upper()}", (14, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 210, 210), 1, cv2.LINE_AA)
        cv2.putText(display, f"Photo {photos_taken + 1} of {target_photos}", (14, 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (140, 140, 160), 1, cv2.LINE_AA)

        # Face box
        for (x, y, fw, fh) in faces:
            cv2.rectangle(display, (x, y), (x + fw, y + fh), (0, 230, 140), 2)

        # Flash effect
        if time.time() - last_capture_time < 0.25:
            overlay = display.copy()
            overlay[:] = (255, 255, 255)
            cv2.addWeighted(overlay, 0.35, display, 0.65, 0, display)

        # Footer
        cv2.rectangle(display, (0, h - 38), (w, h), (12, 12, 20), -1)
        if len(faces) > 0:
            cv2.putText(display, "Press SPACE to capture", (w // 2 - 105, h - 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 230, 140), 1, cv2.LINE_AA)
        else:
            cv2.putText(display, "Position your face in the frame", (w // 2 - 140, h - 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, (100, 100, 230), 1, cv2.LINE_AA)

        cv2.imshow(win_name, display)
        key = cv2.waitKey(1) & 0xFF

        if key == 32 and len(faces) > 0:  # SPACE
            photo_path = os.path.join(AUTHORIZED_DIR, f"face_{photos_taken + 1}.jpg")
            cv2.imwrite(photo_path, frame)
            photos_taken += 1
            last_capture_time = time.time()
            print(f"   [CAMERA] Captured photo {photos_taken}/{target_photos}")

        elif key == 27:  # ESC
            print("   [CANCEL] Cancelled.")
            cap.release()
            cv2.destroyAllWindows()
            return False

    # Don't release camera yet — we'll use it for the test scan

    print(f"\n   [SUCCESS] {photos_taken} photos captured!")
    print("   [INFO] Building auth database...\n")

    enrolled = enroll_authorized_photos()
    if enrolled == 0:
        print("   [ERROR] Enrollment failed — no faces could be processed.")
        cap.release()
        cv2.destroyAllWindows()
        return False

    # ── Compute adaptive threshold from pairwise scores ──
    print("   [INFO] Computing adaptive threshold from enrollment photos...")
    photo_paths = [os.path.join(AUTHORIZED_DIR, f"face_{i+1}.jpg") for i in range(photos_taken)]
    pairwise_scores = []

    try:
        from deepface import DeepFace
        for i in range(len(photo_paths)):
            for j in range(i + 1, len(photo_paths)):
                emb_i = DeepFace.represent(photo_paths[i], model_name='ArcFace', detector_backend='opencv', enforce_detection=False)[0]['embedding']
                emb_j = DeepFace.represent(photo_paths[j], model_name='ArcFace', detector_backend='opencv', enforce_detection=False)[0]['embedding']
                # Cosine similarity
                dot = sum(a * b for a, b in zip(emb_i, emb_j))
                mag_i = sum(a * a for a in emb_i) ** 0.5
                mag_j = sum(a * a for a in emb_j) ** 0.5
                similarity = dot / (mag_i * mag_j) if mag_i and mag_j else 0
                pairwise_scores.append(similarity)
                print(f"      Photo {i+1} vs Photo {j+1}: {similarity:.4f}")
    except Exception as e:
        print(f"   [WARNING]  Score computation error: {e}")

    if pairwise_scores:
        min_score = min(pairwise_scores)
        avg_score = sum(pairwise_scores) / len(pairwise_scores)
        adaptive_threshold = max(min_score - 0.05, 0.5)  # At least 0.5
        print(f"\n   [INFO] Score range: {min_score:.4f} — {max(pairwise_scores):.4f}")
        print(f"   [INFO] Average self-similarity: {avg_score:.4f}")
        print(f"   [INFO] Adaptive threshold set to: {adaptive_threshold:.4f}")

        with open(THRESHOLD_FILE, "w") as f:
            f.write(str(adaptive_threshold))
    else:
        adaptive_threshold = 0.75
        print(f"   [WARNING]  Could not compute scores. Using default threshold: {adaptive_threshold}")
        with open(THRESHOLD_FILE, "w") as f:
            f.write(str(adaptive_threshold))

    # ── Test scan — verify recognition before finishing ──
    print("\n   [TEST] VERIFICATION TEST")
    print("   Look at the camera — verify the system recognizes you.")
    print()
    print("   SPACE : Test if system recognizes you")
    print("   TAB   : Capture extra training photo (if test fails)")
    print("   ESC   : Finish enrollment\n")

    win_name = "Enrollment Verification"
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(win_name, cv2.WND_PROP_TOPMOST, 1)
    cv2.resizeWindow(win_name, 640, 480)

    test_passed = False
    test_done = False
    extra_photo_count = 0
    last_test_result = None  # None, "pass", "fail"

    while not test_done:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        display = frame.copy()
        h, w = display.shape[:2]

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        # Header
        cv2.rectangle(display, (0, 0), (w, 58), (12, 12, 20), -1)
        cv2.putText(display, "ENROLLMENT VERIFICATION", (14, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 210, 210), 1, cv2.LINE_AA)
        cv2.putText(display, f"Threshold: {adaptive_threshold:.2f}  |  Photos: {photos_taken + extra_photo_count}", (14, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (140, 140, 160), 1, cv2.LINE_AA)

        # Face box
        for (x, y, fw, fh) in faces:
            if last_test_result == "pass":
                color = (0, 230, 130)
            elif last_test_result == "fail":
                color = (60, 60, 230)
            else:
                color = (210, 170, 0)
            cv2.rectangle(display, (x, y), (x + fw, y + fh), color, 2)

        # Status message
        if last_test_result == "pass":
            cv2.rectangle(display, (0, 60), (w, 90), (0, 80, 30), -1)
            cv2.putText(display, "RECOGNIZED - Press ESC to finish", (w // 2 - 155, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 140), 1, cv2.LINE_AA)
        elif last_test_result == "fail":
            cv2.rectangle(display, (0, 60), (w, 90), (0, 0, 80), -1)
            cv2.putText(display, "NOT RECOGNIZED - Press TAB to add training photo", (w // 2 - 210, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (120, 120, 255), 1, cv2.LINE_AA)

        # Footer with controls
        cv2.rectangle(display, (0, h - 42), (w, h), (12, 12, 20), -1)
        if len(faces) > 0:
            cv2.putText(display, "SPACE:Test  TAB:Train more  ESC:Done", (w // 2 - 170, h - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 230, 140), 1, cv2.LINE_AA)
        else:
            cv2.putText(display, "Position your face in the frame", (w // 2 - 140, h - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (100, 100, 230), 1, cv2.LINE_AA)

        cv2.imshow(win_name, display)
        key = cv2.waitKey(1) & 0xFF

        if key == 32 and len(faces) > 0:  # SPACE — test recognition
            test_path = os.path.join("temp_uploads", "enrollment_test.jpg")
            os.makedirs("temp_uploads", exist_ok=True)
            cv2.imwrite(test_path, frame)

            print("   [INFO] Testing recognition...")
            verifier = get_auth_verifier()
            found, matched_name, score = verifier.identify_from_database(test_path, threshold=adaptive_threshold)

            try:
                os.remove(test_path)
            except Exception:
                pass

            if found:
                score_pct = round(float(score) * 100, 1)
                print(f"   [SUCCESS] TEST PASSED! Recognized as '{matched_name}' ({score_pct}%)")
                last_test_result = "pass"
                test_passed = True
            else:
                print(f"   [FAILURE] TEST FAILED — Press TAB to capture a training photo from this angle")
                last_test_result = "fail"

        elif key == 9 and len(faces) > 0:  # TAB — capture extra training photo
            extra_photo_count += 1
            photo_path = os.path.join(AUTHORIZED_DIR, f"face_extra_{extra_photo_count}.jpg")
            cv2.imwrite(photo_path, frame)
            print(f"   [CAMERA] Extra training photo #{extra_photo_count} captured!")

            # Enroll this photo immediately
            verifier = get_auth_verifier()
            success, msg = verifier.enroll_identity(photo_path, user_name)
            if success:
                print(f"   [SUCCESS] Enrolled into auth database")

                # Recalculate adaptive threshold with ALL photos
                all_photos = [os.path.join(AUTHORIZED_DIR, f) for f in os.listdir(AUTHORIZED_DIR)
                              if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
                try:
                    from deepface import DeepFace
                    all_scores = []
                    for i in range(len(all_photos)):
                        for j in range(i + 1, len(all_photos)):
                            emb_i = DeepFace.represent(all_photos[i], model_name='ArcFace', detector_backend='opencv', enforce_detection=False)[0]['embedding']
                            emb_j = DeepFace.represent(all_photos[j], model_name='ArcFace', detector_backend='opencv', enforce_detection=False)[0]['embedding']
                            dot = sum(a * b for a, b in zip(emb_i, emb_j))
                            mag_i = sum(a * a for a in emb_i) ** 0.5
                            mag_j = sum(a * a for a in emb_j) ** 0.5
                            sim = dot / (mag_i * mag_j) if mag_i and mag_j else 0
                            all_scores.append(sim)

                    if all_scores:
                        adaptive_threshold = max(min(all_scores) - 0.05, 0.5)
                        with open(THRESHOLD_FILE, "w") as f:
                            f.write(str(adaptive_threshold))
                        print(f"   [target] Threshold recalibrated: {adaptive_threshold:.4f}")
                except Exception as e:
                    print(f"   [WARNING]  Recalibration error: {e}")

                last_test_result = None  # Reset — try test again
                print("   → Now press SPACE to test again!\n")
            else:
                print(f"   [WARNING]  Enroll failed: {msg}")

        elif key == 27:  # ESC — done
            test_done = True

    cap.release()
    cv2.destroyAllWindows()

    total_photos = photos_taken + extra_photo_count
    if test_passed:
        print(f"\n   [SUCCESS] Enrollment complete! '{user_name}' verified with {total_photos} photos.")
        print(f"   [target] Adaptive threshold: {adaptive_threshold:.4f}\n")
    else:
        print(f"\n   [SUCCESS] Enrollment saved with {total_photos} photos.")
        print(f"   [target] Threshold: {adaptive_threshold:.4f}")
        print(f"   [INFO] Run --enroll again to recalibrate if needed.\n")
    return True


# ═══════════════════════════════════════════════════════
#  FACE SCAN AGENT — Auto-identifies faces continuously
# ═══════════════════════════════════════════════════════

def run_face_scan_agent():
    """
    OpenCV webcam window with auto-recognition.
    Uses the SHARED auth verifier instance.
    - Recognized → shows name + 'Press SPACE to continue'
    - Not recognized → shows 'UNREGISTERED USER'
    Returns (authenticated: bool, user_name: str or None).
    """
    import cv2

    print()
    print("-" * 55)
    print("  [AUTH]  BIOMETRIC AUTHENTICATION")
    print("  -----------------------------")
    print("  Stand in front of the camera.")
    print("  The system will identify you automatically.")
    print("  Press ESC to use backup password instead.")
    print("-" * 55)
    print()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("  [ERROR] Cannot open webcam!")
        return False, None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    win_name = "Biometric Authentication"
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(win_name, cv2.WND_PROP_TOPMOST, 1)
    cv2.resizeWindow(win_name, 640, 480)

    authenticated = False
    auth_user = None
    frame_count = 0

    # Auto-scan state
    is_scanning = False
    last_scan_time = 0
    scan_cooldown = 3.0
    current_identity = None
    identity_time = 0

    # Use the SHARED verifier (same instance that enrolled the photos)
    print("  [INFO] Loading recognition model...")
    verifier = get_auth_verifier()

    # Load adaptive threshold
    adaptive_threshold = 0.75  # fallback default
    if os.path.exists(THRESHOLD_FILE):
        try:
            with open(THRESHOLD_FILE, "r") as f:
                adaptive_threshold = float(f.read().strip())
            print(f"  [target] Adaptive threshold loaded: {adaptive_threshold:.4f}")
        except Exception:
            pass

    # Verify data is actually in the collection
    try:
        info = verifier.db_client.get_collection(AUTH_COLLECTION)
        print(f"  [SUCCESS] Model ready. Auth DB has {info.points_count} enrolled faces.\n")
    except Exception:
        print("  [SUCCESS] Model ready.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        display = frame.copy()
        h, w = display.shape[:2]
        frame_count += 1

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        # Header bar
        cv2.rectangle(display, (0, 0), (w, 52), (12, 12, 20), -1)
        cv2.putText(display, "BIOMETRIC AUTHENTICATION", (14, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 210, 210), 1, cv2.LINE_AA)
        cv2.putText(display, "Identity Verification System", (14, 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 100, 120), 1, cv2.LINE_AA)

        # Pulsing LIVE indicator
        pulse = abs((frame_count % 60) - 30) / 30.0
        dot_color = (0, int(160 + 95 * pulse), 0)
        cv2.circle(display, (w - 22, 26), 7, dot_color, -1)
        cv2.putText(display, "LIVE", (w - 60, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 200, 0), 1, cv2.LINE_AA)

        # Face tracking with corner brackets
        for (x, y, fw, fh) in faces:
            if current_identity and current_identity["found"]:
                color = (0, 230, 130)   # Green
            elif current_identity and not current_identity["found"]:
                color = (60, 60, 230)   # Red
            else:
                color = (210, 170, 0)   # Cyan

            cl = 25
            t = 2
            cv2.line(display, (x, y), (x + cl, y), color, t, cv2.LINE_AA)
            cv2.line(display, (x, y), (x, y + cl), color, t, cv2.LINE_AA)
            cv2.line(display, (x + fw, y), (x + fw - cl, y), color, t, cv2.LINE_AA)
            cv2.line(display, (x + fw, y), (x + fw, y + cl), color, t, cv2.LINE_AA)
            cv2.line(display, (x, y + fh), (x + cl, y + fh), color, t, cv2.LINE_AA)
            cv2.line(display, (x, y + fh), (x, y + fh - cl), color, t, cv2.LINE_AA)
            cv2.line(display, (x + fw, y + fh), (x + fw - cl, y + fh), color, t, cv2.LINE_AA)
            cv2.line(display, (x + fw, y + fh), (x + fw, y + fh - cl), color, t, cv2.LINE_AA)

        # Auto-scan trigger
        now = time.time()
        if len(faces) > 0 and not is_scanning and (now - last_scan_time) > scan_cooldown:
            is_scanning = True
            last_scan_time = now

            temp_path = os.path.join("temp_uploads", "scan_auth.jpg")
            os.makedirs("temp_uploads", exist_ok=True)
            cv2.imwrite(temp_path, frame)

            def do_auto_scan():
                nonlocal is_scanning, current_identity, identity_time
                try:
                    found, user_id, score = verifier.identify_from_database(temp_path, threshold=adaptive_threshold)
                    score_val = float(score) if isinstance(score, (int, float)) else 0.0
                    current_identity = {
                        "found": found,
                        "user_id": user_id,
                        "score": score_val,
                        "confidence": round(score_val * 100, 1) if found else 0.0
                    }
                    identity_time = time.time()
                except Exception as e:
                    print(f"   [WARNING] Scan error: {e}")
                    import traceback
                    traceback.print_exc()
                    current_identity = {"found": False, "user_id": None, "score": 0, "confidence": 0}
                    identity_time = time.time()
                finally:
                    is_scanning = False
                    try:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                    except Exception:
                        pass

            # Run synchronously to avoid Qdrant local file threading issues
            do_auto_scan()

        # Scanning animation
        if is_scanning:
            elapsed = now - last_scan_time
            scan_y = int(60 + (h - 120) * ((elapsed * 1.8) % 1.0))
            cv2.line(display, (20, scan_y), (w - 20, scan_y), (0, 245, 200), 2, cv2.LINE_AA)

            overlay = display.copy()
            cv2.rectangle(overlay, (20, scan_y - 12), (w - 20, scan_y + 12), (0, 245, 200), -1)
            cv2.addWeighted(overlay, 0.06, display, 0.94, 0, display)

            cv2.rectangle(display, (w // 2 - 80, h - 55), (w // 2 + 80, h - 30), (12, 12, 20), -1)
            cv2.putText(display, "ANALYZING...", (w // 2 - 58, h - 39),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 245, 200), 1, cv2.LINE_AA)

        # Identity display
        elif current_identity is not None:
            if current_identity["found"]:
                # RECOGNIZED
                user = current_identity["user_id"]
                conf = current_identity["confidence"]

                cv2.rectangle(display, (0, h - 95), (w, h), (0, 100, 40), -1)

                cv2.putText(display, f"{user}", (w // 2 - len(user) * 8, h - 68),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 140), 2, cv2.LINE_AA)

                cv2.putText(display, f"Confidence: {conf}%", (w // 2 - 70, h - 42),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 255, 200), 1, cv2.LINE_AA)

                # Blinking "Press SPACE"
                if (frame_count // 20) % 2 == 0:
                    cv2.putText(display, "Press SPACE to continue", (w // 2 - 115, h - 12),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

                # Confidence bar
                bar_x, bar_y, bar_w, bar_h = 20, h - 5, w - 40, 4
                cv2.rectangle(display, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (30, 30, 40), -1)
                fill_w = int(bar_w * min(conf / 100.0, 1.0))
                cv2.rectangle(display, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), (0, 230, 130), -1)

            else:
                # UNREGISTERED USER
                cv2.rectangle(display, (0, h - 70), (w, h), (0, 0, 100), -1)

                cv2.putText(display, "UNREGISTERED USER", (w // 2 - 125, h - 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (80, 80, 255), 2, cv2.LINE_AA)

                cv2.putText(display, "ESC for backup password  |  Rescanning...",
                            (w // 2 - 185, h - 12),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 255), 1, cv2.LINE_AA)

        else:
            # Waiting
            cv2.rectangle(display, (0, h - 38), (w, h), (12, 12, 20), -1)
            if len(faces) > 0:
                cv2.putText(display, "Identifying...", (w // 2 - 60, h - 12),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (130, 130, 150), 1, cv2.LINE_AA)
            else:
                cv2.putText(display, "Look at the camera  |  ESC: Cancel", (w // 2 - 155, h - 12),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (130, 130, 150), 1, cv2.LINE_AA)

        cv2.imshow(win_name, display)
        key = cv2.waitKey(1) & 0xFF

        # SPACE → proceed (only if recognized)
        if key == 32 and current_identity and current_identity["found"]:
            authenticated = True
            auth_user = current_identity["user_id"]
            break

        # ESC → cancel
        elif key == 27:
            print("   [CANCEL] Face scan cancelled.")
            break

    cap.release()
    cv2.destroyAllWindows()
    return authenticated, auth_user


# ═══════════════════════════════════════════════════════
#  SERVER
# ═══════════════════════════════════════════════════════

def wait_for_server(timeout=30):
    import urllib.request
    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(URL, timeout=2)
            return True
        except Exception:
            time.sleep(0.5)
    return False


# ═══════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════

def main():
    print_banner()
    os.chdir(SCRIPT_DIR)

    force_enroll = "--enroll" in sys.argv

    # ── Check if enrolled ──
    has_photos = False
    if os.path.isdir(AUTHORIZED_DIR):
        photos = [f for f in os.listdir(AUTHORIZED_DIR) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
        has_photos = len(photos) > 0

    if not has_photos or force_enroll:
        print("[NEW] First-time setup: biometric enrollment required.")
        print("   Your face will be stored in a separate auth database.\n")

        if not enroll_self_via_webcam():
            print("[ERROR] Enrollment failed. Cannot proceed.")
            return
    else:
        # Re-enroll photos into auth DB if needed
        print("[KEY] Loading auth database...")
        try:
            verifier = get_auth_verifier()
            try:
                info = verifier.db_client.get_collection(AUTH_COLLECTION)
                if info.points_count > 0:
                    print(f"   [SUCCESS] Auth database has {info.points_count} enrolled photos.")
                else:
                    enroll_authorized_photos()
            except Exception:
                enroll_authorized_photos()
        except Exception as e:
            print(f"   [WARNING]  Cannot initialize database: {e}")
            return

    # ── Step 1: Face Scan Agent ──
    print()
    print("[STEP 1] BIOMETRIC AUTHENTICATION")
    face_matched, auth_user = run_face_scan_agent()

    # ── Step 2: Password (always required) ──
    authenticated = False
    if os.path.exists(PASSWORD_FILE):
        print()
        if face_matched:
            print(f"[LOCKED] Face recognized: {auth_user}")
            print("   Password verification required (2-factor auth).")
        else:
            print("[LOCKED] Face scan was not successful.")
            print("   Enter your password to authenticate.")
        print()

        with open(PASSWORD_FILE, "r") as f:
            stored_hash = f.read().strip()

        for attempt in range(3):
            pw = input(f"  Enter password (attempt {attempt + 1}/3): ")
            if hashlib.sha256(pw.encode()).hexdigest() == stored_hash:
                authenticated = True
                if not auth_user:
                    name_file = os.path.join(AUTHORIZED_DIR, "name.txt")
                    if os.path.exists(name_file):
                        with open(name_file, "r") as f:
                            auth_user = f.read().strip()
                    else:
                        auth_user = "Authorized User"
                print(f"  [SUCCESS] Password accepted! Welcome, {auth_user}.")
                break
            else:
                remaining = 2 - attempt
                if remaining > 0:
                    print(f"  [ERROR] Wrong password. {remaining} attempt(s) remaining.")

    if not authenticated:
        print()
        print("🚫 ACCESS DENIED.")
        print("   💡 Run 'python launch.py --enroll' to re-enroll.")
        input("\n   Press Enter to exit...")
        return

    # ── Step 2: Seed main database + launch server ──
    print()
    print(f"✅ Welcome, {auth_user}!")
    print()
    print("🌐 STEP 2: Launching dashboard...")

    # Close auth verifier before seeding main DB (releases file lock)
    close_auth_verifier()

    seed_main_database()

    print(f"\n🚀 Starting server at {URL}...")

    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", str(PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    print("⏳ Waiting for server...")
    if wait_for_server():
        print("✅ Server ready!")
        webbrowser.open(URL)

        print()
        print("━" * 55)
        print(f"  🎯  Dashboard is live — Welcome, {auth_user}!")
        print(f"  🔗  {URL}")
        print("  🛑  Ctrl+C to stop.")
        print("━" * 55)
        print()
    else:
        print("❌ Server failed to start.")
        server_process.terminate()
        return

    try:
        for line in server_process.stdout:
            decoded = line.decode('utf-8', errors='replace').strip()
            if decoded:
                print(f"  [server] {decoded}")
    except KeyboardInterrupt:
        pass
    finally:
        print("\n🛑 Shutting down...")
        server_process.terminate()
        server_process.wait(timeout=5)

        # Clean up auth database
        print("🧹 Clearing auth database...")
        try:
            from qdrant_client import QdrantClient
            client = QdrantClient(path=QDRANT_PATH)
            client.delete_collection(AUTH_COLLECTION)
            client.close()
            print("   ✅ Auth database cleared.")
        except Exception:
            pass

        print("👋 Goodbye!")


if __name__ == "__main__":
    main()
