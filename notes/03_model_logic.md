# Model Logic & Algorithms

## 1. The Core Concept: Embeddings
Facial recognition doesn't compare images pixel-by-pixel (which would fail with different lighting or angles). Instead, it converts a face into a **Vector Embedding**.

*   **What is an Embedding?**
    It is a list of numbers (e.g., `[0.12, -0.5, 0.88, ...]`) that represents the *features* of a face (distance between eyes, nose shape, jawline).
*   **Dimensionality**: We use **ArcFace**, which generates a **512-dimensional vector**.

## 2. The Model: ArcFace
We utilize **ArcFace** (Additive Angular Margin Loss), one of the most accurate open-source face recognition models.
*   **Why ArcFace?** It is designed to maximize the distance between different people and minimize the distance between images of the same person in the vector space.
*   **Accuracy**: Achieves >99% accuracy on standard benchmarks (LFW).

## 3. Similarity Metric: Cosine Similarity
To compare two faces, we calculate the **Cosine Similarity** between their embeddings.

$$
\text{Cosine Similarity} (A, B) = \frac{A \cdot B}{\|A\| \|B\|}
$$

*   **Range**: -1 to 1.
*   **Interpretation**:
    *   **1.0**: Identical vectors (Same person).
    *   **0.0**: Orthogonal vectors (Completely different).
    *   **-1.0**: Opposite vectors.

**Thresholding**:
We set a threshold (e.g., **0.4** or **0.5**).
*   If Score > Threshold $\rightarrow$ **Verified**.
*   If Score < Threshold $\rightarrow$ **Not Verified**.

## 4. Vector Search (Qdrant)
For **Identification (1:N)**, we don't just compare two images. We compare one image against *millions* in a database.
*   **HNSW Algorithm**: Qdrant uses Hierarchical Navigable Small World graphs to find the "nearest neighbors" (closest vectors) extremely fast, without scanning the entire database.
