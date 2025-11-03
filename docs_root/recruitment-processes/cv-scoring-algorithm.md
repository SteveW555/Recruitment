# CV Scoring Algorithm - Technical Specification

## Overview
Automated CV evaluation system that scores candidates based on job-CV alignment, with emphasis on detecting CV customization/tailoring as the strongest indicator of candidate quality.

## Scoring Components

### 1. Keyword Matching Score (30 points max)

**Purpose:** Detect exact terminology matches between job description and CV

**Algorithm:**
```
For each critical keyword in job description:
  - Exact match (case-insensitive): +3 points
  - Semantic match (synonym/related term): +1.5 points
  - No match: 0 points

Weight multipliers:
  - Required tools/systems: 2x weight
  - Required metrics: 2x weight
  - Industry terminology: 1.5x weight
  - Soft skills: 1x weight
```

**Example:**
- Job requires "Zendesk" → CV says "Zendesk" = 3 × 2 = **6 points**
- Job requires "de-escalation" → CV says "de-escalation" = 3 × 1.5 = **4.5 points**

**Maximum: 30 points**

---

### 2. Tool & Technology Match (25 points max)

**Purpose:** Measure overlap between required and candidate tools/systems

**Algorithm:**
```
Required tools extraction:
  - Extract from job requirements section
  - Extract from responsibilities section
  - Identify mandatory vs. nice-to-have

Scoring:
  - Exact tool match (mandatory): +5 points
  - Exact tool match (nice-to-have): +2 points
  - Related/similar tool: +1 point
  - Missing mandatory tool: -3 points

Calculate percentage overlap:
  Tool_Score = (matched_tools / required_tools) × 25
```

**Example:**
- Job requires: Zendesk (mandatory), Salesforce (mandatory), JIRA (nice-to-have)
- CV mentions: Zendesk, Salesforce, Intercom
- Score: (5 + 5 + 1) / 3 required tools = **11/25 points**

**Maximum: 25 points**

---

### 3. Experience & Qualification Match (20 points max)

**Purpose:** Evaluate years of experience, industry background, and role relevance

**Algorithm:**
```
Experience scoring:
  - Meets minimum years required: +5 points
  - Exceeds minimum by 50%+: +3 bonus points
  - Below minimum: proportional reduction

Industry match:
  - Exact industry match: +5 points
  - Related industry: +2 points
  - Unrelated industry: 0 points

Role relevance:
  - Same/similar role: +5 points
  - Transferable role: +2 points
  - Unrelated role: -5 points

Qualification alignment:
  - Meets requirements: +5 points
  - Exceeds requirements: +7 points
  - Below requirements: proportional reduction
```

**Example:**
- Job requires: 2 years customer support (SaaS)
- Candidate: 4 years customer support (SaaS)
- Score: 5 (minimum met) + 3 (exceeds 50%) + 5 (exact industry) + 5 (same role) = **18/20 points**

**Maximum: 20 points**

---

### 4. Customization/Tailoring Score (25 points max) 🎯

**Purpose:** Detect evidence of CV customization - THE MOST IMPORTANT INDICATOR

**Algorithm:**
```
Detect tailoring signals:

A. Exact phrase matching:
   - Job phrase found verbatim in CV: +3 points each (max 5 phrases)
   - Examples: "knowledge base articles", "high volume support"

B. Quantified metric alignment:
   - CV provides metrics matching job requirements: +5 points
   - Example: Job "90% CSAT" → CV "96% CSAT"

C. Responsibility mirroring:
   - CV experience mirrors job responsibilities: +2 points each (max 3)
   - Uses similar language structure

D. Tool prominence:
   - Required tools mentioned in summary/top section: +3 points
   - Tools buried in CV body: +1 point

E. Industry context awareness:
   - Mentions company type, work style, or domain: +2 points

Customization_Score = min(A + B + C + D + E, 25)
```

**Red Flags (deductions):**
- Generic objective statement: -3 points
- "One-size-fits-all" language: -2 points
- No job-specific keywords: -5 points

