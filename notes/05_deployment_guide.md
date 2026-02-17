# Deployment Guide

## Prerequisites
*   **Docker Desktop** installed and running.
*   **Git** (optional, for cloning).

## Quick Start

1.  **Navigate to Project Directory**:
    ```bash
    cd identity_verification_system
    ```

2.  **Build and Run**:
    We use `docker-compose` to orchestrate the API and the Database.
    ```bash
    docker-compose up --build
    ```
    *   `--build`: Forces a rebuild of the Docker image (useful if you changed code).
    *   The first run will take time to download the base Python image and install dependencies.

3.  **Access the Application**:
    *   Open your browser to: [http://localhost:8000](http://localhost:8000)
    *   You should see the "Identity Verification System" interface.

## Troubleshooting

### "Failed to connect to Qdrant"
*   **Cause**: The `qdrant` service hasn't started yet when the `app` tries to connect.
*   **Fix**: The application has a built-in retry mechanism. Wait a few seconds, and it should connect automatically.

### "No face detected"
*   **Cause**: The image quality is too low, or the face is obscured.
*   **Fix**: Ensure the image has good lighting and the face is fully visible.

### Docker Build Fails
*   **Common Issue**: Network timeouts during `pip install`.
*   **Fix**: Check your internet connection and try running `docker-compose build` again.
