import os
import re
import nltk
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import string

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Comprehensive skills database
SKILLS_DB = {
    'programming': [
        'python', 'java', 'javascript', 'js', 'typescript', 'ts', 'c++', 'c#', 'c',
        'php', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab',
        'sql', 'nosql', 'html', 'css', 'sass', 'less', 'xml', 'json', 'yaml'
    ],
    'web_frameworks': [
        'django', 'flask', 'fastapi', 'spring', 'spring boot', 'express', 'react',
        'angular', 'vue', 'nextjs', 'nuxt', 'laravel', 'rails', 'asp.net',
        'bootstrap', 'tailwind', 'jquery', 'node.js', 'nodejs'
    ],
    'databases': [
        'mysql', 'postgresql', 'postgres', 'sqlite', 'mongodb', 'redis',
        'elasticsearch', 'dynamodb', 'cassandra', 'oracle', 'mariadb',
        'firebase', 'supabase', 'neo4j', 'couchdb'
    ],
    'cloud_devops': [
        'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s',
        'jenkins', 'gitlab ci', 'github actions', 'terraform', 'ansible',
        'chef', 'puppet', 'vagrant', 'prometheus', 'grafana', 'nginx',
        'apache', 'ci/cd', 'devops', 'microservices', 'serverless'
    ],
    'ai_ml': [
        'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'keras',
        'scikit-learn', 'sklearn', 'pandas', 'numpy', 'scipy', 'matplotlib',
        'seaborn', 'plotly', 'jupyter', 'colab', 'nlp', 'computer vision',
        'opencv', 'llm', 'transformers', 'huggingface', 'langchain',
        'data science', 'data analysis', 'statistics', 'regression',
        'classification', 'clustering', 'neural networks', 'cnn', 'rnn', 'lstm'
    ],
    'tools': [
        'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'trello',
        'slack', 'postman', 'swagger', 'figma', 'sketch', 'adobe xd',
        'vscode', 'intellij', 'pycharm', 'eclipse', 'vim', 'linux', 'unix',
        'bash', 'powershell', 'ssh', 'ftp', 'sftp'
    ],
    'soft_skills': [
        'leadership', 'communication', 'teamwork', 'problem solving',
        'critical thinking', 'time management', 'project management',
        'agile', 'scrum', 'kanban', 'presentation', 'mentoring'
    ],
    'data_engineering': [
        'etl', 'elt', 'data pipeline', 'data warehousing', 'big data',
        'hadoop', 'spark', 'kafka', 'airflow', 'dbt', 'snowflake',
        'databricks', 'data modeling', 'data governance'
    ],
    'mobile': [
        'android', 'ios', 'react native', 'flutter', 'xamarin',
        'ionic', 'cordova', 'swift', 'objective-c', 'kotlin'
    ],
    'testing': [
        'unit testing', 'integration testing', 'e2e testing', 'selenium',
        'cypress', 'jest', 'mocha', 'pytest', 'junit', 'testng',
        'cucumber', 'cicd', 'automation testing', 'qa'
    ]
}

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return str(e)

def clean_text(text):
    """Clean and preprocess text"""
    # Convert to lowercase
    text = text.lower()
    # Remove special characters but keep spaces
    text = re.sub(r'[^\w\s]', ' ', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

def extract_skills(text):
    """Extract skills from resume text"""
    text_lower = clean_text(text)
    found_skills = {
        'technical': [],
        'soft_skills': [],
        'tools': []
    }
    
    # Flatten skills database
    all_technical = (SKILLS_DB['programming'] + SKILLS_DB['web_frameworks'] + 
                     SKILLS_DB['databases'] + SKILLS_DB['cloud_devops'] + 
                     SKILLS_DB['ai_ml'] + SKILLS_DB['data_engineering'] +
                     SKILLS_DB['mobile'] + SKILLS_DB['testing'])
    
    # Check for technical skills
    for skill in all_technical:
        # Use word boundaries for better matching
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_skills['technical'].append(skill)
    
    # Check for soft skills
    for skill in SKILLS_DB['soft_skills']:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_skills['soft_skills'].append(skill)
    
    # Check for tools
    for tool in SKILLS_DB['tools']:
        pattern = r'\b' + re.escape(tool.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_skills['tools'].append(tool)
    
    return found_skills

def calculate_similarity(resume_text, job_description):
    """Calculate TF-IDF cosine similarity between resume and job description"""
    # Clean texts
    resume_clean = clean_text(resume_text)
    job_clean = clean_text(job_description)
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_clean, job_clean])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return similarity
    except:
        return 0.0

