"""
Demo - quick_match_multi() Function
====================================

Demonstrates the new quick_match_multi() function for batch CV evaluation
with detailed results for each candidate, sorted by score.
"""

import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from cv_matcher import quick_match_multi

# Job description
job_description = """
Customer Support Specialist
Innovatech Solutions - Remote UK - £30,000-£38,000

We need a technically proficient Customer Support Specialist for our SaaS product.
You'll be first point of contact helping users with technical issues.

REQUIREMENTS:
• 2+ years customer support experience (SaaS/technical preferred)
• Zendesk, Salesforce Service Cloud proficiency
• Exceptional communication and de-escalation skills
• 90%+ CSAT score maintenance
• High volume support (live chat, email, phone)
"""

print("=" * 80)
print("MULTI-CV MATCHING DEMO - quick_match_multi()")
print("=" * 80)

# Get all CV paths
cv_dir = Path(__file__).parent.parent.parent.parent / "jobs" / "CVs"
good_cvs_dir = cv_dir / "Good CVs"
bad_cvs_dir = cv_dir / "Bad CVs"

cv_paths = []
candidate_names = []

# Add good CVs
if good_cvs_dir.exists():
    for cv_file in good_cvs_dir.glob("*.pdf"):
        cv_paths.append(str(cv_file))
        # Extract name from filename (remove "(good fit).pdf")
        name = cv_file.stem.replace(" (good fit)", "").replace("_", " ")
        candidate_names.append(name)

# Add bad CVs
if bad_cvs_dir.exists():
    for cv_file in bad_cvs_dir.glob("*.pdf"):
        cv_paths.append(str(cv_file))
        # Extract name from filename (remove "(bad fit).pdf")
        name = cv_file.stem.replace(" (bad fit)", "").replace("_", " ")
        candidate_names.append(name)

if cv_paths:
    print(f"\nEvaluating {len(cv_paths)} candidates...\n")

    # Call quick_match_multi
    results = quick_match_multi(job_description, cv_paths, candidate_names)

    print(results)
else:
    print("\n❌ No CV files found in jobs/CVs directory")

print("\n" + "=" * 80)
print("✅ USAGE:")
print("=" * 80)
print("""
from cv_matcher import quick_match_multi

# With file paths and names
cvs = ["elena.pdf", "john.pdf", "mary.pdf"]
names = ["Elena Rossi", "John Smith", "Mary Jones"]
results = quick_match_multi(job_description, cvs, names)
print(results)

# Without names (auto-extracted)
cvs = ["cv1.pdf", "cv2.pdf", "cv3.pdf"]
results = quick_match_multi(job_description, cvs)
print(results)

# With CV text instead of files
cv_texts = [
    "Elena Rossi\\n4 years SaaS support\\nZendesk expert...",
    "John Smith\\n2 years customer service\\nJIRA, Confluence...",
]
results = quick_match_multi(job_description, cv_texts, ["Elena", "John"])
print(results)
""")
print("=" * 80)
