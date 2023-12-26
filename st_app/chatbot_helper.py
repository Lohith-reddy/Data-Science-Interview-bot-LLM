import os
from dotenv import load_dotenv
import PyPDF2

# from langchain.chat_models import ChatVertexAI
# from langchain.llms import GooglePalm
from langchain.prompts import ChatPromptTemplate
import google.generativeai as palm
from langchain.output_parsers.structured import StructuredOutputParser, ResponseSchema
import pandas as pd
from langchain_google_genai import GoogleGenerativeAI

import utils as h


load_dotenv()


# chat = ChatVertexAI()

palm.configure(api_key=os.getenv("PALM_API_KEY"))  # alternatively use streamlit secrets


def read_pdf(file):
    if file is not None:
        # Read the PDF file
        pdf_reader = PyPDF2.PdfReader(file)
        # Extract the content
        content = ""
        for page in range(len(pdf_reader.pages)):
            content += pdf_reader.pages[page].extract_text()
    return content


def extract_info(resume_content, job_desc):
    resume_content = read_pdf(resume_content)
    resume_content = resume_content.replace("\n", " ")
    skills = h.get_skills_resume(resume_content)
    projects = h.get_projects(resume_content)
    job_desc_skills = h.get_skills_job_desc(job_desc)
    skills = [skill.lower() for skill in skills]
    job_desc_skills = [skill.lower() for skill in job_desc_skills]
    # skills that are common between job description and resume
    skills_queue = list(set(skills).intersection(set(job_desc_skills)))
    return skills_queue, projects


def questioner(skill, asked_questions):
    prompt = ChatPromptTemplate.from_template(
        """
    Ask a question to test the candidate's knowledge on the skill {skill}
    and these are the questions we have already asked:
    {asked_questions}
    Ask a different question.
    """
    )

    formated_prompt = prompt.format(
        **{"skill": skill, "asked_questions": asked_questions}
    )

    llm = GoogleGenerativeAI(model="gemini-pro",
                             google_api_key=os.getenv("PALM_API_KEY"),
                             temperature=0.9)

    response_palm = llm.invoke(formated_prompt)

    return response_palm


def converse(chat_history):
    prompt = ChatPromptTemplate.from_template(
        """
    You are an interviewer who is having a conversation with the candidate.
    The following is the recent conversation you had with the candidate:
    {history}
    based on the recent messages from the candidate, generate a response to the candidate.

    your response should have nothing but the response to the candidate.
    """
    )

    formated_prompt = prompt.format(**{"history": chat_history})

    llm = GoogleGenerativeAI(model="gemini-pro",
                             google_api_key=os.getenv("PALM_API_KEY"),
                             temperature=0.9)

    response_palm = llm.invoke(formated_prompt)

    return response_palm


def questioner_project(project, project_asked_questions):
    prompt = ChatPromptTemplate.from_template(
        """
    Ask a question to test the candidate's knowledge on the project {project}
    and these are the questions we have already asked:
    {project_asked_questions}
    Ask a different question.
    """
    )

    formated_prompt = prompt.format(
        **{"project": project, "project_asked_questions": project_asked_questions}
    )

    llm = GoogleGenerativeAI(model="gemini-pro",
                             google_api_key=os.getenv("PALM_API_KEY"),
                             temperature=0.9)

    response_palm = llm.invoke(formated_prompt)

    return response_palm


def create_answer(question, relevant_passage):
    relevant_passage = (
        relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
    )

    prompt = ChatPromptTemplate.from_template(
        """You are a helpful and informative bot that answers questions using text from the reference passage included below. \
    Be sure to respond in a complete sentence, being comprehensive, including all relevant background information. \
    However, you are talking to a non-technical audience, so be sure to break down complicated concepts and \
    strike a friendly and converstional tone. \
    Here is the question you need to answer:
    {question}
    and below are some revelevant passages to augment your answers:
    {relevant_passage}
    If the passage is irrelevant to the answer, you may ignore it.
    """
    )

    formated_prompt = prompt.format(
        **{"question": question, "relevant_passage": relevant_passage}
    )

    llm = GoogleGenerativeAI(model="gemini-pro",
                             google_api_key=os.getenv("PALM_API_KEY"),
                             temperature=0.1)

    response_palm = llm.invoke(formated_prompt)

    return response_palm


