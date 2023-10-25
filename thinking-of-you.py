import openai
import pinecone

# Set OpenAI API key
openai.api_key = "YOUR-OPENAI-KEY"

# Initialize Pinecone
PINECONE_API_KEY = "YOUR-PINECONE-API-KEY"
pinecone.init(api_key=PINECONE_API_KEY, environment="gcp-starter")

def create_embedding(query):
    response = openai.Embedding.create(
        input=query,
        model="text-embedding-ada-002"
    )
    return response["data"][0]["embedding"]

def generate_phrase_with_openai():
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Without any comment or subject line, generate a message capturing a scenario in which someone is reaching out to tell me they've been thinking of me due to a fictional memory. Respond in 2-3 sentences with no carriage returns, and make sure your message is thoughtful, personal and describes a specific anecdote and compliment or positive attribute."}
        ]
    )
    return response.choices[0].message["content"].strip()

def select_best_context_with_openai(response):
    text_chunks = "\n\n".join([match['metadata']['text'] for match in response["matches"]])
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"From the following text chunks, select a single quote that's personal, directed to me, memorable, meaningful, not negative, and under 150 characters. Nothing too private. Respond without comment or carriage returns. No need for quotation marks, but do not rephrase or edit the verbatim you've selected: \n\n{text_chunks}"}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    return response.choices[0].message["content"].strip()

def search_in_pinecone(query_embedding, index_name="semanticsearch", num_results=5):
    index = pinecone.Index(index_name=index_name)
    results = index.query(query_embedding, k=num_results, top_k=num_results, include_metadata=True)
    return results

if __name__ == "__main__":
    # Generate a semantically similar phrase using OpenAI
    generated_phrase = generate_phrase_with_openai()
    
    # Convert the generated phrase into an embedding
    query_embedding = create_embedding(generated_phrase)

    # Search the Pinecone index using the embedding
    search_results = search_in_pinecone(query_embedding)

    # Process the search results with OpenAI to get the highest quality context
    best_context = select_best_context_with_openai(search_results)
    
    # Print the best context
    print(best_context)
