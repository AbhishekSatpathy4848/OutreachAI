import os
from google.generativeai import GenerativeModel, configure
from dotenv import load_dotenv

load_dotenv()
configure(api_key=os.getenv("GEMINI_API_KEY"))

def prompt_gemini(text):
    model = GenerativeModel("gemini-2.5-flash-preview-05-20")
    response = model.generate_content(text)
    return response.text

if __name__ == "__main__":
    text = "What is the capital of France?"
    response = prompt_gemini(text)
    print(f"Response from Gemini: {response}")
