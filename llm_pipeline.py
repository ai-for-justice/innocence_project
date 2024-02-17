import os
import argparse
import fitz  # Import the PyMuPDF library
import base64
import requests
from PIL import Image
from io import BytesIO
from termcolor import colored
from typing import List, Union

# import langchain
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field, validator

from utils import (
    LLM,
    INFO_EXTRACTION_RPOMPT,
    MISSINFO_CHECK_PROMPT_TEMPLATE,
    CRITERIA_CHECK_PROMPT_TEMPLATE,
)

###############PDF to Image###############


def encode_image(image_path: List[str]) -> List[str]:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def encode_image_pil(image) -> str:
    """
    Encodes a PIL Image object to a base64 string.
    """
    with BytesIO() as image_buffer:
        image.save(image_buffer, format="PNG")  # Save image to buffer in PNG format
        return base64.b64encode(image_buffer.getvalue()).decode("utf-8")


def pdf_to_images(pdf_path: str) -> List[str]:
    """
    Converts each page of a PDF file into a list of base64-encoded images.

    Args:
        pdf_path (str): The file path of the PDF.

    Returns:
        List of base64-encoded strings, where each string represents an image of a PDF page.
    """
    encoded_images = []  # Initialize an empty list to store the base64 strings

    with fitz.open(pdf_path) as pdf:
        for page in pdf:
            # Render page to a pixmap (an image)
            pix = page.get_pixmap()
            # Convert the pixmap to an image bytes
            img_bytes = pix.tobytes("png")
            # Create a PIL Image object from the bytes
            image = Image.open(BytesIO(img_bytes))
            # Use the modified encode function to get a base64 string
            encoded_image = encode_image_pil(image)
            # Append the base64 string to the list
            encoded_images.append(encoded_image)

    return encoded_images


###############Analyze intake letter###############


def analyze_applicant_intake_letters(file_path: str) -> str:
    """
    Analyzes provided intake letters or images to summarize key information about an applicant's case.

    Args:
        file_path_or_images (str): The file path of the PDF or a list of image file paths containing the applicant's intake letters.

    Returns:
        The response from the API call.
    """
    if file_path.endswith(".pdf"):
        encoded_images = pdf_to_images(file_path)
    elif file_path.endswith((".png", ".jpeg", ".jpg")):
        encoded_images = [encode_image(file_path)]
    else:
        raise ValueError(
            "Unsupported file format or type. Please provide a PDF path or a list of PNG/JPEG image paths."
        )

    messages_content = [{"type": "text", "text": INFO_EXTRACTION_RPOMPT}] + [
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image}"}}
        for image in encoded_images
    ]

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": messages_content,
            }
        ],
        "max_tokens": 2000,
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=HEADERS, json=payload
    )

    return response.json()["choices"][0]["message"]["content"]


class MissInfoCheckOutput(BaseModel):
    response: str = Field(
        ...,
        description="Yes or No reply to the question: 'Is there any missing information?'",
    )
    next_steps: str = Field(
        ...,
        description="The letter that asks for missing information, provided only if response is 'Yes'.",
    )

    @validator("response")
    def response_must_be_yes_or_no(cls, v):
        if v.lower() not in ["yes", "no"]:
            raise ValueError('Response must be either "yes" or "no".')
        return v.lower()

    class Config:
        schema_extra = {
            "example": {
                "response": "yes",
                "next_steps": "Dear [Applicant Name],\n\nWe have reviewed your submission and found that it is missing critical information needed for further evaluation. Specifically, we require [missing information]. Please provide this at your earliest convenience.\n\nSincerely,\n[Your Name]",
            }
        }


class CriteriaCheckOutput(BaseModel):
    evaluation: str = Field(
        ...,
        description="The step by step evaluation of the applicant's case against the Innocence Project's criteria, including detailed reasoning for each point of consideration.",
    )
    conclusion: str = Field(
        ...,
        description="The conclusion of the evaluation, stating whether the case matches the excluded criteria or is suitable for further review.",
    )
    next_steps: str = Field(
        ...,
        description="The next steps to be taken based on the evaluation. This could be drafting a rejection letter if the case meets the excluded criteria or indicating the case is forwarded to a different team for cases that do not match the excluded criteria.",
    )

    class Config:
        schema_extra = {
            "example": {
                "evaluation": "The applicant's case was reviewed step by step against the project's criteria. No evidence of self-defense, illegal substance charges, or fraud was found.",
                "conclusion": "The case does not match any of the excluded criteria and is suitable for further review.",
                "next_steps": "The case is forwarded to the review team for detailed evaluation.",
            }
        }


