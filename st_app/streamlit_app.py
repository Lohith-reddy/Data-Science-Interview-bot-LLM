import streamlit as st

# import OpenAI
import time
import numpy as np
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.output_parsers.structured import StructuredOutputParser, ResponseSchema
import pandas as pd
import os
import warnings

import chatbot_helper as ch

warnings.filterwarnings("ignore", category=DeprecationWarning)

embedding = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
st.title("The Griller")

# client = OpenAI(api_key=st.secrets["PALM_API_KEY"])

# Set a default model
# if "openai_model" not in st.session_state:
#    st.session_state["openai_model"] = "gpt-3.5-turbo"

with st.sidebar:
    st.title("Input CV and job description")

    resume_content = st.file_uploader("Upload your resume (PDF)", type="pdf")
    job_desc = st.text_input("enter job description")


if resume_content and job_desc:
    with st.spinner("Processing Resume and Job Description..."):
    # Process the resume
        skills, projects = ch.extract_info(resume_content, job_desc)
        if skills == []:
            skills = ["Python", "Java", "SQL", " R", " C++", "Hadoop", "Spark", "MATLAB", "Excel",
                        "Tableau", "Power BI", "SAS", "SPSS", "Machine Learning", "Deep Learning",
                        "Natural Language Processing", "Computer Vision", "Linear Regression",
                        "Logistic Regression", "Decision Tree", "Random Forest", "XGBoost",
                        "K Nearest Neighbor", "Naive Bayes", "Support Vector Machine", "Neural Networks",
                        "K Means Clustering", "Hierarchical Clustering", "DBSCAN", "PCA",
                        "Time Series Analysis", "Reinforcement Learning", "TensorFlow", "Keras", "PyTorch",
                        "Scikit Learn", "Pandas", "Numpy", "Scipy", "Statistics", "Probability",
                        "Hypothesis Testing", "Data Cleaning", "Data Manipulation",
                        "Data Visualization", "EDA", "Web Scraping", "Cloud Computing", "AWS",
                        "GCP", "Azure", "Docker", "Kubernetes",
                        "Git", "GitHub"]
        with st.chat_message("assisstant"):
            st.write(skills)


# Opening message

if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello Candidate, Please upload your resume and \
job description in the sidebar to start the interview and then enter 'start' in the chat box to begin.\n\n \
Instructions:\n Type 'pass' to move to next question,\n Type 'project' to discuss projects,\n Type 'report' to get your report and \n\
Type 'help' to move to tutorial phase.",
        }
    ]


# writing the history to chat every rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# User-provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

questions_asked = []
project_questions_asked = []

db = Chroma(persist_directory="docs/chroma/", embedding_function=embedding)

# Generate a new response if last message is not from assistant
# Initialising and directing conversation
if st.session_state.messages[-1]["role"] != "assistant":
    # Get the last message from the user
    prompt = st.session_state.messages[-1]["content"]

    if prompt == "start":
        with st.chat_message("assistant"):
            st.write("start")
            st.write("common skills", skills)
        # generate a question
        skill = np.random.choice(skills)
        question = ch.questioner(skill, [""])
        st.session_state.messages.append({"role": "assistant", "content": question})
        with st.chat_message("assistant"):
            st.write(question)
        questions_asked.append(question)
      
    elif prompt not in ["project", "report"]:
        # Display assistant response in chat message container
        # with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        if 'history_df' not in globals():
            history_df = pd.DataFrame(columns=["skill", "rating", "decision", "question", "relevant_passage"])
        # st.write(st.session_state.messages[-2]["content"])
        with st.spinner("Thinking..."):
            output_response = ch.reasoning(
                db, prompt, st.session_state.messages[-2]["content"]
            )  # prompt is the last answer by the user
            history_df = ch.decision_processing(output_response, history_df)
        st.write(history_df)

        if output_response["decision"] == "skill_question_new":
            # ask a question on a new skill
            skill = np.random.choice(skills)
            question = ch.questioner(skill, history_df["question"])
            questions_asked.append({"question": question, "skill": skill})
            st.session_state.messages.append(
                {"role": "assistant", "content": question}
            )
            st.write(question)

        elif output_response["decision"] == "skill_question_same":
            # ask a question on a new skill
            skill = history_df["skill"].iloc[-1]
            question = ch.questioner(skill, history_df["question"])
            questions_asked.append({"question": question, "skill": skill})
            st.session_state.messages.append(
                {"role": "assistant", "content": question}
            )
            st.write(question)

        elif output_response["decision"] == "project_question_new":
            project = np.random.choice(projects)
            question = ch.questioner_project(project, history_df["question"])
            project_questions_asked.append(
                {"question": question, "project": project}
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": question}
            )
            st.write(question)

        elif output_response["decision"] == "conversation":

            response = ch.converse(st.session_state.messages[-4:])
            st.session_state.messages.append({"role": "assistant",
                                             "content": response})
            st.write(response)

        else:
            st.session_state.messages.append(
                {"role": "assistant", "content": output_response["decision"]}
            )

            st.write(output_response["decision"])

            # project = history_df["project"].iloc[-1]
            # question = ch.questioner_project(project, history_df["question"])
            # project_questions_asked.append(
            #     {"question": question, "project": project}
            # )
            # st.session_state.messages.append(
            #     {"role": "assistant", "content": question}
            # )

            # st.write(question)

    elif prompt == "project":
        if projects == []:
            with st.chat_message("assistant"):
                st.write("You have no projects in your resume")
        else:
            project = np.random.choice(projects)
            question = ch.questioner_project(project, history_df["question"])
            st.session_state.messages.append({"role": "assistant", "content": question})
            with st.chat_message("assistant"):
                st.write(question)
            questions_asked.append(question)

    elif prompt == "report":
        with st.chat_message("assistant"):
            try:
                st.write(history_df)
            except NameError:
                st.write("No report yet")


    # elif prompt == "help":
    # with st.chat_message("assistant"):
    #    st.write("what topic would like to learn about?")
