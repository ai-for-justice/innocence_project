import os
from langchain_community.chat_models import ChatOpenAI

os.environ["OPENAI_API_KEY"] = "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"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
}

INFO_EXTRACTION_RPOMPT = """
    Analyze the provided images to summarize key information about the applicant's case based on their responses. Focus on accurately capturing:

    - Personal identification details.
    - Specifics of the crime(s) they were convicted of, including dates and locations.
    - Their account of the events surrounding the crime, emphasizing their description and any claims of innocence.
    - Any alibi or evidence they provide that supports their case.
    - Connections or relationships with the victim(s) or others involved in the case.
    - Clarify the applicant's stance on their conviction and any aspects they are disputing.

    Ensure to maintain the original meaning and intention of the applicant's responses, avoiding any assumptions or modifications beyond what is explicitly stated in their answers.
"""

LLM = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))
