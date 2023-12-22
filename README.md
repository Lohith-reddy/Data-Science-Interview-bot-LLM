# The Griller - Datascience Interview Bot

- Fixing Bugs

## Configuring the interview

User configures the interview by,

    1. uploading a resume
    2. copy pasting a job description
    3. Difficulty level - 1-5
    4. Interview Prep or real simulation

Resume will be parsed to find skills and projects

skills will be extracted using NLP - computationally cheap and fast

Extracting projects - few shot learning.

Skills should be extracted from job description. Business use cases should be 
extracted - extracting Domain should be enough.

## Interview Process

start by saying hello

start taking about skills, ask questions based on the skills that match between job desc. and resume

sub flow

select a skill, retrieve a question from DB
    ASk the question to the candidate

Retrieve answers from the DB - rate the answer

    rate the answer,
        if the answer is good, ask a different question on the same skill - 
        if the answer seems shaky, grill 
        if the answer is bad, a pass, ask a different question on the same skill

Note: (How to determine difficulty of question?)

    After asking N question move to next skill (N is determined by difficulty and interview config - simulation or learning)
    or 
    If 30% total time has passed, move on to project grilling. 
        (total time is determined by config)

    After 70% of time,
        Question them to design frameworks for the particular business domain
        Grill them on their answer
        or
        Ask them to find some usecases for the said business domain.

    Grilling: 
        Ask questions about processes mentioned by candidate. Any skills, keywords, algorithms mentioned by the candidate. Why the candidate chose a certain path. Suggest alternatives and check why they didn't pursue those paths instead.

        Ask details about the mechanisms of different algorithms. Ask the pseudo code of algorithms. 
    
    After each question, rate the resoponse.
    Store the question, skill, rating in a json report. 
    At the end of the interview, based on the report, provide feedback. 

## Tutoring - in development

    Based on the report and questions poorly answered,
    provide valid answers for the question one by one. chat with the candidate to understand if they understood the concept. Give out all the details about the skill, algorithm, or process.

## 📦 Streamlit App

Description of the app ...

## Demo App

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://app-starter-kit.streamlit.app/)

## GitHub Codespaces

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/app-starter-kit?quickstart=1)

## Description

Streamlit chatbot hosting 'The Griller'
