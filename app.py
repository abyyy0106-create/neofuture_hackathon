from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from flask import Flask, render_template, request, redirect, session, send_file
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson.errors import InvalidId
from functools import wraps

import os
import re
import io
import pdfplumber
import docx
import pandas as pd

from fpdf import FPDF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from werkzeug.security import generate_password_hash, check_password_hash


<<<<<<< HEAD
# ===================== Flask Setup =====================
=======
def sbert_similarity(text1: str, text2: str) -> float:
    """Lightweight similarity fallback for the app."""
    if not text1 or not text2:
        return 0.0
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform([text1, text2])
    return cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100


>>>>>>> 4f24208 (Added JD)
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "final_secret_key")


# ===================== MongoDB Setup =====================
mongo_uri = os.environ.get("MONGO_URI")
mongo = None

if mongo_uri and mongo_uri != "mongodb+srv://test_user:test_password@test-cluster.mongodb.net/talentiq_test?retryWrites=true&w=majority":
    # Only try to connect if a real URI is provided
    app.config["MONGO_URI"] = mongo_uri
    try:
        mongo = PyMongo(app)
        users = mongo.db.users
        jds = mongo.db.job_descriptions
        resumes = mongo.db.resumes
        print("✓ MongoDB connected successfully")
    except Exception as e:
        print(f"⚠️  MongoDB connection failed: {e}")
        print("⚠️  App will run in limited mode. Update .env with real MongoDB credentials and restart.")
        mongo = None
else:
    print("⚠️  MongoDB credentials not configured. Update .env with real credentials.")
    print("⚠️  App will run in limited UI-only mode.")
    users = None
    jds = None
    resumes = None


# ===================== MongoDB Check =====================
def require_mongodb():
    """Check if MongoDB is connected, return error page if not."""
    if mongo is None or users is None:
        return "❌ MongoDB not configured. Please add MONGO_URI credentials to .env and restart the app.", 503
    return None


# ===================== ROLE PROTECTION =====================
def login_required(role=None):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user" not in session:
                return redirect("/login")
            if role and session.get("role") != role:
                return "Unauthorized Access", 403
            return f(*args, **kwargs)
        return decorated
    return wrapper


# ===================== Utilities =====================
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def load_file(file):
    if not file or not file.filename:
        return ""

    filename = file.filename.lower()
    text = ""

    if filename.endswith(".txt"):
        text = file.read().decode("utf-8", errors="ignore")

    elif filename.endswith(".docx"):
        d = docx.Document(file)
        text = "\n".join(p.text for p in d.paragraphs)

    elif filename.endswith(".pdf"):
        out = []
        with pdfplumber.open(file) as pdf:
            for p in pdf.pages:
                t = p.extract_text()
                if t:
                    out.append(t)
        text = "\n".join(out)

    return clean_text(text)


def load_skills():
    try:
        s = pd.read_excel("skills_onet.xlsx")
        t = pd.read_excel("Technology Skills.xlsx")

        s = s[(s["Scale Name"] == "Importance") & (s["Data Value"] >= 3)]

        return set(s["Element Name"].str.lower()).union(
            set(t["Example"].str.lower())
        )
    except Exception as e:
        print(f"⚠️  Could not load skills database: {e}")
        print("⚠️  Skill matching will use limited mode")
        return set()  # Return empty set as fallback


SKILL_DB = load_skills()

def extract_experience_years(text):
    text = text.lower()

    matches = re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*(years|yrs)", text)
    if matches:
        values = [float(m[0]) for m in matches]
        return int(max(values))

    since_match = re.search(r"since\s+(20\d{2})", text)
    if since_match:
        from datetime import datetime
        start_year = int(since_match.group(1))
        return datetime.now().year - start_year

    return 0


