# app.py

import os
from fastapi import FastAPI, HTTPException
from typing import List

# LangChain & Vector Store
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document

# LLM imports
from langchain import PromptTemplate, LLMChain
from langchain.llms import OpenAI  # or ChatOpenAI if you prefer GPT-3.5-turbo
from langchain.chat_models import ChatOpenAI
# Helpers
from utils.pdf_loader import load_preceptor_profiles_from_pdf
from utils.db_connection import get_mentee_data

app = FastAPI()

# -----------------------
# 1. INITIAL SETUP
# -----------------------
os.environ["OPENAI_API_KEY"] = "fill in the key"  # or set this as an environment variable
PDF_PATH = "data/preceptors.pdf"
CHROMA_PERSIST_DIR = "embeddings/chromadb"

# Create embedding model
embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")

# 1a. Load PDF as Documents (or handle manually if needed)
all_preceptor_docs = load_preceptor_profiles_from_pdf(PDF_PATH)

# 1b. Create or load a Chroma vector store
try:
    vector_store = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embedding_model
    )
    # Check if the store is empty; if yes, we ingest documents now
    if vector_store._collection.count() == 0:
        raise ValueError("Chroma store is empty; re-ingesting documents...")
except Exception:
    # Rebuild from scratch and persist
    vector_store = Chroma.from_documents(
        documents=all_preceptor_docs,
        embedding=embedding_model,
        persist_directory=CHROMA_PERSIST_DIR
    )
    vector_store.persist()

# 1c. Define an LLM to generate personalized summaries
# Using the older GPT-3 model as an example; for GPT-3.5+,
# you might do ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo").
llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")  # temperature=0.7 for a bit of creativity

# 1d. Create a PromptTemplate and LLMChain for personalizing each match
prompt_template = PromptTemplate(
    input_variables=["mentee_profile", "preceptor_profile"],
    template="""
Given the following Mentee profile:

{mentee_profile}

And the following Preceptor profile:

{preceptor_profile}

Please produce a short, human-friendly summary that explains why this preceptor might be a good fit for the mentee, referencing the mentee's background, experience, learning style, availability, personality, and unit needs. Provide a cohesive, empathetic description that feels natural and addresses how the preceptor can meet the mentee’s preferences. Instead of saying our mentee, refer to the mentee as you
"""
)
personalize_chain = LLMChain(llm=llm, prompt=prompt_template)

# -----------------------
# 2. MATCH MENTOR ENDPOINT
# -----------------------
@app.get("/match_mentor/{mentee_id}")
def match_mentor(mentee_id: int, k: int = 3):
    """
    API endpoint that returns a list of top 'k' matching preceptors for a given mentee ID,
    along with a personalized summary for each match.
    """
    # 2a. Retrieve Mentee Data from MySQL
    mentee_info = get_mentee_data(mentee_id)
    if not mentee_info:
        raise HTTPException(status_code=404, detail="Mentee not found in database.")

    # 2b. Concatenate Mentee Data
    mentee_profile_text = (
        f"Background: {mentee_info['background']}\n"
        f"Experience: {mentee_info['experience']}\n"
        f"LearningStyle: {mentee_info['learning_style']}\n"
        f"Availability: {mentee_info['availability']}\n"
        f"PersonalityTraits: {mentee_info['personality']}\n"
        f"UnitNeeds: {mentee_info['unit_needs']}"
    )

    # 2c. Similarity Search in Vector DB
    results = vector_store.similarity_search(
        query=mentee_profile_text,
        k=k
    )

    # 2d. (Optional) Filter or re-rank results by metadata or business rules here
    # e.g., if doc.metadata["specialty"] == mentee_info["unit_needs"], etc.

    # 2e. PERSONALIZE the response for each top match using an LLM
    personalized_matches = []
    for doc in results:
        # doc.page_content holds the preceptor's raw text from the PDF
        # Generate a custom summary referencing the mentee's profile
        summary = personalize_chain.run({
            "mentee_profile": mentee_profile_text,
            "preceptor_profile": doc.page_content
        })

        personalized_matches.append({
            "preceptor_profile_snippet": doc.page_content[:300],  # snippet
            "personalized_summary": summary.strip(),
        })

    # 2f. Return the final structured result
    return {
        "mentee_id": mentee_id,
        "personalized_matches": personalized_matches
    }