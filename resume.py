import docx
import fitz  # PyMuPDF
import spacy
import streamlit as st

# Load spacy model
nlp = spacy.load("en_core_web_sm")


def extract_text_from_resume(uploaded_file):
    text = ""
    file_name = uploaded_file.name

    if file_name.endswith(".pdf"):
        # Read the file bytes directly for PyMuPDF
        file_bytes = uploaded_file.read()
        reader = fitz.open(stream=file_bytes, filetype="pdf")
        for page in reader:
            text += page.get_text()

    elif file_name.endswith(".docx"):
        # Pass the file-like object directly to Document
        doc = docx.Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text

    else:
        # Assuming text file
        text = uploaded_file.read().decode("utf-8", errors="ignore")

    return text


def calculate_match_score(resume_text, criteria_list):
    resume_doc = nlp(resume_text)
    total_similarity = 0

    for criteria in criteria_list:
        criteria_doc = nlp(criteria)
        similarity = resume_doc.similarity(criteria_doc)
        total_similarity += similarity

    score = (total_similarity / len(criteria_list)) * 100
    return min(score, 100)


# streamlit ui
st.title("Resume Matcher App")

user_input = st.text_input(
    "Enter job criteria/skills separated by commas (e.g. Python programming, Machine learning, AWS)"
)

# Added file uploader
uploaded_files = st.file_uploader(
    "Upload Resumes", type=["pdf", "docx", "txt"], accept_multiple_files=True
)

if st.button("Process Resumes"):
    career_criteria = [
        item.strip() for item in user_input.split(",") if item.strip()
    ]

    if not career_criteria:
        st.warning("No criteria entered. Please enter skills.")
    elif not uploaded_files:
        st.warning("Please upload at least one resume.")
    else:
        best_score = -1
        best_file = ""

        # Loop through uploaded files
        for uploaded_file in uploaded_files:
            try:
                # Reset file pointer to the beginning for each read
                uploaded_file.seek(0)
                resume_text = extract_text_from_resume(uploaded_file)
                score = calculate_match_score(resume_text, career_criteria)
                st.write(
                    f"Match Score for '{uploaded_file.name}': *{score:.2f}%*"
                )

                if score > best_score:
                    best_score = score
                    best_file = uploaded_file.name

            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {e}")

        if best_file:
            st.success("--- Best Match ---")
            st.write(f"File: *{best_file}*")
            st.write(f"Match Score: *{best_score:.2f}%*")