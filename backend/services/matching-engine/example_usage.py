"""
Example Usage - CV Matching Tool
=================================

Demonstrates how to use the CV matching tool with the example CVs.
"""

import os
import sys
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from cv_matcher import CVMatcher


def main():
    """Run example CV matching"""

    # Initialize matcher
    print("🚀 Initializing CV Matcher...")
    matcher = CVMatcher(
        config={
            "use_nlp": False,  # Set to True if spaCy is installed
            "semantic_threshold": 0.70,
            "enable_disqualification": True,
        }
    )

    # Load job description
    job_description_path = Path(__file__).parent.parent.parent.parent / "jobs" / "Job_Description.pdf"

    if not job_description_path.exists():
        print(f"❌ Job description not found at: {job_description_path}")
        print("Please provide the job description as text instead.")
        job_description = """
Customer Support Specialist
Company: Innovatech Solutions
Location: Remote (United Kingdom)
Salary Range: £30,000 – £38,000 per annum

THE ROLE
Innovatech Solutions is seeking a highly empathetic and technically proficient Customer Support Specialist.
You will be the first point of contact for our SaaS product users, helping them navigate technical issues,
understand features, and ensure high levels of customer satisfaction and retention.

KEY RESPONSIBILITIES
• Manage a high volume of incoming support requests via live chat, email (Zendesk ticketing system),
  and occasional phone calls.
• Diagnose, troubleshoot, and resolve technical issues related to account settings, integrations,
  and product bugs.
• Maintain an average CSAT (Customer Satisfaction) score above 90%.
• Create and update internal knowledge base articles and external documentation to empower self-service.
• Escalate complex or unresolvable issues to the Tier 2 support or engineering teams efficiently.
• Identify trends in customer issues and provide proactive feedback to the Product team.

REQUIREMENTS
• Minimum 2 years of experience in a customer-facing support role, preferably for a SaaS or
  technical product.
• Proven proficiency with CRM and ticketing systems (e.g., Zendesk, Salesforce Service Cloud).
• Exceptional written and verbal communication and de-escalation skills.
• Strong ability to explain complex technical concepts in simple, user-friendly language.
• High level of empathy and a patient, customer-centric attitude.
• Ability to work independently in a fast-paced, remote environment.
        """
    else:
        # Extract text from PDF (requires PyPDF2)
        try:
            from cv_matcher.text_extractor import TextExtractor

            extractor = TextExtractor()
            job_description = extractor.extract(str(job_description_path))
        except ImportError:
            print("❌ PyPDF2 not installed. Using sample job description instead.")
            job_description = "Customer Support Specialist... (truncated)"

    print("\n" + "=" * 80)
    print("📋 JOB DESCRIPTION")
    print("=" * 80)
    print(job_description[:500] + "...\n")

    # Define CV paths
    cv_dir = Path(__file__).parent.parent.parent.parent / "jobs" / "CVs"
    good_cvs_dir = cv_dir / "Good CVs"
    bad_cvs_dir = cv_dir / "Bad CVs"

    # Example 1: Match a single good CV
    print("\n" + "=" * 80)
    print("🔍 EXAMPLE 1: Matching Elena Rossi (Good CV)")
    print("=" * 80)

    elena_cv_path = good_cvs_dir / "Elena_Rossi_CV (good fit).pdf"

    if elena_cv_path.exists():
        result = matcher.match_cv_to_job(job_description, str(elena_cv_path))
        print_result(result)
    else:
        print(f"❌ CV not found: {elena_cv_path}")

    # Example 2: Match a single bad CV
    print("\n" + "=" * 80)
    print("🔍 EXAMPLE 2: Matching Ben Carter (Bad CV)")
    print("=" * 80)

    ben_cv_path = bad_cvs_dir / "Ben_Carter_CV (bad fit).pdf"

    if ben_cv_path.exists():
        result = matcher.match_cv_to_job(job_description, str(ben_cv_path))
        print_result(result)
    else:
        print(f"❌ CV not found: {ben_cv_path}")

    # Example 3: Batch match all CVs
    print("\n" + "=" * 80)
    print("🔍 EXAMPLE 3: Batch Matching All 4 CVs")
    print("=" * 80)

    all_cvs = []
    if good_cvs_dir.exists():
        all_cvs.extend([str(f) for f in good_cvs_dir.glob("*.pdf")])
    if bad_cvs_dir.exists():
        all_cvs.extend([str(f) for f in bad_cvs_dir.glob("*.pdf")])

    if all_cvs:
        results = matcher.match_multiple_cvs(job_description, all_cvs)

        print(f"\n📊 RANKING ({len(results)} candidates):\n")
        print(f"{'Rank':<6} {'Name':<25} {'Score':<8} {'Classification':<20} {'Recommendation'}")
        print("-" * 90)

        for rank, result in enumerate(results, 1):
            emoji = "🌟" if result.overall_score >= 80 else "✅" if result.overall_score >= 60 else "⚠️" if result.overall_score >= 40 else "❌"
            print(
                f"{emoji} {rank:<4} {result.candidate_name:<25} {result.overall_score:<8.1f} {result.classification:<20} {result.recommendation}"
            )
    else:
        print("❌ No CVs found in the specified directories")

    # Example 4: Using text input (no file)
    print("\n" + "=" * 80)
    print("🔍 EXAMPLE 4: Matching CV from Text (No File Upload)")
    print("=" * 80)

    sample_cv_text = """
John Smith
07999 888 777 | john.smith@example.com

SUMMARY
Experienced Customer Support Specialist with 5 years in SaaS technical support.
Expert in Zendesk and Salesforce Service Cloud. Proven track record of maintaining
95% CSAT scores and handling high-volume support across multiple channels.

EXPERIENCE
Senior Support Agent - CloudTech Inc
2021 - Present
• Handle 70+ tickets per day via Zendesk ticketing system
• Maintain CSAT score of 95% through empathetic communication
• Create knowledge base articles reducing ticket volume by 20%
• Expert in troubleshooting SaaS integration issues

SKILLS
Tools: Zendesk, Salesforce Service Cloud, JIRA, Intercom
Skills: De-escalation, Technical Troubleshooting, Written Communication
    """

    result = matcher.match_cv_to_job(job_description, sample_cv_text, candidate_name="John Smith")
    print_result(result)


def print_result(result):
    """Pretty print match result"""

    print(f"\n👤 Candidate: {result.candidate_name}")
    print(f"📊 Overall Score: {result.overall_score:.1f}/100")
    print(f"🏷️  Classification: {result.classification}")
    print(f"🎯 Confidence: {result.confidence:.0%}")
    print(f"✅ Recommendation: {result.recommendation}")

    print(f"\n📈 Score Breakdown:")
    breakdown = result.breakdown
    print(f"   • Keyword Matching: {breakdown['keyword_matching']['score']:.1f}/30")
    print(f"   • Tool Matching: {breakdown['tool_matching']['score']:.1f}/25")
    print(f"   • Experience Matching: {breakdown['experience_matching']['score']:.1f}/20")
    print(f"   • Customization Score: {breakdown['customization_score']['score']:.1f}/25")

    if result.strengths:
        print(f"\n💪 Strengths:")
        for strength in result.strengths:
            print(f"   ✓ {strength}")

    if result.concerns:
        print(f"\n⚠️  Concerns:")
        for concern in result.concerns:
            print(f"   ! {concern}")

    print(f"\n📝 Next Steps: {result.next_steps}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()
