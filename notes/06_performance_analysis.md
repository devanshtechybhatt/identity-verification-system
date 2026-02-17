# Performance Analysis & Time Complexity

## 1. Why was it slow?
The initial version used **RetinaFace** for face detection.
*   **Pros**: Extremely accurate, can detect tiny faces.
*   **Cons**: Very computationally expensive ($O(N^2)$ in some layers due to large receptive fields).
*   **Impact**: On a standard CPU, it takes **2-3 seconds** just to find the face before recognition even starts.

## 2. Optimization: Switching to OpenCV (Haar Cascades)
We switched the detector to **OpenCV** (Haar Cascades) or **SSD** (Single Shot Detector).
*   **Impact**: Detection time drops to **~0.05 - 0.2 seconds**.
*   **Trade-off**: Slightly lower accuracy for difficult angles, but perfect for ID cards and selfies which are usually front-facing.

## 3. Time Complexity Analysis (Big O)

The total time complexity for one verification request is:

$$ T_{total} = T_{detection} + T_{embedding} + T_{search} $$

### A. Face Detection ($T_{detection}$)
*   **Algorithm**: Sliding Window (Haar Cascades).
*   **Complexity**: $O(W \times H)$, where $W, H$ are image dimensions.
*   **Optimization**: We resize images before processing to keep $W, H$ constant.

### B. Embedding Generation ($T_{embedding}$)
*   **Algorithm**: ArcFace (ResNet-100 architecture).
*   **Complexity**: $O(L \times K^2 \times C)$, where $L$ is layers, $K$ is kernel size, $C$ is channels.
*   **Practical**: It's a fixed forward pass through a neural network. Constant time $O(1)$ relative to database size, but computationally heavy.

### C. Vector Search ($T_{search}$)
*   **Algorithm**: HNSW (Hierarchical Navigable Small World) in Qdrant.
*   **Naive Search**: $O(N \times D)$ (checking every vector).
*   **HNSW Search**: $O(\log(N))$.
    *   $N$: Number of users in database.
    *   $D$: Dimensions (512).
*   **Benefit**: Even with 1 million users, search remains extremely fast (milliseconds).

## 4. Summary Table

| Operation | Original Time | Optimized Time | Complexity |
| :--- | :--- | :--- | :--- |
| **Face Detection** | ~2.5s | **~0.1s** | $O(Pixels)$ |
| **Embedding** | ~0.5s | ~0.5s | $O(1)$ |
| **Search** | ~0.01s | ~0.01s | $O(\log N)$ |
| **Total** | **~3.0s** | **~0.6s** | **Fast** |
