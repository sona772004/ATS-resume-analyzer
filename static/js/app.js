// DOM Elements
const dropZone = document.getElementById('dropZone');
const resumeInput = document.getElementById('resumeInput');
const fileInfo = document.getElementById('fileInfo');
const jobDescription = document.getElementById('jobDescription');
const analyzeBtn = document.getElementById('analyzeBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const uploadSection = document.getElementById('uploadSection');
const resultsSection = document.getElementById('resultsSection');
const newAnalysisBtn = document.getElementById('newAnalysisBtn');
const errorModal = document.getElementById('errorModal');
const errorMessage = document.getElementById('errorMessage');

// State
let selectedFile = null;

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

function setupEventListeners() {
    // File input change
    resumeInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);

    // Job description input
    jobDescription.addEventListener('input', validateForm);

    // Analyze button
    analyzeBtn.addEventListener('click', analyzeResume);

    // New analysis button
    newAnalysisBtn.addEventListener('click', resetAnalysis);
}

// File handling functions
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        validateAndSetFile(file);
    }
}

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        validateAndSetFile(files[0]);
    }
}

function validateAndSetFile(file) {
    // Check file type
    if (file.type !== 'application/pdf' && !file.name.endsWith('.pdf')) {
        showError('Please upload a PDF file only');
        return;
    }

    // Check file size (16MB limit)
    if (file.size > 16 * 1024 * 1024) {
        showError('File size must be less than 16MB');
        return;
    }

    selectedFile = file;
    displayFileInfo(file);
    validateForm();
}

function displayFileInfo(file) {
    const fileSize = formatFileSize(file.size);
    fileInfo.innerHTML = `
        <i class="fas fa-file-pdf"></i>
        <span><strong>${file.name}</strong> (${fileSize})</span>
        <i class="fas fa-check-circle" style="color: var(--success-color); margin-left: auto;"></i>
    `;
    fileInfo.classList.add('show');
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Form validation
function validateForm() {
    const hasFile = selectedFile !== null;
    const hasJobDesc = jobDescription.value.trim().length > 0;
    
    analyzeBtn.disabled = !(hasFile && hasJobDesc);
}

// Analysis function
async function analyzeResume() {
    if (!selectedFile || !jobDescription.value.trim()) {
        showError('Please provide both a resume and job description');
        return;
    }

    // Show loading state
    setLoadingState(true);

    try {
        const formData = new FormData();
        formData.append('resume', selectedFile);
        formData.append('job_description', jobDescription.value.trim());

        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Analysis failed');
        }

        if (data.success) {
            displayResults(data);
        } else {
            throw new Error(data.error || 'Analysis failed');
        }

    } catch (error) {
        showError(error.message);
    } finally {
        setLoadingState(false);
    }
}

function setLoadingState(loading) {
    if (loading) {
        analyzeBtn.disabled = true;
        loadingSpinner.classList.add('show');
        analyzeBtn.innerHTML = '<span class="loading-spinner show"></span> Analyzing...';
    } else {
        analyzeBtn.disabled = false;
        loadingSpinner.classList.remove('show');
        analyzeBtn.innerHTML = '<i class="fas fa-magic"></i> Analyze Resume<span class="loading-spinner" id="loadingSpinner"></span>';
    }
}

