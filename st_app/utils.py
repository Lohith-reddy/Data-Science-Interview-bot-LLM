from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
#from langchain.llms import VertexAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from typing import List
from langchain_google_genai import GoogleGenerativeAI
import os
from collections import Counter
import json
import re


from dotenv import load_dotenv

load_dotenv()


def load_pdfs(path):
    loader = PyPDFLoader(path)
    pages = loader.load()
    pdf_content = "\n".join([page.page_content for page in pages])
    return pdf_content


def remove_surrogates(text):
    return text.encode('utf-8', 'ignore').decode('utf-8')


def get_chunks(text, chunk_size=1000, chunk_overlap=10):
    r_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, separators=["\.", "\n"]
    )
    split_data = r_splitter.split_text(text)
    # Remove tabs and newline characters
    cleaned_chunks = [chunk.replace('\t', '').replace('\n', '') for chunk in split_data]
    cleaned_chunks = [remove_surrogates(chunk) for chunk in cleaned_chunks]
    return cleaned_chunks


def get_projects(resume_content):
    class ProjectItem(BaseModel):
        project_name: str
        project_description: str

    class Projects(BaseModel):
        projects: List[ProjectItem]

    parser = PydanticOutputParser(pydantic_object=Projects)

    prompt = ChatPromptTemplate.from_template(
        "From the resume below extract the projects and their descriptions {resume_content}.\
                                               Return the projects and their descriptions in json format. \n {format_instructions}"
    )

    formated_prompt = prompt.format(
        **{
            "resume_content": resume_content,
            "format_instructions": parser.get_format_instructions(),
        }
    )

    llm = GoogleGenerativeAI(model="gemini-pro",
                             google_api_key=os.getenv("PALM_API_KEY"),
                             temperature=0.1)

    response_palm = llm.invoke(formated_prompt)
    response_palm = parser.parse(response_palm)
    response_palm = json.loads(response_palm.model_dump_json())["projects"]
    # print("PaLM:")
    # print(response_palm)
    return response_palm


def get_skills_resume(resume_content):
    skills = ResponseSchema(
        name="skills",
        description="Skills mentioned in the resume",
    )

    output_parser = StructuredOutputParser.from_response_schemas([skills])

    prompt = ChatPromptTemplate.from_template(
        "What the different skills mentioned in the resume below {resume_content}. Return the skills in json format. \n {format_instructions}"
    )

    formated_prompt = prompt.format(
        **{
            "resume_content": resume_content,
            "format_instructions": output_parser.get_format_instructions(),
        }
    )

    llm = GoogleGenerativeAI(model="gemini-pro",
                             google_api_key=os.getenv("PALM_API_KEY"),
                             temperature=0.1)

    response_palm = llm.invoke(formated_prompt)

    return output_parser.parse(response_palm)["skills"]


def get_skills_job_desc(job_desc):
    skills = ResponseSchema(
        name="skills",
        description="Skills mentioned in the resume",
    )

    output_parser = StructuredOutputParser.from_response_schemas([skills])

    prompt = ChatPromptTemplate.from_template(
        "What the different skills mentioned in the job description below {job_desc}.\
         Return the skills in json format.\
         {format_instructions}"
    )

    formated_prompt = prompt.format(
        **{
            "job_desc": job_desc,
            "format_instructions": output_parser.get_format_instructions(),
        }
    )

    llm = GoogleGenerativeAI(model="gemini-pro",
                             google_api_key=os.getenv("PALM_API_KEY"),
                             temperature=0.1)

    response_palm = llm.invoke(formated_prompt)
    # print("PaLM:")
    # print(response_palm)
    # print(output_parser.parse(response_palm))
    return output_parser.parse(response_palm)["skills"]


def get_experience(resume_content):
    #### Extract Projects from resume
    template = f"""
    From the resume below extract data science related experience
    Output should be a integer value denoting the number of months of experience
    {resume_content}
    """
    llm = GoogleGenerativeAI(model="gemini-pro",
                             google_api_key=os.getenv("PALM_API_KEY"),
                             temperature=0.1)

    response_palm = llm.invoke(template)

    return int(response_palm)

# deprecated

def get_skills_regex(resume_content_chunks: list) -> list:
    """
    Load skills list from config.json and check for matches in the resume
    it might be better to use an LLM for this too.
    """
    with open("config.json") as f:
        data = json.load(f)
        entities = data["skills"]  # Check if skills is the correct key

    # Combine the skills for regex pattern
    pattern = "|".join(entities)
    # Processing all files
    for file in resume_content_chunks:
        # Find all skills in the text
        skills.extend(re.findall(pattern, file, re.IGNORECASE))

    skills = list(set([skill.lower() for skill in skills]))

    # Get the unique values and their counts
    skills = Counter(skills)
    return skills
    # print(f"For file, found skills: {skills}") # for debugging
