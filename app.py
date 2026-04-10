from flask import Flask, render_template, request, redirect, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from functools import wraps

import re
import pdfplumber
import docx

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from semantic_matcher import sbert_similarity
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "hackathon_key"


# Mongo
app.config["MONGO_URI"] = "mongodb+srv://resume_user:fcritru12345@cluster0.vpqwj7a.mongodb.net/ai_resume_db"
mongo = PyMongo(app)

users = mongo.db.users
jds = mongo.db.job_descriptions


# role protection
def login_required(role=None):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user" not in session:
                return redirect("/login")
            if role and session.get("role") != role:
                return "Unauthorized", 403
            return f(*args, **kwargs)
        return decorated
    return wrapper


def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text)


def load_file(file):
    if not file:
        return ""

    name = file.filename.lower()

    if name.endswith(".txt"):
        return clean_text(file.read().decode("utf-8"))

    elif name.endswith(".docx"):
        d = docx.Document(file)
        return clean_text("\n".join(p.text for p in d.paragraphs))

    elif name.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file) as pdf:
            for p in pdf.pages:
                if p.extract_text():
                    text += p.extract_text()
        return clean_text(text)

    return ""


def score_resume(resume, jd):
    vec = TfidfVectorizer(stop_words="english")
    mat = vec.fit_transform([resume, jd])
    tfidf = cosine_similarity(mat[0:1], mat[1:2])[0][0] * 100

    semantic = sbert_similarity(resume, jd)
    final = 0.6 * semantic + 0.4 * tfidf

    return round(final, 2)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        users.insert_one({
            "username": request.form["username"],
            "password": generate_password_hash(request.form["password"]),
            "role": request.form["role"]
        })
        return redirect("/login")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = users.find_one({"username": request.form["username"]})

        if user and check_password_hash(user["password"], request.form["password"]):
            session["user"] = user["username"]
            session["role"] = user["role"]
            return redirect(f"/{user['role']}")

    return render_template("login.html")


# HR dashboard
@app.route("/hr")
@login_required("hr")
def hr():
    return render_template("hr_dashboard.html", jds=list(jds.find()))


@app.route("/hr/upload", methods=["POST"])
@login_required("hr")
def upload_jd():
    jd = load_file(request.files["jd"])

    jds.insert_one({
        "title": request.form["title"],
        "jd": jd
    })

    return redirect("/hr")


@app.route("/hr/analyze", methods=["POST"])
@login_required("hr")
def analyze():
    jd = jds.find_one({"_id": ObjectId(request.form["jd_id"])})

    results = []

    for file in request.files.getlist("resumes"):
        resume = load_file(file)
        score = score_resume(resume, jd["jd"])

        results.append({
            "name": file.filename,
            "score": score
        })

    results.sort(key=lambda x: x["score"], reverse=True)

    return render_template("hr_results.html", results=results)


# candidate
@app.route("/candidate")
@login_required("candidate")
def candidate():
    return render_template("candidate.html", jobs=list(jds.find()))


@app.route("/candidate/upload", methods=["POST"])
@login_required("candidate")
def candidate_upload():
    resume = load_file(request.files["resume"])
    jd = jds.find_one({"_id": ObjectId(request.form["job_id"])})

    score = score_resume(resume, jd["jd"])

    return render_template("candidate_result.html", score=score)


if __name__ == "__main__":
    app.run(debug=True)