// Results display functions
function displayResults(data) {
    // Hide upload section, show results
    uploadSection.style.display = 'none';
    resultsSection.style.display = 'block';

    // Update overall score
    updateScoreDisplay(data.ats_score);

    // Update detailed scores
    updateDetailedScores(data.detailed_scores);

    // Update skills
    updateSkills(data.extracted_skills);

    // Update match section
    updateMatchSection(data.matched_skills, data.missing_skills);

    // Update recommendations
    updateRecommendations(data.recommendations);

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function updateScoreDisplay(score) {
    const scoreValue = document.getElementById('scoreValue');
    const scoreCircle = document.getElementById('scoreCircle');
    const scoreText = document.getElementById('scoreText');

    // Animate score
    animateValue(scoreValue, 0, score, 1500, '%');

    // Update circle gradient based on score
    let gradientColors;
    if (score >= 80) {
        gradientColors = ['#10b981', '#059669']; // Green
        scoreText.textContent = 'Excellent! Your resume is highly ATS-compatible';
    } else if (score >= 60) {
        gradientColors = ['#6366f1', '#8b5cf6']; // Purple/Indigo
        scoreText.textContent = 'Good match! Some improvements recommended';
    } else if (score >= 40) {
        gradientColors = ['#f59e0b', '#d97706']; // Orange
        scoreText.textContent = 'Fair match. Consider the recommendations below';
    } else {
        gradientColors = ['#ef4444', '#dc2626']; // Red
        scoreText.textContent = 'Low ATS compatibility. Significant improvements needed';
    }

    scoreCircle.style.background = `conic-gradient(${gradientColors[0]} 0%, ${gradientColors[1]} ${score}%, var(--bg-card) ${score}%, var(--bg-card) 100%)`;
    scoreValue.style.background = `linear-gradient(135deg, ${gradientColors[0]}, ${gradientColors[1]})`;
    scoreValue.style.webkitBackgroundClip = 'text';
    scoreValue.style.webkitTextFillColor = 'transparent';
    scoreValue.style.backgroundClip = 'text';
}

function updateDetailedScores(scores) {
    const scoreElements = {
        keyword: { score: document.getElementById('keywordScore'), progress: document.getElementById('keywordProgress') },
        content: { score: document.getElementById('contentScore'), progress: document.getElementById('contentProgress') },
        structure: { score: document.getElementById('structureScore'), progress: document.getElementById('structureProgress') },
        length: { score: document.getElementById('lengthScore'), progress: document.getElementById('lengthProgress') }
    };

    // Update each score with animation
    Object.keys(scores).forEach(key => {
        const score = scores[key];
        const elementKey = key === 'content_similarity' ? 'content' : 
                          key === 'keyword_match' ? 'keyword' :
                          key === 'structure' ? 'structure' : 'length';
        
        if (scoreElements[elementKey]) {
            const el = scoreElements[elementKey];
            animateValue(el.score, 0, score, 1000, '%');
            setTimeout(() => {
                el.progress.style.width = score + '%';
            }, 100);
        }
    });
}

function updateSkills(skills) {
    const technicalSkills = document.getElementById('technicalSkills');
    const toolsSkills = document.getElementById('toolsSkills');
    const softSkills = document.getElementById('softSkills');

    technicalSkills.innerHTML = createSkillTags(skills.technical);
    toolsSkills.innerHTML = createSkillTags(skills.tools);
    softSkills.innerHTML = createSkillTags(skills.soft_skills);
}

function createSkillTags(skills) {
    if (!skills || skills.length === 0) {
        return '<span class="empty-state">No skills detected</span>';
    }
    return skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('');
}

function updateMatchSection(matchedSkills, missingSkills) {
    const matchedContainer = document.getElementById('matchedSkills');
    const missingContainer = document.getElementById('missingSkills');

    matchedContainer.innerHTML = createMatchTags(matchedSkills, 'success');
    missingContainer.innerHTML = createMatchTags(missingSkills, 'warning');
}

function createMatchTags(skills, type) {
    if (!skills || skills.length === 0) {
        return '<span class="empty-state">None found</span>';
    }
    return skills.map(skill => `<span class="match-tag">${skill}</span>`).join('');
}

function updateRecommendations(recommendations) {
    const list = document.getElementById('recommendationsList');
    
    if (!recommendations || recommendations.length === 0) {
        list.innerHTML = '<li>No specific recommendations. Your resume looks good!</li>';
    } else {
        list.innerHTML = recommendations.map(rec => `<li>${rec}</li>`).join('');
    }
}

// Utility functions
function animateValue(element, start, end, duration, suffix = '') {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.round(current) + suffix;
    }, 16);
}

function resetAnalysis() {
    // Reset form
    selectedFile = null;
    resumeInput.value = '';
    jobDescription.value = '';
    fileInfo.innerHTML = '';
    fileInfo.classList.remove('show');
    
    // Show upload section, hide results
    uploadSection.style.display = 'block';
    resultsSection.style.display = 'none';
    
    // Reset button state
    analyzeBtn.disabled = true;
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showError(message) {
    errorMessage.textContent = message;
    errorModal.classList.add('show');
}

function closeModal() {
    errorModal.classList.remove('show');
}

// Close modal on outside click
errorModal.addEventListener('click', (e) => {
    if (e.target === errorModal) {
        closeModal();
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
    }
});
