# Candidate Registration & CV Upload Analysis

## Overview

ProActive People uses **Jotform** (third-party form platform) for candidate CV registration. This is a critical user-facing feature that captures candidate data.

---

## Registration Form Structure

### Form Platform
- **Provider**: Jotform
- **Form ID**: 80244397156359
- **Max File Size**: 10MB
- **Total Questions**: 13 (multi-step wizard)

### Form Fields (13 Steps)

#### Step 1: Full Name
- **Field Type**: Text (First Name + Last Name)
- **Required**: Yes
- **Purpose**: Primary identification

#### Step 2: Email
- **Field Type**: Email
- **Required**: Yes
- **Purpose**: Primary contact method

#### Step 3: Phone Number
- **Field Type**: Phone (Area Code + Number)
- **Required**: Yes
- **Purpose**: Secondary contact method

#### Step 4: Employment Status
- **Field Type**: Radio buttons
- **Required**: Yes
- **Options**:
  - Employed
  - Unemployed
  - Self-Employed
  - Student
- **Purpose**: Availability indicator

#### Step 5: Speciality
- **Field Type**: Dropdown/Select
- **Required**: No (appears optional)
- **Purpose**: Job category selection
- **Expected Values**:
  - Sales Jobs
  - Technical Jobs
  - Contact Centre Jobs
  - Accountancy Jobs
  - Commercial Jobs

#### Step 6: Expected Salary
- **Field Type**: Text/Number
- **Required**: No
- **Purpose**: Salary expectations capture

#### Step 7: Experience Level
- **Field Type**: Slider/Select
- **Required**: No
- **Options**:
  - Trainee
  - Graduate
  - Inexperienced
  - Experienced
  - Expert
- **Purpose**: Experience level assessment

#### Step 8: Available Start Date
- **Field Type**: Date picker
- **Required**: Yes
- **Purpose**: Availability timeline

#### Step 9: Resume Submission Method
- **Field Type**: Choice
- **Required**: Yes
- **Options**:
  - Upload File
  - Provide URL
- **Purpose**: CV collection method selection

#### Step 10a: Upload File (if Upload chosen)
- **Field Type**: File upload
- **Required**: Conditional
- **Max Size**: 10MB
- **Features**: Drag & drop
- **Purpose**: Direct CV upload

#### Step 10b: URL/Blog (if URL chosen)
- **Field Type**: Text (URL)
- **Required**: Conditional
- **Purpose**: Link to online CV/portfolio

#### Step 10c: Optional Upload
- **Field Type**: File upload
- **Required**: No
- **Max Size**: 10MB
- **Purpose**: Additional documents (cover letter, certifications, etc.)

#### Step 11: Job Updates Preference
- **Field Type**: Radio buttons
- **Required**: No
- **Options**:
  - Yes
  - No
- **Purpose**: Consent for marketing communications

---

## Technical Implementation Details

### Current System
- **Platform**: Jotform (SaaS form builder)
- **Integration**: Embedded iframe on website
- **Data Storage**: Jotform servers initially
- **Submission Flow**: Jotform → Email notification → Manual processing

### Limitations of Current System
1. **No Direct ATS Integration**: Forms likely exported/emailed to Bullhorn
2. **Manual Processing**: Someone must manually enter data into Bullhorn
3. **No Automation**: No automatic CV parsing or candidate profiling
4. **Third-Party Dependency**: Relies on Jotform availability
5. **Limited Validation**: Basic form validation only
6. **No Real-Time Matching**: Can't immediately match candidate to jobs

---

## Automation System Requirements

### Replace Jotform with Native Solution

**Benefits of Native Implementation:**
1. **Direct Integration**: Straight into Candidate Service and Bullhorn
2. **Automatic CV Parsing**: Parse uploaded CV immediately
3. **Instant Profiling**: Create candidate profile in real-time
4. **Job Matching**: Immediately suggest relevant jobs
5. **Better UX**: Modern, branded experience
6. **Data Ownership**: All data stays in-house
7. **Cost Savings**: Eliminate Jotform subscription

### New Candidate Registration Service Features

#### Frontend (UI)
```
Multi-Step Registration Wizard:
┌─────────────────────────────────────┐
│ Step 1: Personal Information        │
│ - Full name                         │
│ - Email, Phone                      │
│ - Employment status                 │
├─────────────────────────────────────┤
│ Step 2: Professional Details        │
│ - Speciality/Job category           │
│ - Experience level                  │
│ - Expected salary                   │
│ - Available start date              │
├─────────────────────────────────────┤
│ Step 3: CV Upload                   │
│ - File upload (drag & drop)         │
│ - Or URL to online CV               │
│ - Optional: Additional documents    │
├─────────────────────────────────────┤
│ Step 4: Preferences                 │
│ - Job alerts (Yes/No)               │
│ - Communication preferences         │
│ - GDPR consent                      │
├─────────────────────────────────────┤
│ Step 5: Review & Submit             │
│ - Preview all information           │
│ - Edit if needed                    │
│ - Submit button                     │
└─────────────────────────────────────┘
```