**Example:**
- Exact phrases: 5 matches × 3 = 15 points
- Quantified metrics: 1 match = 5 points
- Tool prominence: Zendesk in summary = 3 points
- Total: **23/25 points**

**Maximum: 25 points**

---

## Overall Scoring Formula

```
Total_Score = Keyword_Score + Tool_Score + Experience_Score + Customization_Score

Maximum possible: 100 points
```

### Score Interpretation

| Score Range | Classification | Recommendation |
|-------------|----------------|----------------|
| 80-100 | **Highly Suitable** | Fast-track to interview |
| 60-79 | **Suitable** | Review for interview |
| 40-59 | **Potentially Suitable** | Manual review needed |
| 20-39 | **Weak Match** | Likely reject |
| 0-19 | **Unsuitable** | Auto-reject |

---

## Advanced Features

### 1. Semantic Similarity (NLP Enhancement)

**Technology:** sentence-transformers, spaCy

**Purpose:** Detect paraphrased requirements

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def semantic_similarity(job_phrase, cv_phrase):
    """
    Returns similarity score 0-1
    """
    job_embedding = model.encode(job_phrase)
    cv_embedding = model.encode(cv_phrase)
    similarity = cosine_similarity(job_embedding, cv_embedding)

    if similarity > 0.85:
        return "exact_match"
    elif similarity > 0.70:
        return "semantic_match"
    else:
        return "no_match"
```

**Example:**
- Job: "explain complex technical concepts in simple language"
- CV: "articulate solutions clearly to non-technical users"
- Similarity: 0.78 → **semantic_match** (+1.5 points)

---

### 2. Named Entity Recognition (NER)

**Purpose:** Extract structured information from unstructured text

```python
import spacy

nlp = spacy.load("en_core_web_sm")

def extract_entities(text):
    doc = nlp(text)
    entities = {
        "tools": [],
        "organizations": [],
        "skills": [],
        "metrics": []
    }

    # Custom entity patterns for recruitment
    # Extract tools (e.g., Zendesk, Salesforce)
    # Extract metrics (e.g., "90% CSAT", "60 tickets/day")

    return entities
```

---

### 3. Disqualification Filters

**Purpose:** Automatically reject fundamentally unsuitable candidates

```python
def check_disqualifiers(job, cv):
    """
    Returns True if candidate should be auto-rejected
    """
    disqualifiers = []

    # 1. Missing mandatory experience
    if cv.years_experience < job.minimum_years:
        if (job.minimum_years - cv.years_experience) > 1:
            disqualifiers.append("insufficient_experience")

    # 2. Wrong career field
    if career_field_match(job.field, cv.field) < 0.3:
        disqualifiers.append("wrong_career_field")

    # 3. Zero required tools
    if len(get_tool_overlap(job.required_tools, cv.tools)) == 0:
        disqualifiers.append("no_tool_overlap")

    # 4. Explicit exclusions
    if any(exclusion in cv.text for exclusion in job.exclusions):
        disqualifiers.append("explicit_exclusion")
        # Example: CV says "No customer-facing experience"

    return len(disqualifiers) > 0, disqualifiers
```

---

## Implementation Architecture

```
Input: Job Description + CV
  ↓
Text Preprocessing
  - Normalize whitespace
  - Remove special characters
  - Lowercase for matching
  ↓
Entity Extraction (NER)
  - Extract tools, skills, metrics
  - Extract experience details
  ↓
Parallel Scoring
  ├─→ Keyword Matching (30pts)
  ├─→ Tool Matching (25pts)
  ├─→ Experience Matching (20pts)
  └─→ Customization Detection (25pts)
  ↓
Disqualification Check
  - Apply filters
  - Flag red flags
  ↓
Score Aggregation
  - Sum component scores
  - Apply penalties
  - Calculate confidence
  ↓
