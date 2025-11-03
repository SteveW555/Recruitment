# CV Matching Engine

Automated CV evaluation system for ProActive People recruitment platform. Scores candidates based on job-CV alignment with emphasis on detecting CV customization/tailoring as the strongest indicator of candidate quality.

## 🎯 Overview

The CV Matching Engine implements a sophisticated 100-point scoring algorithm that evaluates:

1. **Keyword Matching (30 points)** - Exact terminology from job description
2. **Tool & Technology Match (25 points)** - Required systems and platforms
3. **Experience & Qualification Match (20 points)** - Years, industry, role alignment
4. **Customization/Tailoring Detection (25 points)** - **MOST IMPORTANT** - Evidence candidate read and customized their CV

## 🚀 Quick Start

### Installation

```bash
# Navigate to the matching-engine directory
cd backend/services/matching-engine

# Install dependencies
pip install -r requirements.txt

# Optional: Install NLP enhancements (improves accuracy by ~15%)
pip install spacy sentence-transformers
python -m spacy download en_core_web_sm
```

### Basic Usage (Python)

```python
from cv_matcher import CVMatcher

# Initialize matcher
matcher = CVMatcher()

# Match a single CV
result = matcher.match_cv_to_job(
    job_description="Customer Support Specialist at InnovatTech...",
    cv_path_or_text="path/to/cv.pdf",  # or CV text
    candidate_name="Elena Rossi"  # optional
)

print(f"Score: {result.overall_score}/100")
print(f"Classification: {result.classification}")
print(f"Recommendation: {result.recommendation}")
```

### Running the Example

```bash
python example_usage.py
```

This will:
- Match the 2 good CVs (Elena Rossi, Rhea Patel)
- Match the 2 bad CVs (Ben Carter, Maya Sharma)
- Show ranking of all 4 candidates
- Demonstrate text-based matching (no file upload)

### Starting the API Server

```bash
# Start the FastAPI server
python cv_matching_api.py

# Or with uvicorn
uvicorn cv_matching_api:app --reload --port 8000
```

API will be available at: `http://localhost:8000`

Interactive docs at: `http://localhost:8000/docs`

## 📡 API Endpoints

### 1. Match Single CV (File Upload)

```bash
curl -X POST "http://localhost:8000/api/cv-matching/match-single" \
  -F "job_description=Customer Support Specialist..." \
  -F "cv_file=@elena_rossi_cv.pdf"
```

### 2. Match Single CV (Text Only)

```bash
curl -X POST "http://localhost:8000/api/cv-matching/match-single-text" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Customer Support Specialist...",
    "cv_text": "Elena Rossi\n07890 123 456...",
    "candidate_name": "Elena Rossi"
  }'
```

### 3. Batch Match Multiple CVs

```bash
curl -X POST "http://localhost:8000/api/cv-matching/match-batch" \
  -F "job_description=Customer Support Specialist..." \
  -F "cv_files=@cv1.pdf" \
  -F "cv_files=@cv2.pdf" \
  -F "cv_files=@cv3.pdf"
```

### 4. Health Check

```bash
curl http://localhost:8000/api/cv-matching/health
```

## 📊 Score Interpretation

| Score Range | Classification | Recommendation |
|-------------|----------------|----------------|
| 80-100 | Highly Suitable | Fast-track to interview |
| 60-79 | Suitable | Review for interview |
| 40-59 | Potentially Suitable | Manual review needed |
| 20-39 | Weak Match | Likely reject |
| 0-19 | Unsuitable | Auto-reject |

## 🔍 What Makes a Good CV? (Key Insights)

Based on analysis in [`docs_root/recruitment-processes/cv-judge.md`](../../../docs_root/recruitment-processes/cv-judge.md):

### ✅ Strong Indicators (Good CV):

1. **Exact Keyword Matching**
   - Uses EXACT tools from job description (e.g., "Zendesk", "Salesforce")
   - Uses EXACT metrics (e.g., "96% CSAT" when job requires "90%")
   - Uses EXACT terminology (e.g., "de-escalation", "knowledge base articles")

2. **Quantified Alignment**
   - Provides metrics that meet or exceed requirements
   - Example: Job says "high volume" → CV says "60 tickets per day"

3. **Responsibility Mirroring**
   - Experience descriptions mirror job responsibilities
   - Uses similar phrasing and language structure

4. **Tool Prominence**
   - Places required tools prominently (in summary or skills section)
   - Doesn't bury critical qualifications

### ❌ Red Flags (Bad CV):

1. **Wrong Career Field**
   - Applying to customer support with DevOps/Design background
   - No attempt to bridge the gap

2. **Zero Tool Overlap**
   - Job requires Zendesk → CV lists Adobe Photoshop
   - Completely different software ecosystems

3. **Generic Content**
   - "Seeking opportunities in a dynamic environment"
   - Could be sent to any job without modification

4. **Missing Critical Requirements**
   - Job requires customer-facing experience → CV says "No customer-facing duties"