#### Backend Processing Flow
```
1. Candidate submits form
   ↓
2. Validate all fields
   ↓
3. Upload CV to S3/Azure Blob
   ↓
4. Parse CV with ML service
   ↓
5. Extract:
   - Skills
   - Work history
   - Education
   - Certifications
   ↓
6. Create candidate profile in:
   - PostgreSQL (primary data)
   - MongoDB (CV document)
   - Elasticsearch (searchable index)
   ↓
7. Sync to Bullhorn (via Integration Hub)
   ↓
8. Run matching algorithm
   ↓
9. Send confirmation email with:
   - Registration success
   - Relevant job matches
   - Next steps
   ↓
10. Assign to consultant (if matches found)
```

---

## Data Mapping

### Form Fields → Database Schema

**Candidate Table (PostgreSQL)**:
```sql
CREATE TABLE candidates (
  id UUID PRIMARY KEY,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  phone_area_code VARCHAR(10),
  phone_number VARCHAR(20) NOT NULL,
  employment_status VARCHAR(20), -- 'employed', 'unemployed', 'self-employed', 'student'
  speciality VARCHAR(50), -- Job category
  expected_salary_min INTEGER,
  expected_salary_max INTEGER,
  experience_level VARCHAR(20), -- 'trainee', 'graduate', 'inexperienced', 'experienced', 'expert'
  available_start_date DATE NOT NULL,
  job_alerts_enabled BOOLEAN DEFAULT true,
  cv_url VARCHAR(500), -- URL to CV file
  cv_parsed BOOLEAN DEFAULT false,
  profile_completed BOOLEAN DEFAULT false,
  source VARCHAR(50) DEFAULT 'website_registration',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**CV Documents (MongoDB)**:
```javascript
{
  candidateId: "uuid",
  originalFileName: "john_doe_cv.pdf",
  fileUrl: "s3://bucket/cvs/uuid.pdf",
  fileSize: 245678, // bytes
  mimeType: "application/pdf",
  uploadedAt: ISODate("2025-01-20T12:00:00Z"),
  parsedData: {
    text: "raw text content...",
    skills: ["JavaScript", "React", "Node.js"],
    workHistory: [...],
    education: [...],
    certifications: [...]
  },
  parsingStatus: "completed", // pending, completed, failed
  additionalDocuments: [
    {
      fileName: "cover_letter.pdf",
      fileUrl: "s3://bucket/docs/uuid_cover.pdf"
    }
  ]
}
```

---

## Enhanced Registration Features

### Beyond Basic Form

**1. Smart Form (Progressive Disclosure)**
- Show only relevant fields based on previous answers
- Example: If "Student" selected, don't ask about current salary
- If "Technical Jobs" selected, show tech-specific questions

**2. CV Auto-Fill**
- Parse uploaded CV immediately
- Pre-fill form fields from CV data
- Candidate only needs to review/confirm
- Massive UX improvement

**3. Real-Time Validation**
- Email: Check if already registered
- Phone: Verify format
- Salary: Range validation
- Date: Must be future date

**4. Instant Job Matching**
- As soon as CV uploaded, run matching
- Show relevant jobs on thank-you page
- "While we process your application, check out these 5 jobs"
- Increase engagement immediately

**5. Skills Extraction & Confirmation**
- Parse CV for skills
- Display extracted skills
- Let candidate add/remove skills
- Better data quality

**6. Profile Completeness Indicator**
```
Your Profile: 75% Complete
─────────────────────────────────────
✓ Basic Information
✓ CV Uploaded
✓ Experience Details
✗ Missing: Portfolio/LinkedIn
✗ Missing: References
```

**7. GDPR Compliance**
- Clear consent checkboxes
- Link to privacy policy
- Data retention information
- Right to deletion notice

---

## Migration Strategy

### From Jotform to Native System

**Phase 1: Parallel Running (Months 1-2)**
- Keep Jotform active
- Build native registration system
- Test with internal users
- Compare data quality

**Phase 2: Soft Launch (Month 3)**
- Native system as primary
- Jotform as backup
- Monitor conversion rates
- Gather user feedback

**Phase 3: Full Cutover (Month 4)**
- Disable Jotform
- Redirect all traffic to native system
- Export historical Jotform data
- Import into new system

**Phase 4: Historical Data Migration**
- Export all Jotform submissions
- Clean and normalize data
- Import into PostgreSQL
- Sync to Bullhorn if needed

---

## Analytics & Tracking

### Registration Funnel Metrics

**Track Each Step:**
```
Step 1 (Personal): 1000 starts
  ↓ 90% completion
Step 2 (Professional): 900 continues
  ↓ 85% completion
Step 3 (CV Upload): 765 continues
  ↓ 80% completion (drop-off point!)
Step 4 (Preferences): 612 continues
  ↓ 95% completion
Step 5 (Review): 581 completes
  = 58.1% overall completion rate
