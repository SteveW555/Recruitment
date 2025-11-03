"""
CV Matching API - FastAPI Endpoint
===================================

RESTful API for CV matching service.

Endpoints:
- POST /api/cv-matching/match-single
- POST /api/cv-matching/match-batch
- GET /api/cv-matching/health
"""

import logging
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import tempfile
import os

from cv_matcher import CVMatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CV Matching API",
    description="Automated CV evaluation and job matching service for ProActive People",
    version="1.0.0",
)

# Initialize CV matcher
cv_matcher = CVMatcher(
    config={
        "use_nlp": True,
        "nlp_model": "en_core_web_sm",
        "semantic_threshold": 0.70,
        "enable_disqualification": True,
    }
)


# Request/Response Models
class SingleMatchRequest(BaseModel):
    job_description: str = Field(..., description="Full job description text")
    cv_text: Optional[str] = Field(None, description="CV text content (if not uploading file)")
    candidate_name: Optional[str] = Field(None, description="Candidate name (optional)")


class SingleMatchResponse(BaseModel):
    success: bool
    result: dict
    message: str


class BatchMatchRequest(BaseModel):
    job_description: str = Field(..., description="Full job description text")


class BatchMatchResponse(BaseModel):
    success: bool
    results: List[dict]
    total_processed: int
    message: str


class HealthResponse(BaseModel):
    status: str
    version: str
    matcher_loaded: bool


# Endpoints


@app.get("/api/cv-matching/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy", version="1.0.0", matcher_loaded=cv_matcher is not None
    )


@app.post("/api/cv-matching/match-single", response_model=SingleMatchResponse)
async def match_single_cv(
    job_description: str = Form(...),
    cv_file: Optional[UploadFile] = File(None),
    cv_text: Optional[str] = Form(None),
    candidate_name: Optional[str] = Form(None),
):
    """
    Match a single CV against a job description.

    Args:
        job_description: Full job description text
        cv_file: CV file upload (PDF or DOCX)
        cv_text: CV text content (alternative to file upload)
        candidate_name: Optional candidate name

    Returns:
        Match result with score, classification, and recommendations
    """
    logger.info("Received single CV matching request")

    try:
        # Validate input
        if not cv_file and not cv_text:
            raise HTTPException(
                status_code=400, detail="Either cv_file or cv_text must be provided"
            )

        # Handle file upload
        cv_path_or_text = cv_text
        if cv_file:
            # Save uploaded file to temp location
            with tempfile.NamedTemporaryFile(delete=False, suffix=cv_file.filename) as tmp_file:
                content = await cv_file.read()
                tmp_file.write(content)
                cv_path_or_text = tmp_file.name

        # Perform matching
        result = cv_matcher.match_cv_to_job(
            job_description=job_description,
            cv_path_or_text=cv_path_or_text,
            candidate_name=candidate_name,
        )

        # Clean up temp file
        if cv_file and os.path.exists(cv_path_or_text):
            os.remove(cv_path_or_text)

        logger.info(
            "Matching complete - Score: %.1f, Classification: %s",
            result.overall_score,
            result.classification,
        )

        return SingleMatchResponse(
            success=True,
            result=result.to_dict(),
            message="CV matched successfully",
        )

    except Exception as e:
        logger.error("Error matching CV: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Matching failed: {str(e)}")


@app.post("/api/cv-matching/match-batch", response_model=BatchMatchResponse)
async def match_batch_cvs(
    job_description: str = Form(...),
    cv_files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None,
):
    """
    Match multiple CVs against a job description.

    Args:
        job_description: Full job description text
        cv_files: List of CV files (PDF or DOCX)

    Returns:
        List of match results, sorted by score (highest first)
    """
    logger.info("Received batch CV matching request - %d CVs", len(cv_files))

    try:
        if not cv_files:
            raise HTTPException(status_code=400, detail="At least one CV file must be provided")

        if len(cv_files) > 50:
            raise HTTPException(
                status_code=400, detail="Maximum 50 CVs per batch request"
            )

        # Save uploaded files to temp locations
        temp_files = []
        for cv_file in cv_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=cv_file.filename) as tmp_file:
                content = await cv_file.read()
                tmp_file.write(content)
                temp_files.append(tmp_file.name)

        # Perform batch matching
        results = cv_matcher.match_multiple_cvs(
            job_description=job_description, cv_paths=temp_files
        )

        # Schedule cleanup in background
        if background_tasks:
            for temp_file in temp_files:
                background_tasks.add_task(cleanup_temp_file, temp_file)
        else:
            # Clean up immediately if no background tasks
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)

        logger.info("Batch matching complete - %d results", len(results))

        return BatchMatchResponse(
            success=True,
            results=[result.to_dict() for result in results],
            total_processed=len(results),
            message=f"Successfully matched {len(results)} CVs",
        )

    except Exception as e:
        logger.error("Error in batch matching: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch matching failed: {str(e)}")


@app.post("/api/cv-matching/match-single-text")
async def match_single_cv_text_only(request: SingleMatchRequest):
    """
    Match a single CV (text only, no file upload).
    Simpler endpoint for programmatic access.

    Args:
        request: SingleMatchRequest with job_description and cv_text

    Returns:
        Match result
    """
    logger.info("Received text-only CV matching request")

    try:
        if not request.cv_text:
            raise HTTPException(status_code=400, detail="cv_text is required")

        result = cv_matcher.match_cv_to_job(
            job_description=request.job_description,
            cv_path_or_text=request.cv_text,
            candidate_name=request.candidate_name,
        )

        return JSONResponse(
            content={"success": True, "result": result.to_dict(), "message": "CV matched successfully"}
        )

    except Exception as e:
        logger.error("Error matching CV: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Matching failed: {str(e)}")


# Helper functions


def cleanup_temp_file(file_path: str):
    """Background task to clean up temporary files"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug("Cleaned up temp file: %s", file_path)
    except Exception as e:
        logger.warning("Failed to clean up temp file %s: %s", file_path, str(e))


# Run the API server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
