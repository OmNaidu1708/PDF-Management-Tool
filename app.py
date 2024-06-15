import streamlit as st
import os
from PyPDF2 import PdfMerger
import fitz
from docx import Document
from pdf2docx import Converter
from transformers import pipeline
import tempfile

# Initialize the NLP pipeline outside the function to avoid repeated loads
nlp = pipeline("question-answering", model="distilbert-base-cased-distilled-squad", tokenizer="distilbert-base-cased")

def merge_pdfs(pdfs):
    merger = PdfMerger()
    for pdf in pdfs:
        merger.append(pdf)
    output = "merged.pdf"
    merger.write(output)
    merger.close()
    return output

def pdf_to_word(pdf_file):
    output = "converted.docx"
    cv = Converter(pdf_file)
    cv.convert(output, start=0, end=None)
    cv.close()
    return output

def word_to_pdf(word_file):
    doc = Document(word_file)
    output = "converted.pdf"
    c = canvas.Canvas(output)
    for para in doc.paragraphs:
        c.drawString(10, 800, para.text)
    c.save()
    return output

def extract_text_from_pdf(pdf_file):
    doc = fitz.open(pdf_file)
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text("text")
    return text

def answer_question(text, question):
    result = nlp(question=question, context=text)
    return result['answer']

def main():
    st.title("PDF Tool with Streamlit")

    # Merge PDFs section
    st.header("Merge PDFs")
    uploaded_files = st.file_uploader("Upload PDFs to merge", type="pdf", accept_multiple_files=True)
    if st.button("Merge PDFs"):
        if uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                pdf_paths = []
                for uploaded_file in uploaded_files:
                    temp_path = os.path.join(tempfile.gettempdir(), uploaded_file.name)
                    pdf_paths.append(temp_path)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                merged_pdf = merge_pdfs(pdf_paths)
                with open(merged_pdf, "rb") as file:
                    st.download_button(label="Download Merged PDF", data=file, file_name=merged_pdf)
        else:
            st.warning("Please upload PDF files to merge.")

    # Convert PDF to Word section
    st.header("Convert PDF to Word")
    pdf_file = st.file_uploader("Upload a PDF to convert to Word", type="pdf")
    if st.button("Convert PDF to Word"):
        if pdf_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(pdf_file.getbuffer())
                word_file = pdf_to_word(temp_file.name)
                with open(word_file, "rb") as file:
                    st.download_button(label="Download Word Document", data=file, file_name=word_file)
        else:
            st.warning("Please upload a PDF file.")

    # Convert Word to PDF section
    st.header("Convert Word to PDF")
    word_file = st.file_uploader("Upload a Word document to convert to PDF", type="docx")
    if st.button("Convert Word to PDF"):
        if word_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
                temp_file.write(word_file.getbuffer())
                pdf_file = word_to_pdf(temp_file.name)
                with open(pdf_file, "rb") as file:
                    st.download_button(label="Download PDF Document", data=file, file_name=pdf_file)
        else:
            st.warning("Please upload a Word file.")

    # Ask questions about a PDF section
    st.header("Ask Questions about a PDF")
    qa_pdf_file = st.file_uploader("Upload a PDF to ask questions about", type="pdf")
    question = st.text_input("Enter your question about the PDF content")
    if st.button("Get Answer"):
        if qa_pdf_file and question:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(qa_pdf_file.getbuffer())
                text = extract_text_from_pdf(temp_file.name)
                answer = answer_question(text, question)
                st.write(f"Answer: {answer}")
        else:
            st.warning("Please upload a PDF and enter a question.")

if __name__ == "__main__":
    main()
