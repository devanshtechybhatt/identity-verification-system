# [LOCK] Identity Verification System

A facial recognition system with biometric authentication, powered by DeepFace (ArcFace) and Qdrant vector database.

## Features

- **Biometric Authentication** — OpenCV webcam agent scans your face before granting access
- **Auto-Recognition** — Continuously identifies faces and shows your name or "Unregistered User"
- **Backup Password** — Fallback authentication if face scan fails
- **Web Dashboard** — Premium glassmorphism UI with live webcam scanner, enrollment, 1:1 verification, and 1:N identification
- **Pre-Seeded Database** — 15 faces from LFW dataset loaded automatically
- **100% Local** — No Docker, no cloud, all data stored locally

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run
python launch.py
```

That's it. On first run, you'll:
1. Enter your name and set a backup password
2. Take 3 photos to create your biometric profile
3. The face scan agent opens — it recognizes you automatically
4. Press SPACE → the web dashboard opens in your browser

## Usage

| Command | Description |
|---------|-------------|
| `python launch.py` | Run the system (enroll on first launch) |
| `python launch.py --enroll` | Re-enroll your face |

## How It Works

```
python launch.py
       │
       ▼
┌─────────────────┐
│  First run?     │──Yes──▶ Webcam enrollment (3 photos)
│                 │         + set backup password
└────────┬────────┘
         │ No
         ▼
┌─────────────────┐
│  Face Scan Agent│──▶ Auto-identifies your face
│  (OpenCV window)│    [SUCCESS] Your Name -> Press SPACE
│                 │    [FAILURE] UNREGISTERED USER
└────────┬────────┘
         │ ESC?
         ▼
┌─────────────────┐
│ Backup Password │──▶ 3 attempts
└────────┬────────┘
         │ Verified
         ▼
┌─────────────────┐
│  Web Dashboard  │──▶ http://localhost:8000
│  (auto-opens)   │
└─────────────────┘
         │ Ctrl+C
         ▼
   Auth DB cleared
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Face Recognition | DeepFace (ArcFace model) |
| Vector Database | Qdrant (local file-based) |
| Backend API | FastAPI + Uvicorn |
| Frontend | HTML/CSS/JS (glassmorphism) |
| Authentication | OpenCV + Haar Cascade |
| Embeddings | 512-dim vectors, cosine similarity |

## Project Structure

```
identity_verification_system/
├── launch.py              # One-click launcher (entry point)
├── verifier.py            # Core face recognition logic
├── api.py                 # FastAPI endpoints
├── templates/
│   └── index.html         # Web dashboard UI
├── dataset/
│   ├── lfw-deepfunneled/  # LFW face dataset
│   └── authorized_users/  # Your enrolled photos
├── qdrant_data/           # Local vector database (auto-created)
├── requirements.txt       # Python dependencies
└── notes/                 # Documentation
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/enroll` | Enroll a new face |
| POST | `/verify` | 1:1 face verification |
| POST | `/identify` | 1:N face identification |
| POST | `/scan` | Webcam base64 frame scan |
| GET | `/db-stats` | Database statistics |

## Recognition Threshold

The system uses a **65% cosine similarity threshold** — a face must match with ≥65% confidence to be identified. This balances accuracy with practical usability.

## Requirements

- Python 3.10+
- Webcam
- ~500MB disk space (for TensorFlow + models)