def score_resume(resume, jd):
    rc, jc = clean_text(resume), clean_text(jd)

    if not rc or not jc:
        return 0, 0, 0, [], []

    vec = TfidfVectorizer(stop_words="english")
    mat = vec.fit_transform([rc, jc])
    tfidf = cosine_similarity(mat[0:1], mat[1:2])[0][0] * 100

    semantic = sbert_similarity(resume, jd)
    final = 0.6 * semantic + 0.4 * tfidf

    matched = [skill for skill in SKILL_DB if skill in rc]
    missing = [skill for skill in SKILL_DB if skill in jc and skill not in rc]

    return round(tfidf, 2), round(semantic, 2), round(final, 2), matched, missing


# ===================== Resume PDF Generator =====================
def resume_to_pdf(resume):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", style="B", size=18)
    pdf.cell(0, 10, resume["name"], ln=True, align="C")

    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, f"{resume['email']} | {resume['phone']}", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", style="B", size=13)
    pdf.cell(0, 8, "Summary", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 7, resume["summary"])
    pdf.ln(5)

    pdf.set_font("Arial", style="B", size=13)
    pdf.cell(0, 8, "Skills", ln=True)
    pdf.set_font("Arial", size=11)
    for skill in resume["skills"]:
        pdf.cell(0, 6, f"• {skill.strip()}", ln=True)

    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    return io.BytesIO(pdf_bytes)


# ===================== HOME =====================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ===================== Signup/Login =====================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]

        if users.find_one({"username": username}):
            return render_template("signup.html", error="Username already exists!")

        users.insert_one({
            "username": username,
            "password": generate_password_hash(request.form["password"]),
            "role": request.form["role"]
        })

        return redirect("/login")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = users.find_one({"username": request.form["username"]})

        if u and check_password_hash(u["password"], request.form["password"]):
            session["user"] = u["username"]
            session["role"] = u["role"]
            return redirect(f"/{u['role']}")

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


# ===================== HR SIDE =====================
@app.route("/hr")
@login_required(role="hr")
def hr_dashboard():
    return render_template("hr_dashboard.html", jds=list(jds.find()))


@app.route("/hr/upload_jd", methods=["POST"])
@login_required(role="hr")
def upload_jd():
    job_title = request.form["job_title"]
    jd_text = load_file(request.files["jd"])

    min_score = float(request.form.get("min_score", 0))
    min_exp = int(request.form.get("min_exp", 0))
    mandatory_raw = request.form.get("mandatory_skills", "")
    mandatory_skills = [s.strip().lower() for s in mandatory_raw.split(",") if s.strip()]

    if not jd_text.strip():
        return "Invalid or empty JD file", 400

    jds.insert_one({
        "title": job_title,
        "jd": jd_text,
        "uploaded_by": session["user"],
        "min_score": min_score,
        "min_experience": min_exp,
        "mandatory_skills": mandatory_skills
    })

    return redirect("/hr")

@app.route("/hr/delete_jd/<jd_id>")
@login_required(role="hr")
def delete_jd(jd_id):
    try:
        jds.delete_one({"_id": ObjectId(jd_id)})
    except InvalidId:
        return "Invalid Job ID", 400
    return redirect("/hr")


