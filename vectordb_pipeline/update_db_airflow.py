from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
from qdrant_client.http.models import PointStruct, Batch
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from os import getenv
import openai
import qdrant_client
import concurrent.futures
from google.cloud import storage
import requests
import json


def download_blob(bucket_name, source_blob_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    data = blob.download_as_text()
    return data


def download_files_concurrently(bucket_name, blob_names):
    """Download multiple blobs from the bucket concurrently and return their data."""
    data = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(download_blob, bucket_name, blob_name): blob_name for blob_name in blob_names}
        for future in concurrent.futures.as_completed(futures):
            blob_name = futures[future]
            try:
                data[blob_name] = future.result()
            except Exception as exc:
                print(f"An error occurred while downloading {blob_name}: {exc}")
    return data


def remove_surrogates(text):
    return text.encode('utf-8', 'ignore').decode('utf-8')


def get_chunks(text, chunk_size=1000, chunk_overlap=10):
    r_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, separators=["\.", "\n"]
    )
    split_data = r_splitter.split_text(text)
    cleaned_chunks = [chunk.replace('\t', '').replace('\n', '') for chunk in split_data]
    cleaned_chunks = [remove_surrogates(chunk) for chunk in cleaned_chunks]
    return cleaned_chunks


def create_embeddings(files):
    openai.api_key = getenv("OPENAI_API_KEY")
    embedding_model = "text-embedding-ada-002"
    vectors = openai.Embedding.create(input=files, model=embedding_model)
    return vectors


def add_file_to_collection(qdrant_client, collection_name, files, bucket_name):
    """Add a file to a VectorDB collection."""
    data = download_files_concurrently(bucket_name, files)
    files = [chunk for file in data.values() for chunk in get_chunks(file)]
    vectors = create_embeddings(files)
    qdrant_client.upsert(collection_name=collection_name, points=Batch(vectors=vectors))


def add_file_to_vectordb(**context):
    """Add a file to a VectorDB collection."""
    data = context['dag_run'].conf
    file_name = data['name']
    collection_name = 'griller_qdrant'
    bucket_name = "griller_data"
    qdrant_client = qdrant_client.QdrantClient()
    add_file_to_collection(qdrant_client, collection_name, [file_name], bucket_name)


def create_snapshot():
    """Create a snapshot of the collection."""
    client = qdrant_client.QdrantClient()
    snapshot_info = client.create_full_snapshot()
    with open('latest_snapshot_info.json', 'w') as f:  # write the latest snapshot info to a file
        json.dump(snapshot_info, f)


default_args = {"start_date": datetime(2023, 12, 20),
                "owner": 'airflow',
                "depends_on_past": False,
                'email': getenv('EMAIL'),
                'email_on_failure': True,
                'email_on_retry': False,
                'retries': 3}


with DAG('update_qdrant_db', default_args=default_args, schedule_interval=None) as dag:

    add_file_task = PythonOperator(task_id='add_file_to_vectordb',
                                   python_callable=add_file_to_vectordb,
                                   provide_context=True)

    create_snapshot_task = PythonOperator(task_id='create_snapshot',
                                          python_callable=create_snapshot,
                                          provide_context=True)

    patch_command = "kubectl patch deployment qdrant-deployment -p \
        {\"spec\":{\"template\":{\"metadata\":{\"annotations\":{\"date\":\"`date +'%s'`\"}}}}}"

    patch_task = BashOperator(task_id='patch_k8s_deployment', bash_command=patch_command)

    add_file_task >> create_snapshot_task >> patch_task
