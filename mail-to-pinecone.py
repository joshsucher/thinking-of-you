import openai
import pinecone
import uuid
import tiktoken
import json

openai.api_key = "YOUR-OPENAI-API-KEY"
pinecone.init(api_key="YOUR-PINECONE-API-KEY", environment="gcp-starter")

def count_tokens(text):
    encoding = tiktoken.encoding_for_model("text-embedding-ada-002")
    return len(encoding.encode(text))

def create_email_embeddings(emails_by_sender):
    email_texts = []
    senders = []
    for sender, email_list in emails_by_sender.items():
        for email in email_list:
            if count_tokens(email) <= 512:  # Ensure the email doesn't exceed token limit
                email_texts.append(email)
                senders.append(sender)

    embeddings = []
    for i, email in enumerate(email_texts):
        print(f"Converting email {i+1}/{len(email_texts)} to embedding...")
        try:
            response = openai.Embedding.create(
                input=email,
                model="text-embedding-ada-002"
            )
            embeddings.append(response["data"][0]["embedding"])
        except Exception as e:
            print(f"Error on email {i+1}: {e}")
    return embeddings, email_texts, senders

def store_in_pinecone(embeddings, emails, senders):
    index_name = "semanticsearch"
    # Check if index already exists
    if index_name not in pinecone.list_indexes():
        print("Creating Pinecone index...")
        pinecone.create_index(name=index_name, metric="cosine", dimension=1536)
    
    pinecone_index = pinecone.Index(index_name=index_name)
    print("Storing embeddings in Pinecone...")
    for embedding, email, sender in zip(embeddings, emails, senders):
        id = uuid.uuid4().hex
        pinecone_index.upsert([(id, embedding, {
            "text": email, "sender": sender
        })])
    print("Done storing embeddings!")

if __name__ == "__main__":
    try:
        with open('processed_emails.json', 'r') as f:
            print("Loading JSON data...")
            emails_by_sender = json.load(f)
        
        print("Converting emails to embeddings...")
        email_embeddings, email_texts, email_senders = create_email_embeddings(emails_by_sender)
        
        store_in_pinecone(email_embeddings, email_texts, email_senders)
        print("All operations completed successfully!")
    except Exception as e:
        print(f"Error: {e}")
