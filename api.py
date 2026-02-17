from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel
import shutil
import os
import uuid
import base64
from verifier import IdentityVerifier

import time
from contextlib import asynccontextmanager

# Global verifier instance
verifier = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global verifier
    print("[INFO] Initializing Identity Verifier Model...")
    
    try:
        verifier = IdentityVerifier()
        print("[SUCCESS] Model Initialized!")
    except Exception as e:
        print(f"[ERROR] Failed to initialize verifier: {e}")
    
    yield
    print("[INFO] Shutting down...")

app = FastAPI(title="Identity Verification API", lifespan=lifespan)

# Create temp directory for uploads
os.makedirs("temp_uploads", exist_ok=True)

# Mount templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def save_upload(file: UploadFile) -> str:
    file_ext = file.filename.split(".")[-1]
    filename = f"temp_uploads/{uuid.uuid4()}.{file_ext}"
    with open(filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return filename

# --- Webcam Scan Endpoint (base64 frame) ---

class ScanRequest(BaseModel):
    image: str  # base64-encoded image data

@app.post("/scan")
async def scan_face(req: ScanRequest):
    """Accept a base64-encoded webcam frame and identify the person."""
    file_path = None
    try:
        # Decode base64 image
        # Remove data URL prefix if present (e.g., "data:image/jpeg;base64,")
        image_data = req.image
        if "," in image_data:
            image_data = image_data.split(",", 1)[1]
        
        img_bytes = base64.b64decode(image_data)
        
        # Save to temp file
        file_path = f"temp_uploads/{uuid.uuid4()}.jpg"
        with open(file_path, "wb") as f:
            f.write(img_bytes)
        
        # Run identification
        found, user_id, score = verifier.identify_from_database(file_path)
        
        # Ensure score is always a float
        if isinstance(score, (int, float)):
            score_value = float(score)
        else:
            score_value = 0.0
        
        return JSONResponse(content={
            "found": found,
            "user_id": user_id,
            "score": score_value,
            "confidence": round(score_value * 100, 1) if found else 0.0
        })
    except Exception as e:
        return JSONResponse(content={
            "found": False,
            "user_id": None,
            "score": 0.0,
            "confidence": 0.0,
            "error": str(e)
        })
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

# --- Database Stats Endpoint ---

@app.get("/db-stats")
async def db_stats():
    """Return database statistics."""
    try:
        info = verifier.db_client.get_collection(verifier.db_collection)
        return JSONResponse(content={
            "total_faces": info.points_count,
            "collection": verifier.db_collection,
            "status": "online"
        })
    except Exception as e:
        return JSONResponse(content={
            "total_faces": 0,
            "collection": "unknown",
            "status": "offline",
            "error": str(e)
        })

# --- Original Endpoints ---

@app.post("/enroll")
async def enroll_user(name: str = Form(...), file: UploadFile = File(...)):
    file_path = save_upload(file)
    try:
        success, message = verifier.enroll_identity(file_path, name)
        return JSONResponse(content={"success": success, "message": message})
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/verify")
async def verify_identity(id_card: UploadFile = File(...), selfie: UploadFile = File(...)):
    path1 = save_upload(id_card)
    path2 = save_upload(selfie)
    try:
        result = verifier.verify_1_to_1(path1, path2)
        # Convert numpy booleans to python bools for JSON serialization
        if 'verified' in result:
            result['verified'] = bool(result['verified'])
        return JSONResponse(content=result)
    finally:
        if os.path.exists(path1): os.remove(path1)
        if os.path.exists(path2): os.remove(path2)

@app.post("/identify")
async def identify_user(file: UploadFile = File(...)):
    file_path = save_upload(file)
    try:
        found, user_id, score = verifier.identify_from_database(file_path)
        # Ensure score is always a float
        if isinstance(score, (int, float)):
            score_value = float(score)
        else:
            score_value = 0.0
        
        return JSONResponse(content={
            "found": found,
            "user_id": user_id,
            "score": score_value
        })
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

