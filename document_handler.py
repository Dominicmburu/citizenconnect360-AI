import openai
import fitz
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=API_KEY)

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file"""
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text("text") for page in doc)
    return text

def summarize_text(text):
    """Summarizes document text using GPT-4"""
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "Summarize the following document."},
            {"role": "user", "content": text[:5000]}
        ]
    )
    return response.choices[0].message.content

def ask_question(text, question):
    """Answers user questions based on document text"""
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "Answer questions based on the document."},
            {"role": "user", "content": f"Document: {text[:5000]}\nQuestion: {question}"}
        ]
    )
    return response.choices[0].message.content

def generate_insights(text):
    """Generates insights based on incident reports"""
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "Analyze these incidents and provide key insights, trends, and unique aspects."},
            {"role": "user", "content": text[:5000]}
        ]
    )
    return response.choices[0].message.content

def generate_feedback_insights(topic, feedback_list):
    """Generates AI insights for a given topic and its feedback messages"""
    
    feedback_text = "\n".join([f"- {fb['message']}" for fb in feedback_list])
    prompt = (
        f"Topic: {topic}\n"
        f"Feedback:\n{feedback_text}\n\n"
        "Analyze this feedback and provide key insights, trends, and actionable suggestions."
    )
    
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "Analyze the following feedback and provide insights."},
                  {"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content


