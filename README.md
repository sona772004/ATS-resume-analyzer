# AI Resume Analyzer - ATS System

A modern, AI-powered Resume Analyzer that helps job seekers optimize their resumes for Applicant Tracking Systems (ATS). Built with Python, Flask, NLP, and TF-IDF.

![ATS Resume Analyzer](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

## Features

- **PDF Resume Upload**: Drag and drop or browse to upload your resume
- **Text Extraction**: Automatically extracts text from PDF files
- **Skill Detection**: Identifies technical skills, soft skills, and tools using NLP
- **Job Description Comparison**: Compares resume against job description using TF-IDF
- **ATS Score**: Comprehensive scoring system based on:
  - Keyword matching (40%)
  - Content similarity (35%)
  - Resume structure (15%)
  - Length & completeness (10%)
- **Recommendations**: Personalized suggestions for improvement
- **Modern UI**: Beautiful dark-themed responsive design

## Tech Stack

- **Backend**: Python, Flask
- **NLP**: NLTK for natural language processing
- **ML**: scikit-learn (TF-IDF, cosine similarity)
- **PDF Processing**: PyPDF2
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Styling**: Custom CSS with modern design patterns

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone or navigate to the project directory**:
```bash
cd ats-resume-analyzer
```

2. **Create a virtual environment** (recommended):
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run the application**:
```bash
python app.py
```

5. **Open your browser** and navigate to:
```
http://localhost:5000
```

## Usage

1. **Upload your resume** (PDF format only)
2. **Paste the job description** you're applying for
3. **Click "Analyze Resume"**
4. **Review your ATS score** and detailed analysis
5. **Follow the recommendations** to improve your resume

## How It Works

### 1. PDF Text Extraction
- Uses PyPDF2 to extract text content from uploaded PDF files
- Handles multi-page PDFs

### 2. Skill Detection
- Comprehensive skills database covering:
  - Programming languages (Python, Java, JavaScript, etc.)
  - Web frameworks (Django, React, Angular, etc.)
  - Databases (MySQL, MongoDB, PostgreSQL, etc.)
  - Cloud & DevOps (AWS, Docker, Kubernetes, etc.)
  - AI/ML (TensorFlow, PyTorch, scikit-learn, etc.)
  - Soft skills (Leadership, Communication, etc.)
- Uses regex pattern matching with word boundaries for accurate detection

### 3. TF-IDF Comparison
- Converts resume and job description to TF-IDF vectors
- Calculates cosine similarity to measure content relevance

### 4. ATS Scoring Algorithm
- **Keyword Match (40%)**: Percentage of job description skills found in resume
- **Content Similarity (35%)**: TF-IDF cosine similarity score
- **Structure (15%)**: Presence of essential sections (Contact, Education, Experience, Skills)
- **Length (15%)**: Optimal word count (300-800 words)

### 5. Recommendations Engine
- Analyzes missing skills
- Suggests content improvements
- Flags structural issues
- Provides actionable feedback

## Project Structure

```
ats-resume-analyzer/
├── app.py                 # Flask application & backend logic
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main frontend template
├── static/
│   ├── css/
│   │   └── style.css     # Modern dark-themed styling
│   └── js/
│       └── app.js        # Frontend JavaScript
├── uploads/              # Temporary upload directory (auto-created)
└── README.md             # This file
```

## API Endpoints

- `GET /` - Serve the main application
- `POST /analyze` - Analyze resume against job description
  - **Parameters**: `resume` (file), `job_description` (text)
  - **Returns**: JSON with ATS scores, skills, recommendations
- `GET /health` - Health check endpoint

## Sample Response

```json
{
  "success": true,
  "ats_score": 75.5,
  "detailed_scores": {
    "keyword_match": 80.0,
    "content_similarity": 70.5,
    "structure": 85.0,
    "length": 66.67
  },
  "extracted_skills": {
    "technical": ["python", "javascript", "react"],
    "soft_skills": ["leadership", "communication"],
    "tools": ["git", "docker"]
  },
  "matched_skills": ["python", "javascript"],
  "missing_skills": ["typescript", "aws"],
  "recommendations": [
    "Consider adding these missing skills: typescript, aws",
    "Tailor your resume content to better match the job requirements"
  ],
  "word_count": 450
}
```

## Customization

### Adding New Skills
Edit the `SKILLS_DB` dictionary in `app.py` to add new skills categories or individual skills.

### Modifying Scoring Weights
Adjust the weights in the `calculate_ats_score` function:
```python
total_score = (
    scores['keyword_match'] * 0.40 +
    scores['content_similarity'] * 0.35 +
    scores['structure'] * 0.15 +
    scores['length'] * 0.10
)
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [scikit-learn](https://scikit-learn.org/) - Machine learning library
- [NLTK](https://www.nltk.org/) - Natural Language Toolkit
- [PyPDF2](https://pypdf2.readthedocs.io/) - PDF processing

## Support

For issues and questions, please open an issue on the project repository.

---

**Built with ❤️ for job seekers worldwide**