@app.route("/hr/analyze", methods=["POST"])
@login_required(role="hr")
def hr_analyze():
    jd_id = request.form["jd_id"]

    try:
        jd_doc = jds.find_one({"_id": ObjectId(jd_id)})
    except InvalidId:
        return "Invalid Job ID", 400

    if not jd_doc:
        return "Job description not found", 404

    min_score = jd_doc.get("min_score", 0)
    min_exp = jd_doc.get("min_experience", 0)
    mandatory_skills = jd_doc.get("mandatory_skills", [])

    shortlisted = []
    rejected = []

    for f in request.files.getlist("resumes")[:20]:
        resume_text = load_file(f)
        if not resume_text.strip():
            continue

        t, s, final, matched, missing = score_resume(resume_text, jd_doc["jd"])
        exp = extract_experience_years(resume_text)

        reasons = []

        if final < min_score:
            reasons.append("Below minimum score")

        if exp < min_exp:
            reasons.append("Insufficient experience")

        for skill in mandatory_skills:
            if skill not in resume_text:
                reasons.append(f"Missing mandatory skill: {skill}")

        candidate_data = {
            "filename": f.filename,
            "score": final,
            "experience": exp,
            "reasons": reasons
        }

        if reasons:
            rejected.append(candidate_data)
        else:
            shortlisted.append(candidate_data)

    shortlisted.sort(key=lambda x: x["score"], reverse=True)
    rejected.sort(key=lambda x: x["score"], reverse=True)

    return render_template(
        "hr_results.html",
        job_title=jd_doc["title"],
        shortlisted=shortlisted,
        rejected=rejected,
        min_score=min_score,
        min_exp=min_exp,
        mandatory_skills=mandatory_skills
    )

# ===================== CANDIDATE SIDE =====================
@app.route("/candidate")
@login_required(role="candidate")
def candidate_dashboard():
    openings = list(jds.find({}, {"title": 1}))

    selected_job = None
    job_id = session.get("job_id")

    if job_id:
        try:
            job_doc = jds.find_one({"_id": ObjectId(job_id)})
            if job_doc:
                selected_job = job_doc["title"]
        except InvalidId:
            session.pop("job_id", None)

    return render_template(
        "candidate_dashboard.html",
        openings=openings,
        selected_job=selected_job
    )


@app.route("/candidate/select_job/<job_id>")
@login_required(role="candidate")
def candidate_select_job(job_id):
    try:
        ObjectId(job_id)
    except InvalidId:
        return "Invalid Job ID", 400

    session["job_id"] = job_id
    session.pop("resume_text", None)
    session.pop("resume_data", None)
    session.pop("last_score", None)

    return redirect("/candidate")


@app.route("/candidate/upload", methods=["GET", "POST"])
@login_required(role="candidate")
def candidate_upload():
    job_id = session.get("job_id")
    if not job_id:
        return redirect("/candidate")

    try:
        job_doc = jds.find_one({"_id": ObjectId(job_id)})
    except InvalidId:
        return "Invalid Job ID", 400

    if not job_doc:
        return "Job description not found", 404

    job_title = job_doc["title"]

    if request.method == "POST":
        resume_text = load_file(request.files["resume"])
        if not resume_text.strip():
            return "Invalid or empty resume file", 400

        session["resume_text"] = resume_text
        session.pop("resume_data", None)
        session["improved"] = False

        # ✅ STORE UPLOADED RESUME
        resumes.insert_one({
            "username": session["user"],
            "job_id": job_id,
            "resume_text": resume_text,
            "created_with": "upload"
        })

        return render_template(
            "candidate_preview.html",
            resume=resume_text,
            job_title=job_title
        )

    return render_template("candidate_upload.html")


@app.route("/candidate/create", methods=["GET", "POST"])
@login_required(role="candidate")
def candidate_create():
    job_id = session.get("job_id")
    if not job_id:
        return redirect("/candidate")

    try:
        job_doc = jds.find_one({"_id": ObjectId(job_id)})
    except InvalidId:
        return "Invalid Job ID", 400

    if not job_doc:
        return "Job description not found", 404

    job_title = job_doc["title"]

    if request.method == "POST":
        skills_raw = request.form["skills"]
        skills_list = [s.strip() for s in re.split(r"[,\n]", skills_raw) if s.strip()]

        resume_data = {
            "name": request.form["name"],
            "email": request.form["email"],
            "phone": request.form["phone"],
            "summary": request.form["summary"],
            "skills": skills_list,
            "experience": request.form["experience"],
            "projects": request.form["projects"],
            "education": request.form["education"],
            "certifications": request.form["certifications"]
        }

        session["resume_data"] = resume_data

        session["resume_text"] = " ".join([
            resume_data["summary"],
            " ".join(skills_list),
            resume_data["projects"],
            resume_data["experience"],
            resume_data["education"],
            resume_data["certifications"]
        ])

        session["improved"] = False

        # ✅ STORE BUILDER RESUME
        resumes.insert_one({
            "username": session["user"],
            "job_id": job_id,
            "resume_text": session["resume_text"],
            "created_with": "builder"
        })

        return render_template(
            "candidate_preview.html",
            resume=resume_data,
            job_title=job_title
        )

    return render_template("candidate_create.html", resume={})



