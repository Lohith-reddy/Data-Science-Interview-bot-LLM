import os
import openai
import qdrant_client
from langchain.document_loaders import PyPDFLoader

# Initialise Qdrant
client = qdrant_client.QdrantClient("http://localhost:6333")
client.get_collections()


def load_pdfs(path):
    loader = PyPDFLoader(path)
    pages = loader.load()
    pdf_content = "\n".join([page.page_content for page in pages])
    return pdf_content


def remove_surrogates(text):
    return text.encode('utf-8', 'ignore').decode('utf-8')


def create_embeddings(files):

    openai.api_key = os.getenv("OPENAI_API_KEY")
    embedding_model = "text-embedding-ada-002"
    vectors = openai.Embedding.create(input="The best vector database",
                                      model=embedding_model
                                     )
    return vectors


pdf_chunks = []


for path in os.listdir("data"):
    print("Processing file: ", path)
    if path.endswith(".pdf"):
        pdf_content = load_pdfs(os.path.join("data", path))
        splitted_text = get_chunks(pdf_content)
        clean_text = [remove_surrogates(text) for text in splitted_text]
        pdf_chunks.extend(clean_text)


# Initialise embeddings - we can alternatively chose one of many different open-source embeddings
# Initialize model
# model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")


client.add(
    collection_name="griller_qdrant",
    documents=pdf_chunks
)

# add a snapshot of the collection to snapshot_bucket