def get_relevant_passage(question, db):
    try:
        relevant_passage = db.similarity_search(question, k=20)
        relevant = []
        for doc in relevant_passage:
            relevant.append(doc.page_content)

        relevant_passage = list(set(relevant))
        relevant_passage = "/n".join(relevant_passage)
    except:
        relevant_passage = ""

    relevant_passage = create_answer(question, relevant_passage)

    return relevant_passage


def reasoning(db, answer, question):

    relevant_passage = get_relevant_passage(question, db)


    rating_schema = ResponseSchema(
        name="rating", description="rating of the answer out of 10"
    )
    decision_schema = ResponseSchema(
        name="decision", description="next decision to be made by the bot"
    )
    skill_schema = ResponseSchema(
        name="skill", description="skill of the question asked by the bot"
    )

    responseschemas = [skill_schema, rating_schema, decision_schema]
    OutputParser = StructuredOutputParser.from_response_schemas(responseschemas)

    prompt = ChatPromptTemplate.from_template(
        """You are a data science interviewer known for being thorough.
        You have previously asked the following questions:
        {question}
        and the following is the response you received from the candidate:
        {answer}                  
        the following is the information in the database about the topic
        {relevant_passage}
        using this information judge the answer,
            if the answer is good, ask a different question on the same skill - 
            if the answer seems shaky, grill some more to check if the candidate has only superficial knowledge
                Ask questions about processes mentioned by candidate. Any skills, keywords, algorithms mentioned by the candidate.\
                Why the candidate chose a certain path. Suggest alternatives and check why they didn't pursue those paths instead.
                Ask details about the mechanisms of different algorithms. Ask the pseudo code of algorithms. 
            if the answer is bad or the candidate has asked to pass the question, ask a different question on the same skill\
            then ask them a different question from a new question on a different skill.
      
            if the candidate has asked for a hint or indulging in conversation relevant to the interview,\
            then the output should be 'conversation'

            If the candidate asks you to ask a new question on a new skill, ask a new question on a new skill.
      
            if the response is out of the scope of the interview, bring the candidate back to the topic of the interview with \
            a gentle nudge and tell him that they can pass the question or skill if they don't know the answer. Or ask a new \
            question to the candidate.

        Never tell the candidate that they are wrong. Always ask them to explain their answer. However, never tell them the answer.
     
        You output should be in a json format. Rate the candidate's answer out of 10 in relevant situations. \
            if the situation is not relevant to rating, then the rating should be -1

        The next decision can be one of the following list
        ['skill_question_new', 'skill_question_same', 'project_question_new', 'project_question_grill','conversation']
      
        'skill_question_new' - ask a question on a new skill
        'skill_question_same' - ask a question on the same skill - if the last question is based on a skill
        'project_question_new' - ask a question on a new project
        'project_question_grill' - ask a question on the same project to grill the candidate - if  the last question is based on a project
        'conversation' - if the candidate has asked for a hint or indulging in conversation relevant to the interview        
                       
        {format_instructions}                             

        """
    )

    # response = palm.chat(context=prompt)

    formated_prompt = prompt.format(
        **{
            "question": question,
            "answer": answer,
            "relevant_passage": relevant_passage,
            "format_instructions": OutputParser.get_format_instructions(),
        }
    )

    llm = GoogleGenerativeAI(model="gemini-pro",
                             google_api_key=os.getenv("PALM_API_KEY"),
                             temperature=0.5)

    response_palm = llm.invoke(formated_prompt)
    response = OutputParser.parse(response_palm)
    # response = json.loads(response.model_dump_json())
    response['question'] = question
    response['relevant_passage'] = relevant_passage
    return response


def decision_processing(output_response, history_df):
    new_df = pd.DataFrame(output_response, index=[0])
    history_df = pd.concat([history_df, new_df])
    return history_df
