import google.generativeai as genai
from typing import List, Dict
import json
import os


def generate_qa_from_text(text: str, api_key: str = None, num_questions: int = 5) -> List[Dict[str, str]]:
    """
    Generate questions and answers from input text using Gemini API.

    Args:
        text (str): The input text to generate Q&A from
        api_key (str, optional): Your Gemini API key. If not provided, 
                                 it will look for GEMINI_API_KEY environment variable
        num_questions (int): Number of Q&A pairs to generate (default: 5)

    Returns:
        List[Dict[str, str]]: List of dictionaries with 'question' and 'answer' keys

    Raises:
        ValueError: If API key is not provided or found in environment
        Exception: For API-related errors
    """

    # Configure API key
    if api_key:
        genai.configure(api_key=api_key)
    else:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("API key must be provided or set as GEMINI_API_KEY environment variable")
        genai.configure(api_key=api_key)

    # Initialize the model
    model = genai.GenerativeModel('gemini-2.5-flash-lite')

    # Create prompt for Gemini
    prompt = f"""
    Based on the following text, generate {num_questions} questions and their corresponding answers.
    The questions should test understanding of the key concepts, facts, and ideas in the text.

    Text:
    {text}

    Please provide the output in the following JSON format:
    [
        {{"question": "Question 1 here", "answer": "Answer 1 here"}},
        {{"question": "Question 2 here", "answer": "Answer 2 here"}},
        ...
    ]

    Ensure each question is clear, specific, and answerable from the text provided.
    """

    try:
        # Generate content
        response = model.generate_content(prompt)

        # Parse the response
        if response.text:
            # Clean the response text (remove any markdown code blocks if present)
            cleaned_text = response.text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]

            # Parse JSON
            qa_list = json.loads(cleaned_text.strip())

            # Validate the format
            if isinstance(qa_list, list) and all(
                                    isinstance(item, dict) and 'question' in item and 'answer' in item
                                    for item in qa_list
            ):
                return qa_list
            else:
                raise ValueError("Response format is incorrect")
        else:
            raise Exception("Empty response from Gemini API")

    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse JSON response: {e}\nResponse: {response.text}")
    except Exception as e:
        raise Exception(f"Error generating Q&A: {str(e)}")



# Alternative version with more customization options
def generate_custom_qa(
        text: str,
        api_key: str = None,
        num_questions: int = 5,
        question_types: str = "factual, conceptual, and analytical",
        difficulty: str = "mixed"
) -> List[Dict[str, str]]:
    """
    Generate questions and answers with more customization options.

    Args:
        text (str): Input text
        api_key (str, optional): Gemini API key
        num_questions (int): Number of Q&A pairs
        question_types (str): Types of questions to generate
        difficulty (str): Difficulty level (easy, medium, hard, or mixed)

    Returns:
        List[Dict[str, str]]: List of Q&A dictionaries
    """

    if api_key:
        genai.configure(api_key=api_key)
    else:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    model = genai.GenerativeModel('gemini-pro')

    prompt = f"""
    Based on the following text, generate {num_questions} {question_types} questions 
    at {difficulty} difficulty level and their corresponding answers.

    Text:
    {text}

    Return ONLY a valid JSON array with objects containing 'question' and 'answer' keys.
    Format:
    [
        {{"question": "...", "answer": "..."}},
        {{"question": "...", "answer": "..."}}
    ]
    """

    try:
        response = model.generate_content(prompt)

        # Parse and clean the response
        cleaned_response = response.text.strip()
        if cleaned_response.startswith('```'):
            cleaned_response = cleaned_response.split('```')[1]
            if cleaned_response.startswith('json'):
                cleaned_response = cleaned_response[4:]

        return json.loads(cleaned_response.strip())

    except Exception as e:
        raise Exception(f"Error generating custom Q&A: {str(e)}")
