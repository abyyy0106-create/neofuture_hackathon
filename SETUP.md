# 🚀 TalentIQ App Setup & Running Guide

## Prerequisites Setup

The app is now fully configured and ready to run. All dependencies are installed and templates are styled. You just need to:

### 1. **Get MongoDB Atlas Credentials**

The app uses MongoDB Atlas (cloud-hosted MongoDB). Follow these steps:

#### Step 1: Create a MongoDB Atlas Account
- Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
- Sign up for a free account (free tier provides 512MB storage, more than enough for hackathon)
- Create a project

#### Step 2: Create a Cluster
- Click "Build a Database" → Choose M0 Free cluster
- Select your preferred region
- Create the cluster (takes ~5-10 minutes)

#### Step 3: Get Your Connection String
- In the cloud console, go to **Clusters** → **Connect** → **Drivers**
- Select **Node.js** version 5.9 or higher
- Copy the connection string, it looks like:
  ```
  mongodb+srv://username:password@cluster.mongodb.net/database_name?retryWrites=true&w=majority
  ```

#### Step 4: Edit Your `.env` File

Update `/workspaces/neofuture_hackathon/.env` with your actual MongoDB credentials:

```env
MONGO_URI=mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/talentiq?retryWrites=true&w=majority
FLASK_SECRET_KEY=your_secure_secret_key_here
```

**Replace:**
- `YOUR_USERNAME` → Your MongoDB Atlas username
- `YOUR_PASSWORD` → Your MongoDB Atlas password  
- `YOUR_CLUSTER` → Your cluster name (e.g., `cluster0`)

---

## Running the App

### Quick Start (Recommended)
```bash
cd /workspaces/neofuture_hackathon
python3 app.py
```

The app will:
- Load environment variables from `.env`
- Download the AI sentence transformer model (first run: ~200MB, takes 1-2 minutes)
- Connect to MongoDB
- Start the Flask server on `http://localhost:5000`

### Access the App
Once running, open your browser and go to:
- **Home Page:** http://localhost:5000/
- **HR Portal:** http://localhost:5000/login (then select HR role)
- **Candidate Portal:** http://localhost:5000/login (then select Candidate role)

---

## What's Included

✅ **All Python dependencies installed:**
- Flask 3.1.3 - Web framework
- Flask-PyMongo 3.0.1 - MongoDB integration
- pdfplumber 0.11.9 - PDF parsing
- python-docx 1.2.0 - DOCX parsing
- sentence-transformers 5.4.0 - AI semantic matching
- scikit-learn 1.8.0 - Machine learning utilities

✅ **Environment setup:**
- `.env` file created with python-dotenv support
- `.gitignore` configured to protect secrets

✅ **All HTML templates:**
- Enterprise-grade UI design
- Landing page (index.html)
- Candidate portal (dashboard, upload, create, preview, results)
- HR portal (dashboard, results)
- Auth pages (login, signup)

✅ **Backend modules:**
- `app.py` - Main Flask application
- `semantic_matcher.py` - AI-powered resume matching
- `resumer_parser.py` - Resume text extraction
- `scoring.py` - Scoring logic

---

## Troubleshooting

### "Cannot connect to MongoDB"
→ Check your `.env` file has the correct `MONGO_URI`
→ Verify MongoDB Atlas cluster is running
→ Double-check username/password in the connection string

### "Model download is slow"
→ First startup downloads the AI model (~200MB) from HuggingFace
→ Subsequent runs will use the cached model
→ This is normal! Grab a coffee ☕

### "Port 5000 already in use"
→ Edit `app.py` line ~750, change `app.run(host='localhost', port=5000)` to use a different port (e.g., 5001)

### "Template not found" errors
→ Make sure you're in the correct directory: `/workspaces/neofuture_hackathon`

---

## Next Steps

1. **Start the app:** `python3 app.py`
2. **Create test user:** Sign up at http://localhost:5000/signup
3. **Upload a resume:** Use the candidate portal
4. **Test matching:** Upload a job description and resumes in HR portal

Enjoy TalentIQ! 🎉