```

**Optimization Opportunities:**
- Identify drop-off points
- A/B test different field orders
- Test optional vs required fields
- Measure impact of auto-fill

### Key Performance Indicators

**Conversion Metrics:**
- Registration completion rate
- Time to complete registration
- CV upload success rate
- Auto-fill accuracy rate

**Quality Metrics:**
- Profile completeness score
- CV parsing success rate
- Duplicate detection rate
- Consultant follow-up rate

**Engagement Metrics:**
- Job alerts opt-in rate
- Immediate job matches viewed
- Application rate (post-registration)
- Return visitor rate

---

## User Experience Improvements

### Current Jotform Experience
❌ 13 separate screens (too many clicks)
❌ No auto-fill from CV
❌ No immediate feedback
❌ No job matches shown
❌ Generic confirmation page
❌ Slow loading (embedded iframe)

### Proposed Native Experience
✅ 5 streamlined steps (better flow)
✅ Auto-fill from uploaded CV
✅ Real-time validation & feedback
✅ Instant job matches on completion
✅ Personalized thank-you page
✅ Fast, modern UI (React)
✅ Mobile-optimized
✅ Progress indicator
✅ Save & continue later option

---

## Mobile Experience

### Critical Considerations
- 60%+ of job seekers use mobile
- File upload must work on mobile
- Camera integration (photo of CV)
- Touch-friendly UI
- Minimal typing required
- Auto-fill from camera scan

### Mobile-Specific Features
```
📱 Mobile Registration Flow:
1. Snap photo of CV → Auto-parse
2. Confirm basic details
3. Choose job categories
4. Set preferences
5. Done in 2 minutes!
```

---

## Integration Points

### Data Flow After Registration

**Immediate Actions:**
1. Create candidate record (PostgreSQL)
2. Store CV document (MongoDB)
3. Parse CV (ML Service)
4. Index for search (Elasticsearch)
5. Sync to Bullhorn (Integration Hub)

**Async Actions (Queue):**
6. Send confirmation email
7. Run matching algorithm
8. Assign to consultant (if matches)
9. Generate profile completeness report
10. Add to drip campaign (if opted in)

**Analytics Actions:**
11. Track registration event
12. Update funnel metrics
13. Calculate profile quality score
14. Feed data to ML training

---

## Security & Compliance

### Data Protection

**Uploaded CVs:**
- Scan for viruses/malware
- Encrypt at rest (S3/Azure)
- Encrypt in transit (TLS)
- Access controls (consultant-only)

**Personal Data (GDPR):**
- Clear consent obtained
- Purpose of data collection stated
- Right to access/delete explained
- Data retention policy (7 years)
- Audit trail of all access

**Validation:**
- SQL injection prevention
- XSS protection
- CSRF tokens
- Rate limiting (prevent spam)
- ReCAPTCHA (optional)

---

## Cost Analysis

### Current (Jotform)
- Jotform Subscription: ~£30-100/month
- Manual data entry: ~2 hours/day × £15/hour × 22 days = £660/month
- **Total: £690-760/month**

### Proposed (Native)
- Development: One-time cost
- Hosting: ~£50/month (included in infrastructure)
- Maintenance: Minimal
- Automated processing: £0 (included in platform)
- **Total: ~£50/month ongoing**

**Annual Savings: ~£8,000**

---

## Implementation Priority

### High Priority Features (MVP)
1. ✅ Multi-step form (5 steps)
2. ✅ CV file upload (10MB max)
3. ✅ Basic field validation
4. ✅ Email confirmation
5. ✅ Database storage
6. ✅ Bullhorn sync

### Medium Priority (Phase 2)
7. ✅ CV auto-parsing
8. ✅ Auto-fill from CV
9. ✅ Real-time job matching
10. ✅ Skills extraction
11. ✅ Profile completeness
12. ✅ Mobile optimization

### Future Enhancements (Phase 3)
13. ✅ Save & continue later
14. ✅ LinkedIn import
15. ✅ Video introduction upload
16. ✅ Portfolio showcase
17. ✅ Skill assessments
18. ✅ Candidate dashboard

---

## Summary

**Current State:**
- Jotform-based registration
- 13-step process
- Manual data processing
- No automation
- Cost: ~£8,000/year

**Proposed State:**
- Native React-based registration
- 5-step streamlined process
- Automatic CV parsing & profiling
- Instant job matching
- Full automation
- Cost: ~£600/year
- **Savings: £7,400/year**
- **Better UX**: Higher conversion rates
- **Better Data**: Automatic parsing & validation

---

## Next Steps

1. ✅ **Document current Jotform fields** (DONE)
2. ⚠️ **Design new registration UI/UX** (wireframes needed)
3. ⚠️ **Build Candidate Registration Service** (Phase 1)
4. ⚠️ **Implement CV parsing** (ML service)
5. ⚠️ **Create registration frontend** (React component)
6. ⚠️ **Test & validate** (UAT with recruiters)
7. ⚠️ **Migrate historical data** (Jotform export)
8. ⚠️ **Launch parallel system** (soft rollout)
9. ⚠️ **Monitor metrics** (conversion, quality)
10. ⚠️ **Full cutover** (disable Jotform)

---

**The candidate registration form is a critical entry point. Automating this properly will save ~8,000/year and dramatically improve candidate experience.**
