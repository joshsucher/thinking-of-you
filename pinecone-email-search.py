import openai
import pinecone

# Set OpenAI API key
openai.api_key = "YOUR-OPENAI-KEY"

# Initialize Pinecone
PINECONE_API_KEY = "YOUR-PINECONE-KEY"
pinecone.init(api_key=PINECONE_API_KEY, environment="gcp-starter")

def create_embedding(query):
    """
    Create an embedding using OpenAI API based on a given query.
    """
    response = openai.Embedding.create(
        input=query,
        model="text-embedding-ada-002"
    )
    return response["data"][0]["embedding"]

def search_in_pinecone(query_embedding, index_name="semanticsearch", num_results=5):
    """
    Search indexed data in Pinecone based on an embedding.
    """
    index = pinecone.Index(index_name=index_name)
    results = index.query(query_embedding, k=num_results, top_k=num_results, include_metadata=True)
    
    return results

if __name__ == "__main__":
    query = input("Enter your search query: ")

    # Convert the query into an embedding
    query_embedding = create_embedding(query)

    # Search the Pinecone index using the embedding
    search_results = search_in_pinecone(query_embedding)
    
    # Display the search results
    print("\nSearch results for the query:", query)
    for match in search_results["matches"]:
        print(f"Text chunk: {match['metadata']['text']}")
        print(f"Similarity score: {match['score']}")
        print("\n")
