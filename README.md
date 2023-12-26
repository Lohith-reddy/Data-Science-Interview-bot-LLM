# The Griller - Datascience Interview Bot

## Overview

The Griller is a datascience interview bot designed to assist in conducting technical interviews for data science positions. It provides a structured interview process, allowing users to configure the interview based on their specific requirements.

The project uses RAG with central reasoning LLM. The project is deployed as a streamlit app on a Kubernetes cluster using Ansible, Terraform and Vault.

## Architecture

The Griller's infrastructure is built and managed using Terraform and Ansible on Google Cloud Platform (GCP). The initial setup of the Qdrant database is handled by the `initial_qdrant_db_setup.py` script inside the `vectordb_pipeline` directory.

The application is deployed on a Kubernetes cluster, with the Streamlit app running as a Docker container. The Docker image is automatically updated by GitHub Actions upon a commit to the main branch.

When data in the GCP bucket changes, a Pub/Sub trigger initiates a GCP function which triggers `data_eng_bastian` to run an Airflow DAG. This updates the database contents with the newly added documents. After the database is updated, Airflow commences a rolling update of the Kubernetes cluster, ensuring the Qdrant pods inside the cluster are updated with the new databases.

## Tech Stack

Terraform | Ansible | Kubernetes | Docker | GitHub Actions | Google Cloud Platform (GCP) | Airflow | Streamlit | Python | Linux Bash Commands | Qdrant | kops

## Features

- Configurable interview setup using resume and job description
- Skill-based questioning
- Retrieval Augmented Generation (RAG)
- Reasoning based flow
- Skill and Question level report for feedback
- Tutoring (in development)

## Usage

To use The Griller, follow these steps:

1. Configure the interview
2. The resume will be parsed to extract skills and projects
3. The interview process will start with a greeting and skill-based questioning
4. Rate the candidate's answers and proceed accordingly
5. After a certain point, move on to project grilling or domain-specific questioning
6. Continue grilling the candidate and rating their responses
7. At the end of the interview, a table will be generated with all the questions, skills, and ratings
8. Based on the report, provide feedback to the candidate

## Future Work

- Implement secure handling of secrets, possibly using Vault
- Create a logging system for better observability and debugging
- Implement monitoring for the project to track system health and performance

## Contact

Reach out to me @https://www.linkedin.com/in/lohithreddy/ @sailohithgummi@gmail.com
