# API Documentation

## Base URL
`http://localhost:8000`

## Endpoints

### 1. Health Check / UI
*   **URL**: `/`
*   **Method**: `GET`
*   **Description**: Returns the simple HTML frontend to test the system.

### 2. Enroll User
*   **URL**: `/enroll`
*   **Method**: `POST`
*   **Description**: Adds a user's face to the database.
*   **Parameters**:
    *   `name` (Form Data): Name of the user.
    *   `file` (File): Image containing the user's face.
*   **Response**:
    ```json
    {
      "success": true,
      "message": "User John Doe enrolled successfully."
    }
    ```

### 3. Verify Identity (1:1)
*   **URL**: `/verify`
*   **Method**: `POST`
*   **Description**: Compares two uploaded images to see if they are the same person.
*   **Parameters**:
    *   `id_card` (File): Image of the ID document.
    *   `selfie` (File): Live photo of the user.
*   **Response**:
    ```json
    {
      "verified": true,
      "distance": 0.34,
      "threshold": 0.68,
      "model": "ArcFace",
      "similarity_metric": "cosine"
    }
    ```

### 4. Identify User (1:N)
*   **URL**: `/identify`
*   **Method**: `POST`
*   **Description**: Searches the database to find who the person in the image is.
*   **Parameters**:
    *   `file` (File): Image to search for.
*   **Response**:
    ```json
    {
      "found": true,
      "user_id": "John Doe",
      "score": 0.89
    }
    ```
