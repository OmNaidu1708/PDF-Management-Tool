import streamlit as st
import os
from PyPDF2 import PdfMerger
from docx import Document
from pdf2docx import Converter
import fitz
from transformers import pipeline
from docx2pdf import convert as docx_to_pdf_convert

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

# Function to convert Word to PDF
def word_to_pdf(word_file):
    output = "converted.pdf"
    docx_to_pdf_convert(word_file, output)
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
    st.set_page_config(layout="wide")
    st.title("PDF Tool with Streamlit")

    st.sidebar.title("Navigation")
    selected_option = st.sidebar.radio("Go to", ["Merge PDFs", "Convert PDF to Word", "Convert Word to PDF", "Ask Questions"])

    if selected_option == "Merge PDFs":
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
                merged_pdf = merge_pdfs(pdf_paths)
                with open(merged_pdf, "rb") as file:
                    st.download_button(label="Download Merged PDF", data=file, file_name="merged.pdf")
            else:
                st.warning("Please upload PDF files to merge.")

    elif selected_option == "Convert PDF to Word":
        st.header("Convert PDF to Word")
        pdf_file = st.file_uploader("Upload a PDF to convert to Word", type="pdf")
        if st.button("Convert PDF to Word"):
            if pdf_file:
                with open("temp_pdf.pdf", "wb") as f:
                    f.write(pdf_file.getbuffer())
                word_file = pdf_to_word("temp_pdf.pdf")
                with open(word_file, "rb") as file:
                    st.download_button(label="Download Word Document", data=file, file_name="converted.docx")
            else:
                st.warning("Please upload a PDF file.")

    elif selected_option == "Convert Word to PDF":
        st.header("Convert Word to PDF")
        word_file = st.file_uploader("Upload a Word document to convert to PDF", type="docx")
        if st.button("Convert Word to PDF"):
            if word_file:
                with open("temp_word.docx", "wb") as f:
                    f.write(word_file.getbuffer())
                pdf_file = word_to_pdf("temp_word.docx")
                with open(pdf_file, "rb") as file:
                    st.download_button(label="Download PDF Document", data=file, file_name="converted.pdf")
            else:
                st.warning("Please upload a Word file.")

    elif selected_option == "Ask Questions":
        st.header("Ask Questions about a PDF")
        qa_pdf_file = st.file_uploader("Upload a PDF to ask questions about", type="pdf")
        question = st.text_input("Enter your question about the PDF content")
        if st.button("Get Answer"):
            if qa_pdf_file and question:
                with open("qa_temp_pdf.pdf", "wb") as f:
                    f.write(qa_pdf_file.getbuffer())
                text = extract_text_from_pdf("qa_temp_pdf.pdf")
                answer = answer_question(text, question)
                st.write(f"Answer: {answer}")
            else:
                st.warning("Please upload a PDF and enter a question.")

if __name__ == "__main__":
    main()
