from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
from vectordb import VectorDB
from qdrant_client.http.models import PointStruct, Batch
from langchain.embeddings import OpenAIEmbeddings
from os import getenv
import openai
import qdrant_client


def create_embeddings(files):

    openai.api_key = getenv("OPENAI_API_KEY")
    embedding_model = "text-embedding-ada-002"
    vectors = openai.Embedding.create(input=files,
                                      model=embedding_model
                                     )
    return vectors


def add_file_to_collection(qdrant_client,collection_name, files):
    """Add a file to a VectorDB collection."""
    vectors = create_embeddings(files)
    qdrant_client.upsert(collection_name=collection_name,
                         points=Batch(ids=[1],
                                      vectors=[response["data"][0]["embedding"]]
                                     )
                        )
    # print(operation_info) # log this instead.


def add_file_to_vectordb(**context):
    """Add a file to a VectorDB collection."""

    # Get the data passed to the DAG run
    data = context['dag_run'].conf

    # Get the name of the file that changed and the type of change
    file_name = data['name']
    event_type = data['eventType']

    # fetch files from gcs that match the file_name returned


    # If the file was created or updated, add it to the VectorDB collection
    if event_type in ['google.storage.object.finalize', 'google.storage.object.update']:
        qdrant_client = qdrant_client.QdrantClient()
        add_file_to_collection(qdrant_client,'griller_qdrant', file_name)


default_args = {"start_date": datetime(2023, 12, 20),
                "owner": 'airflow',
                "depends_on_past": False,
                'email': getenv('EMAIL')}


# Define the DAG
dag = DAG('your_dag_id', default_args=default_args, schedule_interval=None)

# Add a task to the DAG
add_file_task = PythonOperator(
    task_id='add_file_to_vectordb',
    python_callable=add_file_to_vectordb,
    provide_context=True,
    dag=dag
)



# Define the command to update the k8s cluster
patch_command = """
kubectl patch deployment qdrant-deployment -p \\
  "{\"spec\":{\"template\":{\"metadata\":{\"annotations\":{\"date\":\"`date +'%s'`\"}}}}}"
"""

# Add a task to the DAG to run the command
patch_task = BashOperator(
    task_id='patch_k8s_deployment',
    bash_command=patch_command,
    dag=dag
)

# Make the patch_task depend on the add_file_task
add_file_task >> patch_task


# create new snapshot

from qdrant_client import QdrantClient

client = QdrantClient("localhost", port=6333)

client.create_full_snapshot()

#bash
GET /snapshots/{snapshot_name}