Output: Score + Breakdown + Recommendation
```

---

## Confidence Score

**Purpose:** Indicate reliability of the match score

```python
def calculate_confidence(scoring_breakdown):
    """
    Returns confidence 0-1
    """
    factors = []

    # More data = higher confidence
    if cv_word_count > 300:
        factors.append(0.2)

    # Structured CV = higher confidence
    if has_clear_sections(cv):
        factors.append(0.2)

    # Multiple signal types = higher confidence
    if keyword_matches > 5:
        factors.append(0.3)

    # Semantic matches found = higher confidence
    if semantic_matches > 3:
        factors.append(0.3)

    return min(sum(factors), 1.0)
```

---

## Output Format

```json
{
  "candidate_name": "Elena Rossi",
  "overall_score": 92,
  "classification": "Highly Suitable",
  "confidence": 0.95,
  "recommendation": "Fast-track to interview",
  "breakdown": {
    "keyword_matching": {
      "score": 28,
      "max": 30,
      "matches": [
        {"term": "Zendesk", "type": "exact", "weight": 2, "points": 6},
        {"term": "de-escalation", "type": "exact", "weight": 1.5, "points": 4.5},
        {"term": "CSAT score", "type": "exact", "weight": 2, "points": 6}
      ]
    },
    "tool_matching": {
      "score": 22,
      "max": 25,
      "required_tools": ["Zendesk", "Salesforce Service Cloud"],
      "candidate_tools": ["Zendesk", "Salesforce Service Cloud", "JIRA", "Intercom"],
      "overlap": 100,
      "missing": []
    },
    "experience_matching": {
      "score": 18,
      "max": 20,
      "years_required": 2,
      "years_candidate": 4,
      "industry_match": "exact",
      "role_match": "same"
    },
    "customization_score": {
      "score": 24,
      "max": 25,
      "signals": [
        "exact_phrase_matching: 5 phrases",
        "quantified_metrics: CSAT 96%",
        "tool_prominence: Zendesk in summary",
        "responsibility_mirroring: 3 matches"
      ],
      "red_flags": []
    }
  },
  "strengths": [
    "Exceeds experience requirements (4 years vs 2 required)",
    "Expert-level Zendesk proficiency",
    "Proven CSAT score of 96% (exceeds 90% requirement)",
    "Strong evidence of CV tailoring to job description",
    "Exact industry match (SaaS)"
  ],
  "concerns": [],
  "next_steps": "Schedule phone screen within 48 hours"
}
```

---

## Performance Targets

- **Processing Time:** <500ms per CV
- **Accuracy:** 90%+ correlation with human recruiter assessment
- **False Positive Rate:** <5% (unsuitable candidates marked suitable)
- **False Negative Rate:** <2% (suitable candidates marked unsuitable)

---

## Training & Calibration

The algorithm should be calibrated using:
1. Historical placement data (successful vs unsuccessful candidates)
2. Recruiter feedback on match quality
3. Interview-to-offer conversion rates by score band
4. A/B testing of scoring weights

---

## Integration Points

- **Input Sources:** Email parsing, ATS uploads, career portal submissions
- **Output Destinations:** Matching Engine database, recruiter dashboard, candidate pipeline
- **APIs:** RESTful API, WebSocket for real-time scoring
- **Monitoring:** Score distribution analytics, false positive/negative tracking

---

## Ethical Considerations

1. **Bias Mitigation:**
   - No demographic information used in scoring
   - Regular audits for disparate impact
   - Transparency in scoring methodology

2. **GDPR Compliance:**
   - CV data processed only with consent
   - Automated decision-making transparency
   - Right to explanation for rejection

3. **Human-in-the-Loop:**
   - Algorithm provides recommendations, not final decisions
   - Manual review required for edge cases (scores 40-60)
   - Recruiter override capability maintained

---

## References

- Original analysis: `cv-judge.md`
- Implementation: `backend/services/matching-engine/cv_matcher/`
- API Documentation: `api/cv-matching-endpoint.md`
