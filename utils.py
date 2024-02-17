import os
from langchain_community.chat_models import ChatOpenAI

os.environ["OPENAI_API_KEY"] = ""

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
}

INFO_EXTRACTION_RPOMPT = """
    Analyze the provided images to summarize key information about the applicant's case based on their responses. Focus on accurately capturing:

    - Specifics of the crime(s) they were convicted of, including dates and locations.
    - Their account of the events surrounding the crime, emphasizing their description and any claims of innocence.
    - Any alibi or evidence they provide that supports their case.
    - Connections or relationships with the victim(s) or others involved in the case.
    - Clarify the applicant's stance on their conviction and any aspects they are disputing.

    Ensure to maintain the original meaning and intention of the applicant's responses, avoiding any assumptions or modifications beyond what is explicitly stated in their answers.
"""

MISSINFO_CHECK_PROMPT_TEMPLATE = """
    Review the summarized information extracted from the applicant's intake letter. 
    
    Information: '{background}'. 
    
    Determine if all necessary details are provided, including specifics of the conviction, the applicant's account and evidence, connections with involved parties, and their stance on the conviction. If any key information is missing, respond with 'YES' and draft a letter requesting the specific missing information from the applicant. The letter should be polite, concise, and clearly specify what information is needed and why it is important for their case. If the narrative is complete, simply respond with 'NO'.
    
    {format_instructions}.
"""

CRITERIA_CHECK_PROMPT_TEMPLATE = """
    Assess in details the provided narrative against the Innocence Project's criteria for cases they do not handle, which include consent/transaction cases, self-defense/justification, sustained abuse, illegal substance charges, RICO/Hobbs Act charges, DWI/DUI, fraud/identity theft/forgery, stalking/harassment, and sentencing reduction/overcharge issues.
    
    Narritive: '{background}'.

    1. Step by step, evaluate each criterion, explaining your decision process why the case does or does not fit within these excluded categories.
    2. Conclude whether the case should be rejected based on these criteria or if it matches the criteria for further review.
    3. If the narrative matches one of the excluded criteria, draft a polite and concise rejection letter explaining the specific reason(s) why the case does not meet the project's guidelines. If the narrative does not match any excluded criteria, indicate that the case is given to a different team for further handling.
    
    {format_instructions}.
"""

LLM = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))
