from flask import Flask, request, jsonify
import os
import requests
import uuid
from dotenv import load_dotenv
from flask_cors import CORS
from document_handler import extract_text_from_pdf, summarize_text, ask_question, generate_insights, generate_feedback_insights

load_dotenv()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploaded_pdfs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

document_summaries = {}

@app.route("/analyze-feedback", methods=["POST"])
def analyze_feedback():
    """Analyzes a topic's feedback and provides insights."""
    data = request.json
    topic = data.get("topic")
    feedbacks = data.get("feedbacks")

    if not topic or not feedbacks:
        return jsonify({"error": "Missing topic or feedbacks"}), 400

    insights = generate_feedback_insights(topic, feedbacks)

    return jsonify({"insights": insights})


@app.route("/analyze-incidents", methods=["POST"])
def analyze_incidents():
    """Analyzes a list of incidents and provides insights."""
    data = request.json
    incidents = data.get("incidents")

    if not incidents:
        return jsonify({"error": "No incidents provided"}), 400

    incident_texts = "\n".join([f"Incident {i+1}: {inc['title']} - {inc['description']}" for i, inc in enumerate(incidents)])
    
    insights = generate_insights(incident_texts)

    return jsonify({"insights": insights})


@app.route("/summarize", methods=["POST"])
def summarize_pdf():
    """Fetch a PDF from a URL, save it uniquely, extract text, and summarize it."""
    data = request.json
    pdf_url = data.get("pdf_url")

    if not pdf_url:
        return jsonify({"error": "Missing PDF URL"}), 400

    unique_filename = f"{uuid.uuid4().hex}.pdf"
    pdf_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    response = requests.get(pdf_url)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch the document"}), 400

    with open(pdf_path, "wb") as f:
        f.write(response.content)

    text = extract_text_from_pdf(pdf_path)
    summary = summarize_text(text)

    document_summaries[unique_filename] = {"summary": summary, "text": text}

    return jsonify({
        "file_id": unique_filename,
        "summary": summary
    })

@app.route("/ask", methods=["POST"])
def ask():
    """Allows users to ask questions about a specific document"""
    data = request.json
    file_id = data.get("file_id")
    question = data.get("question")

    if not file_id or not question:
        return jsonify({"error": "Missing file_id or question"}), 400

    document_data = document_summaries.get(file_id)
    if not document_data:
        return jsonify({"error": "Document not found"}), 404

    answer = ask_question(document_data["text"], question)
    
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