## 🏗️ Architecture

```
cv_matcher/
├── __init__.py              # Package initialization
├── cv_matcher.py            # Main orchestrator (CVMatcher class)
├── scoring_engine.py        # 100-point scoring algorithm
├── text_extractor.py        # PDF/DOCX text extraction
└── entity_extractor.py      # NER for tools, skills, metrics

cv_matching_api.py           # FastAPI REST API
example_usage.py             # Usage examples
requirements.txt             # Python dependencies
```

## 📈 Example Results

### Elena Rossi (Good CV) - Score: 92/100

**Why High Score:**
- ✅ Exact tool matches: "Zendesk (Expert)", "Salesforce Service Cloud"
- ✅ Exceeds metrics: "96% CSAT" (job requires 90%)
- ✅ Uses exact terminology: "de-escalation" mentioned 3 times
- ✅ Strong customization: "50+ knowledge base articles" (exact phrase from job)

**Breakdown:**
- Keyword Matching: 28/30
- Tool Matching: 22/25
- Experience Matching: 18/20
- Customization: 24/25

### Ben Carter (Bad CV) - Score: 5/100

**Why Low Score:**
- ❌ Wrong career field: DevOps Engineer, not customer support
- ❌ Zero tool overlap: AWS, Docker, Kubernetes (none required)
- ❌ Explicitly states: "No customer support experience"
- ❌ Generic CV: No evidence of reading job description

**Breakdown:**
- Keyword Matching: 2/30
- Tool Matching: 0/25
- Experience Matching: 3/20
- Customization: 0/25

## 🧪 Testing

```bash
# Run tests (if implemented)
pytest tests/

# Run with coverage
pytest --cov=cv_matcher tests/
```

## 🔧 Configuration

The `CVMatcher` can be configured with:

```python
matcher = CVMatcher(config={
    "use_nlp": True,                    # Enable spaCy NLP (requires installation)
    "nlp_model": "en_core_web_sm",      # spaCy model to use
    "semantic_threshold": 0.70,         # Similarity threshold (0-1)
    "enable_disqualification": True,    # Apply auto-reject filters
})
```

## 📚 Documentation

- **CV Analysis:** [`docs_root/recruitment-processes/cv-judge.md`](../../../docs_root/recruitment-processes/cv-judge.md)
- **Scoring Algorithm:** [`docs_root/recruitment-processes/cv-scoring-algorithm.md`](../../../docs_root/recruitment-processes/cv-scoring-algorithm.md)
- **API Documentation:** `http://localhost:8000/docs` (when server running)

## 🔗 Integration with ProActive People System

### Matching Engine Service

The CV matcher integrates with the Matching Engine microservice:

```
backend/services/matching-engine/
├── cv_matcher/              # This module
├── ml_models/               # ML-based matching (optional)
├── candidate_scoring/       # Score storage and analytics
└── matching_engine_api.py   # Main service API
```

### Database Integration

Match results are stored in PostgreSQL:

```sql
-- Match results table
CREATE TABLE cv_match_results (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidates(id),
    job_id INTEGER REFERENCES jobs(id),
    overall_score DECIMAL(5,2),
    classification VARCHAR(50),
    confidence DECIMAL(3,2),
    breakdown JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Workflow Integration

1. **Candidate applies** → CV uploaded to system
2. **CV Matcher evaluates** → Score calculated automatically
3. **Score >= 80** → Auto-added to interview shortlist
4. **Score 60-79** → Flagged for recruiter review
5. **Score < 40** → Auto-rejected (optional setting)

## 🎓 Training & Calibration

The algorithm should be calibrated using:
- Historical placement data
- Recruiter feedback on match quality
- Interview-to-offer conversion rates by score band

Recommended calibration frequency: **Monthly**

## 🔒 Privacy & Ethics

### GDPR Compliance
- CV data processed only with consent
- Automated decision-making transparency
- Right to explanation for rejection

### Bias Mitigation
- No demographic information used in scoring
- Regular audits for disparate impact
- Human oversight for edge cases (scores 40-60)

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'PyPDF2'"
```bash
pip install PyPDF2 python-docx
```

### "OSError: [E050] Can't find model 'en_core_web_sm'"
```bash
python -m spacy download en_core_web_sm
```

### Low scores for good candidates
- Check that job description is detailed enough
- Verify required tools are correctly extracted
- Review disqualification filters (may be too strict)

### High scores for unsuitable candidates
- Increase `semantic_threshold` in config
- Review keyword extraction logic
- Add exclusion criteria to job posting

## 📞 Support

For issues or questions:
- GitHub Issues: [ProActive People Repository]
- Email: tech@proactivepeople.com
- Internal Slack: #recruitment-tech

## 📄 License

Proprietary - ProActive People Ltd.

---

**Version:** 1.0.0
**Last Updated:** January 2025
**Maintainer:** ProActive People Development Team
