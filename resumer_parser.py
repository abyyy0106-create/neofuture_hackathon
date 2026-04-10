def load_text(file_path):
    with open(file_path, "r") as f:
        return f.read().lower()
# resumer_parser.py

import re
import docx
import PyPDF2


# -----------------------------
# 1. Extract text from PDF
# -----------------------------
def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print("Error reading PDF:", e)
    return text


# -----------------------------
# 2. Extract text from DOCX
# -----------------------------
def extract_text_from_docx(file_path):
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print("Error reading DOCX:", e)
    return text


# -----------------------------
# 3. Extract Email
# -----------------------------
def extract_email(text):
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return emails[0] if emails else None


# -----------------------------
# 4. Extract Phone Number
# -----------------------------
def extract_phone(text):
    phones = re.findall(r"\b\d{10}\b", text)
    return phones[0] if phones else None


# -----------------------------
# 5. Extract Skills
# -----------------------------
def extract_skills(text):
    skills_db = [
        "python", "java", "c++", "javascript", "react", "node",
        "machine learning", "deep learning", "nlp",
        "html", "css", "sql", "mongodb", "tensorflow"
    ]

    text = text.lower()
    found_skills = []

    for skill in skills_db:
        if skill in text:
            found_skills.append(skill)

    return found_skills


# -----------------------------
# 6. Main Parser Function (FIXED)
# -----------------------------
def parse_resume(file_path):

    # Check file type and extract text
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)

    elif file_path.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    elif file_path.endswith(".txt"):
        text = load_text(file_path)
    else:
        return "Unsupported file format"

    if not text:
        return "No text extracted. Check file."

    # Extract data
    data = {
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text)
    }

    return data


class ResumeParser:
    """Wrapper for the resume parsing utilities."""

    def parse_resume(self, file_path):
        return parse_resume(file_path)


# -----------------------------
# 7. Test (MAIN)
# -----------------------------
if __name__ == "__main__":
    file = "resume.pdf"   # ⚠️ Make sure this file exists in your folder

    result = parse_resume(file)

    print("\nParsed Resume Data:")
    print(result)
