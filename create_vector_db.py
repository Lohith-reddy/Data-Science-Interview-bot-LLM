import os
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from utils import load_pdfs, get_chunks


def remove_surrogates(text):
    return text.encode('utf-8', 'ignore').decode('utf-8')


pdf_chunks = []


for path in os.listdir("data"):
    print("Processing file: ", path)
    if path.endswith(".pdf"):
        pdf_content = load_pdfs(os.path.join("data", path))
        splitted_text = get_chunks(pdf_content)
        clean_text = [remove_surrogates(text) for text in splitted_text]
        pdf_chunks.extend(clean_text)

# need to implement markdown reader. Problem with NLTK

persist_directory = os.getenv("PERSIST_DIRECTORY", "VectorDB")

# Initialise embeddings - we can alternatively chose one of many different open-source embeddings
# Initialize model
# model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

embedding = OpenAIEmbeddings()

# create vector DB using Chroma
print("Creating vector DB")
vectordb = Chroma.from_texts(
    texts=pdf_chunks, embedding=embedding, persist_directory=persist_directory
)


"""
Example use case
question = "what is reguralisation?"

#Loading from disk
db3 = Chroma(persist_directory="docs/chroma/", embedding_function=embedding)
docs = db3.similarity_search(question, k=3)

print(docs)
"""
