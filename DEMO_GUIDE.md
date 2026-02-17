# Professor Demo Guide

## Quick Start

Run the comprehensive demo to showcase all functionality:

```bash
# Make sure Docker is running
docker-compose up -d

# Wait 10 seconds for services to start, then run:
docker exec identity_verification_system-app-1 python professor_demo.py
```

## What the Demo Shows

### 1. **Enrollment (1:N Setup)**
- Adds 3 users to the database
- Shows face → vector embedding conversion
- Demonstrates Qdrant storage

### 2. **Verification (1:1 Matching)**
- Compares ID card vs Selfie
- Shows Cosine Similarity calculation
- Displays match/no-match decision

### 3. **Identification (1:N Search)**
- Searches database for a person
- Demonstrates HNSW fast search
- Shows similarity scores

## Expected Output

The script will display:
- [SUCCESS] Success indicators
- [TIME] Time measurements for each operation
- [STATS] Performance statistics
- [SEARCH] Detailed results with similarity scores

## Key Points for Presentation

1. **Speed**: ~0.6s per operation (optimized with OpenCV detector)
2. **Scalability**: O(log N) search time with HNSW algorithm
3. **Accuracy**: Uses ArcFace model (>99% accuracy on benchmarks)
4. **Architecture**: Microservices with Docker + FastAPI + Qdrant

## Documentation Reference

Point your professor to:
- `notes/01_project_overview.md` - Problem statement
- `notes/02_system_architecture.md` - System design
- `notes/03_model_logic.md` - AI/ML explanation
- `notes/06_performance_analysis.md` - Time complexity analysis