def calculate_ats_score(resume_text, job_description):
    """Calculate comprehensive ATS score"""
    scores = {}
    
    # 1. Keyword matching score (40%)
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)
    
    all_resume_skills = (resume_skills['technical'] + resume_skills['soft_skills'] + 
                          resume_skills['tools'])
    all_job_skills = (job_skills['technical'] + job_skills['soft_skills'] + 
                      job_skills['tools'])
    
    if all_job_skills:
        matched_skills = set(all_resume_skills) & set(all_job_skills)
        keyword_score = (len(matched_skills) / len(set(all_job_skills))) * 100
    else:
        keyword_score = 0
    
    scores['keyword_match'] = min(keyword_score, 100)
    
    # 2. Content similarity score (35%)
    similarity = calculate_similarity(resume_text, job_description)
    scores['content_similarity'] = similarity * 100
    
    # 3. Resume structure score (15%)
    structure_score = analyze_resume_structure(resume_text)
    scores['structure'] = structure_score
    
    # 4. Length and completeness score (10%)
    word_count = len(resume_text.split())
    if 300 <= word_count <= 800:
        length_score = 100
    elif word_count < 300:
        length_score = (word_count / 300) * 100
    else:
        length_score = max(0, 100 - ((word_count - 800) / 100) * 10)
    scores['length'] = length_score
    
    # Calculate weighted total score
    total_score = (
        scores['keyword_match'] * 0.40 +
        scores['content_similarity'] * 0.35 +
        scores['structure'] * 0.15 +
        scores['length'] * 0.10
    )
    
    scores['total'] = round(total_score, 2)
    
    return scores, list(matched_skills), list(set(all_job_skills) - set(all_resume_skills))

def analyze_resume_structure(text):
    """Analyze resume structure and formatting"""
    score = 0
    text_lower = text.lower()
    
    # Check for essential sections
    essential_sections = {
        'contact': ['email', 'phone', 'linkedin', 'address'],
        'education': ['education', 'degree', 'university', 'college', 'school'],
        'experience': ['experience', 'work', 'employment', 'career'],
        'skills': ['skills', 'technologies', 'technical skills', 'competencies']
    }
    
    for section, keywords in essential_sections.items():
        for keyword in keywords:
            if keyword in text_lower:
                score += 25
                break
    
    return min(score, 100)

def get_recommendations(missing_skills, scores):
    """Generate recommendations based on analysis"""
    recommendations = []
    
    if missing_skills:
        recommendations.append(f"Consider adding these missing skills: {', '.join(missing_skills[:5])}")
    
    if scores['keyword_match'] < 50:
        recommendations.append("Try to include more relevant keywords from the job description")
    
    if scores['content_similarity'] < 60:
        recommendations.append("Tailor your resume content to better match the job requirements")
    
    if scores['structure'] < 75:
        recommendations.append("Ensure your resume has clear sections: Contact, Education, Experience, Skills")
    
    if scores['length'] < 50:
        if len(recommendations) == 0 or "too short" not in str(recommendations):
            word_count = len(scores)  # placeholder
            recommendations.append("Your resume might be too short. Aim for 300-800 words")
    
    return recommendations

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_resume():
    try:
        # Check if resume file is provided
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400
        
        resume_file = request.files['resume']
        job_description = request.form.get('job_description', '')
        
        if resume_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not job_description:
            return jsonify({'error': 'Job description is required'}), 400
        
        # Validate file type
        if not resume_file.filename.endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are supported'}), 400
        
        # Save and process file
        filename = secure_filename(resume_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        resume_file.save(filepath)
        
        # Extract text from PDF
        resume_text = extract_text_from_pdf(filepath)
        
        if not resume_text or resume_text.startswith('Error'):
            os.remove(filepath)
            return jsonify({'error': 'Could not extract text from PDF'}), 400
        
        # Extract skills
        resume_skills = extract_skills(resume_text)
        
        # Calculate ATS score
        scores, matched_skills, missing_skills = calculate_ats_score(resume_text, job_description)
        
        # Generate recommendations
        recommendations = get_recommendations(missing_skills, scores)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        # Prepare response
        response = {
            'success': True,
            'ats_score': scores['total'],
            'detailed_scores': {
                'keyword_match': round(scores['keyword_match'], 2),
                'content_similarity': round(scores['content_similarity'], 2),
                'structure': round(scores['structure'], 2),
                'length': round(scores['length'], 2)
            },
            'extracted_skills': resume_skills,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'recommendations': recommendations,
            'word_count': len(resume_text.split())
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
