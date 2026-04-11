import pdfplumber
import docx
import re
from typing import List, Optional


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s@.+-]", "", text)
    return text.strip()


def extract_text(file, filename: str) -> str:
    text = ""

    if filename.lower().endswith(".pdf"):
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

    elif filename.lower().endswith(".docx"):
        document = docx.Document(file)
        for para in document.paragraphs:
            text += para.text + "\n"

    return clean_text(text)


def extract_email(text: str) -> Optional[str]:
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return emails[0] if emails else None


def extract_phone(text: str) -> Optional[str]:
    phones = re.findall(r"\b\d{10}\b", text)
    return phones[0] if phones else None


def extract_skills(text: str) -> List[str]:
    skills_db = [
        "python", "java", "c++", "javascript", "react", "node",
        "machine learning", "deep learning", "nlp",
        "html", "css", "sql", "mongodb", "tensorflow"
    ]

    text = text.lower()
    return [skill for skill in skills_db if skill in text]


def parse_resume(file_path: str) -> dict:
    if file_path.lower().endswith(".pdf"):
        with open(file_path, "rb") as f:
            text = extract_text(f, file_path)
    elif file_path.lower().endswith(".docx"):
        with open(file_path, "rb") as f:
            text = extract_text(f, file_path)
    elif file_path.lower().endswith(".txt"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = clean_text(f.read())
    else:
        raise ValueError("Unsupported file format")

    if not text:
        return {}

    return {
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "text": text
    }


class ResumeParser:
    def parse_resume(self, file_path: str) -> dict:
        return parse_resume(file_path)


if __name__ == "__main__":
    print("Resume parser module loaded.")