MISSINFO_CHECK_PARSER = JsonOutputParser(pydantic_object=MissInfoCheckOutput)

MISSINFO_CHECK_PROMPT = PromptTemplate(
    input_variables=["background"],
    template=MISSINFO_CHECK_PROMPT_TEMPLATE,
    partial_variables={
        "format_instructions": MISSINFO_CHECK_PARSER.get_format_instructions()
    },
)

CRITERIA_CHECK_PARSER = JsonOutputParser(pydantic_object=CriteriaCheckOutput)

CRITERIA_CHECK_PROMPT = PromptTemplate(
    input_variables=["background"],
    template=CRITERIA_CHECK_PROMPT_TEMPLATE,
    partial_variables={
        "format_instructions": CRITERIA_CHECK_PARSER.get_format_instructions()
    },
)

MISSINFO_CHECK_CHAIN = MISSINFO_CHECK_PROMPT | LLM | MISSINFO_CHECK_PARSER
CRITERIA_CHECK_CHAIN = CRITERIA_CHECK_PROMPT | LLM | CRITERIA_CHECK_PARSER


def evaluate_applicant_criteria(background: str) -> str:
    """
    Evaluates the applicant's case against the Innocence Project's criteria for cases they do not handle.

    Args:
        background (str): The summarized information extracted from the applicant's intake letter.

    Returns:
        The response from the API call.
    """
    is_missinginfo = MISSINFO_CHECK_CHAIN.invoke({"background": background})
    if is_missinginfo["response"].lower() == "yes":
        return is_missinginfo
    else:
        return CRITERIA_CHECK_CHAIN.invoke({"background": background})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file_path",
        type=str,
        required=True,
        help="The file path of the PDF or the image file path containing the applicant's intake letters.",
    )
    parser.add_argument(
        "--openai_api_key",
        type=str,
        required=True,
        help="The OpenAI API key to authenticate the API requests.",
    )

    args = parser.parse_args()

    # setup the openai api key
    os.environ["OPENAI_API_KEY"] = args.openai_api_key
    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
    }
    LLM = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))
    MISSINFO_CHECK_CHAIN = MISSINFO_CHECK_PROMPT | LLM | MISSINFO_CHECK_PARSER
    CRITERIA_CHECK_CHAIN = CRITERIA_CHECK_PROMPT | LLM | CRITERIA_CHECK_PARSER

    print(
        colored(
            "Analyzing applicant's intake letter from the input files. Please wait...",
            "blue",
        )
    )

    # Assuming an affirmative response, proceed with analysis
    background = analyze_applicant_intake_letters(file_path=args.file_path)

    # Before printing out the background information
    print(
        colored(
            "What background information have we extracted from the applicant's intake letter?",
            "blue",
        )
    )
    print(colored(background, "yellow"))

    # Checking for missing information
    print(
        colored(
            "\nIs there any missing information in the application that we need to address?",
            "blue",
        )
    )
    missinfo_check = MISSINFO_CHECK_CHAIN.invoke({"background": background})

    if missinfo_check["response"].lower() == "yes":
        print(
            colored(
                "What does the drafted letter requesting the missing information say?",
                "blue",
            )
        )
        print(colored(missinfo_check["next_steps"], "yellow"))
    else:
        print(
            colored(
                "With no missing information, how does the applicant's case stand against our criteria?",
                "blue",
            )
        )
        criteria_check_response = CRITERIA_CHECK_CHAIN.invoke(
            {"background": background}
        )
        print(colored("Evaluation:", "green"), criteria_check_response["evaluation"])
        print(colored("Conclusion:", "green"), criteria_check_response["conclusion"])
        print(colored("Next Steps:", "green"), criteria_check_response["next_steps"])
