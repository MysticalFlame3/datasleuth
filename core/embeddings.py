from fastembed import TextEmbedding

class EmbeddingService:
    def __init__(self):
        # BAAI/bge-m3 generates dense vectors of dim 1024
        # fastembed runs purely on CPU locally
        print("Initializing BGE-Base local embedding model...")
        self.model = TextEmbedding(model_name="BAAI/bge-base-en-v1.5")

    def embed_text(self, text: str):
        # Generate dense embeddings (FastEmbed returns an iterator of arrays)
        embeddings = list(self.model.embed([text]))
        return embeddings[0].tolist()

embedding_service = EmbeddingService()

if __name__ == "__main__":
    test_text = "This is a sample document for DataSleuth."
    dense_vector = embedding_service.embed_text(test_text)
    print(f"Generated dense vector of length: {len(dense_vector)}")
    print(f"First 5 dimensions: {dense_vector[:5]}")
