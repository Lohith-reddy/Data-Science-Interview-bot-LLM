# The Griller - Datascience Interview Bot

## Overview

The Griller is a datascience interview bot designed to assist in conducting technical interviews for data science positions. It provides a structured interview process, allowing users to configure the interview based on their specific requirements.

The project uses RAG with central reasoning LLM. The project is deployed as a streamlit (app on a kubernetes cluster using ansible, terraform and vault.)

## Features

- Configurable interview setup:
    - Upload resume
    - Copy-paste job description
    - Set difficulty level (1-5)
    - Choose between interview preparation or real simulation

- Resume parsing:
    - Extract skills and projects from the uploaded resume using NLP techniques

- Skill-based questioning:
    - Ask questions based on the skills that match between the job description and the resume

- Sub-flow:
    - Select a skill and retrieve a question from the database
    - Ask the question to the candidate
    - Rate the answer and proceed accordingly:
        - If the answer is good, ask a different question on the same skill
        - If the answer seems shaky, grill the candidate for more details
        - If the answer is bad, move on to a different question on the same skill

- Interview process flow:
    - After asking a certain number of questions or when a certain percentage of total time has passed, move on to project grilling
    - After a certain percentage of total time has passed, question the candidate on designing frameworks or finding use cases for a specific business domain
    - Conduct grilling by asking questions about processes, skills, keywords, and algorithms mentioned by the candidate
    - Rate the candidate's responses and store the question, skill, and rating in a JSON report

- Tutoring (in development):
    - Provide valid answers for poorly answered questions
    - Engage in a chat with the candidate to ensure understanding of concepts
    - Provide detailed information about skills, algorithms, or processes

- Streamlit App:
    - A user-friendly interface for interacting with The Griller

## Usage

To use The Griller, follow these steps:

1. Configure the interview by providing a resume, job description, difficulty level, and interview type.
2. The resume will be parsed to extract skills and projects.
3. The interview process will start with a greeting and skill-based questioning.
4. Rate the candidate's answers and proceed accordingly.
5. After a certain point, move on to project grilling or domain-specific questioning.
6. Continue grilling the candidate and rating their responses.
7. At the end of the interview, a JSON report will be generated with all the questions, skills, and ratings.
8. Based on the report, provide feedback to the candidate.

## Installation

To install and run The Griller, follow these steps:

1. Clone the repository: `git clone https://github.com/your-username/your-repo.git`
2. Navigate to the project directory: `cd your-repo`
3. Install the required dependencies: `pip install -r requirements.txt`
4. Run the Streamlit app: `streamlit run app.py`

## Contributing

Contributions are welcome! If you would like to contribute to The Griller, please follow these guidelines:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make your changes and commit them: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request.

