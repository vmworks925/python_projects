import cohere
from pinecone import Pinecone

class EmbeddingSearchService:
    def __init__(self, cohere_api_key, pinecone_api_key, index_name):
        self.co = cohere.Client(cohere_api_key)
        self.pc = Pinecone(api_key=pinecone_api_key)
        self.index = self.pc.Index(index_name)

    def embed_query(self, query: str):
        resp = self.co.embed(
            texts=[query],
            model="embed-english-light-v3.0",
            input_type="search_query"
        )
        return resp.embeddings[0]

    def search(self, query: str, top_k: int = 3):
        query_vec = self.embed_query(query)
        result = self.index.query(
            vector=query_vec,
            top_k=top_k,
            include_metadata=True
        )
        return [
            {
                "score": match.score,
                "text": match.metadata.get("text", "")
            }
            for match in result.matches
        ]