@app.route("/candidate/download")
@login_required(role="candidate")
def candidate_download_resume():
    resume_data = session.get("resume_data")
    if not resume_data:
        return "Download only works for created resumes.", 400

    pdf_stream = resume_to_pdf(resume_data)

    return send_file(
        pdf_stream,
        as_attachment=True,
        download_name="Resume.pdf",
        mimetype="application/pdf"
    )


@app.route("/candidate/check")
@login_required(role="candidate")
def candidate_check():
    job_id = session.get("job_id")
    if not job_id:
        return redirect("/candidate")

    resume = session.get("resume_text", "")
    if not resume.strip():
        return "Resume is empty", 400

    try:
        jd_doc = jds.find_one({"_id": ObjectId(job_id)})
    except InvalidId:
        return "Invalid Job ID", 400

    if not jd_doc:
        return "Job description not found", 404

    t, s, f, matched, missing = score_resume(resume, jd_doc["jd"])

    focus_skills = missing[:2]
    session["missing_skills"] = focus_skills
    session["last_score"] = f

    current_trends = []
    if focus_skills:
        current_trends.append(
            f"Deepen your practical knowledge of modern {focus_skills[0]} workflows and enterprise-grade implementation patterns."
        )
        if len(focus_skills) > 1:
            current_trends.append(
                f"Explore current tools, frameworks, and automation strategies around {focus_skills[1]}."
            )
        current_trends.append(
            "Emphasize measurable outcomes, collaboration, and the business value of your technical contributions."
        )
        current_trends.append(
            "Focus on real project experience, not just keyword lists, for stronger ATS and recruiter impact."
        )
    else:
        current_trends = [
            "Continue highlighting modern workflows, measurable results, and team collaboration.",
            "Ensure your resume reflects enterprise readiness, impact, and scalability.",
            "Use concise project narratives that connect your skills to business outcomes."
        ]

    return render_template(
        "candidate_result.html",
        job_title=jd_doc["title"],
        tfidf=t,
        semantic=s,
        final=f,
        matched=matched,
        focus_skills=focus_skills,
        current_trends=current_trends
    )


@app.route("/candidate/fix_resume")
@login_required(role="candidate")
def candidate_fix_resume():
    resume_data = session.get("resume_data")
    missing = session.get("missing_skills")

    if not resume_data:
        return "Fix works only for Resume Builder resumes.", 400

    old_score = session.get("last_score")
    added_skills = []

    if missing:
        for skill in missing[:6]:
            if skill not in resume_data["skills"]:
                resume_data["skills"].append(skill)
                added_skills.append(skill)

    session["resume_data"] = resume_data

    session["resume_text"] = " ".join([
        resume_data["summary"],
        " ".join(resume_data["skills"]),
        resume_data["projects"],
        resume_data["experience"],
        resume_data["education"],
        resume_data["certifications"]
    ])

    session["improved"] = True
    session["old_score"] = old_score
    session["skills_added"] = added_skills

    return redirect("/candidate/check")


# ===================== Global Error Handlers =====================
@app.errorhandler(404)
def not_found(e):
    return "Page not found", 404


@app.errorhandler(500)
def server_error(e):
    return "Internal server error", 500


# ===================== Run =====================
if __name__ == "__main__":
    app.run(debug=True)
