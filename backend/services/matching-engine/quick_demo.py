"""
Quick Demo - Simple Convenience Functions
==========================================

Demonstrates the easiest way to use the CV matching tool.
"""

import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from cv_matcher import quick_match, quick_score, quick_batch

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
print("QUICK CV MATCHING DEMO")
print("=" * 80)

# Example 1: Single CV match with formatted output
print("\n1️⃣  SINGLE CV MATCH (quick_match)\n")

cv_path = Path(__file__).parent.parent.parent.parent / "jobs" / "CVs" / "Good CVs" / "Elena_Rossi_CV (good fit).pdf"

if cv_path.exists():
    result = quick_match(job_description, str(cv_path), "Elena Rossi")
    print(result)
else:
    print("CV file not found, using sample text instead...")

    sample_cv = """
    Elena Rossi
    Senior Customer Success Specialist

    4+ years SaaS technical support experience
    Expert in Zendesk, Salesforce Service Cloud
    Maintained 96% CSAT score handling 60 tickets/day
    Created 50+ knowledge base articles
    De-escalation and customer retention specialist
    """

    result = quick_match(job_description, sample_cv, "Elena Rossi")
    print(result)

# Example 2: Just get the score
print("\n\n2️⃣  JUST GET THE SCORE (quick_score)\n")

if cv_path.exists():
    score = quick_score(job_description, str(cv_path))
    print(f"Score: {score:.1f}/100")

# Example 3: Batch matching
print("\n\n3️⃣  BATCH RANKING (quick_batch)\n")

cv_dir = Path(__file__).parent.parent.parent.parent / "jobs" / "CVs"
good_cvs = cv_dir / "Good CVs"
bad_cvs = cv_dir / "Bad CVs"

all_cvs = []
if good_cvs.exists():
    all_cvs.extend([str(f) for f in good_cvs.glob("*.pdf")])
if bad_cvs.exists():
    all_cvs.extend([str(f) for f in bad_cvs.glob("*.pdf")])

if all_cvs:
    ranking = quick_batch(job_description, all_cvs)
    print(ranking)
else:
    print("No CV files found")

print("\n" + "=" * 80)
print("✅ That's it! Three simple functions for CV matching:")
print("   • quick_match(job, cv, name) - Full formatted result")
print("   • quick_score(job, cv) - Just the score")
print("   • quick_batch(job, [cvs]) - Ranked list")
print("=" * 80)
