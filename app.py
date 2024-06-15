import streamlit as st
import os
from PyPDF2 import PdfMerger
from docx import Document
from pdf2docx import Converter
import fitz 
from transformers import pipeline
import subprocess

# Function to merge PDFs
def merge_pdfs(pdfs):
    merger = PdfMerger()
    for pdf in pdfs:
        merger.append(pdf)
    output = "merged.pdf"
    merger.write(output)
    merger.close()
    return output

# Function to convert PDF to Word
def pdf_to_word(pdf_file):
    output = "converted.docx"
    cv = Converter(pdf_file)
    cv.convert(output, start=0, end=None)
    cv.close()
    return output

# Function to convert Word to PDF using docx2pdf
def word_to_pdf(word_file):
    output = "converted.pdf"
    try:
        # Use docx2pdf for conversion
        from docx2pdf import convert
        convert(word_file, output)
    except Exception as e:
        st.error(f"Error converting Word to PDF: {e}")
        return None
    return output

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(pdf_file)
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text("text")
    return text

# Function to answer a question based on PDF content
def answer_question(text, question):
    nlp = pipeline("question-answering", model="distilbert-base-cased-distilled-squad", tokenizer="distilbert-base-cased")
    result = nlp(question=question, context=text)
    return result['answer']

def main():
    st.title("PDF Management Tool with Streamlit")

    # Merge PDFs section
    st.header("Merge PDFs")
    uploaded_files = st.file_uploader("Upload PDFs to merge", type="pdf", accept_multiple_files=True)
    if st.button("Merge PDFs"):
        if uploaded_files:
            pdf_paths = []
            for uploaded_file in uploaded_files:
                file_path = os.path.join(os.getcwd(), uploaded_file.name)
                pdf_paths.append(file_path)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            try:
                merged_pdf = merge_pdfs(pdf_paths)
                with open(merged_pdf, "rb") as file:
                    st.download_button(label="Download Merged PDF", data=file, file_name="merged.pdf")
            except Exception as e:
                st.error(f"Error during PDF merge: {e}")
        else:
            st.warning("Please upload PDF files to merge.")

    # Convert PDF to Word section
    st.header("Convert PDF to Word")
    pdf_file = st.file_uploader("Upload a PDF to convert to Word", type="pdf")
    if st.button("Convert PDF to Word"):
        if pdf_file:
            try:
                with open("temp_pdf.pdf", "wb") as f:
                    f.write(pdf_file.getbuffer())
                word_file = pdf_to_word("temp_pdf.pdf")
                with open(word_file, "rb") as file:
                    st.download_button(label="Download Word Document", data=file, file_name="converted.docx")
            except Exception as e:
                st.error(f"Error during PDF to Word conversion: {e}")
        else:
            st.warning("Please upload a PDF file.")

    # Convert Word to PDF section
    st.header("Convert Word to PDF")
    word_file = st.file_uploader("Upload a Word document to convert to PDF", type="docx")
    if st.button("Convert Word to PDF"):
        if word_file:
            try:
                with open("temp_word.docx", "wb") as f:
                    f.write(word_file.getbuffer())
                pdf_file = word_to_pdf("temp_word.docx")
                if pdf_file:
                    with open(pdf_file, "rb") as file:
                        st.download_button(label="Download PDF Document", data=file, file_name="converted.pdf")
            except Exception as e:
                st.error(f"Error during Word to PDF conversion: {e}")
        else:
            st.warning("Please upload a Word file.")

    # Ask questions about a PDF section
    st.header("Ask Questions about a PDF")
    qa_pdf_file = st.file_uploader("Upload a PDF to ask questions about", type="pdf")
    question = st.text_input("Enter your question about the PDF content")
    if st.button("Get Answer"):
        if qa_pdf_file and question:
            try:
                with open("qa_temp_pdf.pdf", "wb") as f:
                    f.write(qa_pdf_file.getbuffer())
                text = extract_text_from_pdf("qa_temp_pdf.pdf")
                if text:
                    answer = answer_question(text, question)
                    st.write(f"Answer: {answer}")
                else:
                    st.warning("Could not extract text from the PDF. Please check the PDF content.")
            except Exception as e:
                st.error(f"Error during PDF question answering: {e}")
        else:
            st.warning("Please upload a PDF and enter a question.")

if __name__ == "__main__":
    main()
