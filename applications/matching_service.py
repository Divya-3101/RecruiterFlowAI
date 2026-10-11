import os
import logging
from .skill_matcher import calculate_resume_match
from .ai_matcher import calculate_semantic_score

logger = logging.getLogger(__name__)


def calculate_final_match(resume_text, candidate_skills, job):
    """
    Hybrid scoring algorithm combining:
    - 70% Semantic context match via Gemini embeddings (or NLP fallback)
    - 30% Deterministic skill verification (ATS match)
    """
    # Explicit skill matching
    skill_result = calculate_resume_match(
        resume_text,
        candidate_skills,
        job.required_skills
    )

    skill_score = skill_result.get("score", 0.0)

    # Job information for semantic AI matching
    job_text = f"""
    Job Title:
    {job.title}

    Company:
    {job.company}

    Job Description:
    {job.description}

    Required Skills:
    {job.required_skills}
    """

    # AI semantic matching
    semantic_score = calculate_semantic_score(
        resume_text or "",
        job_text
    )

    # Final weighted score
    final_score = (semantic_score * 0.7) + (skill_score * 0.3)

    return {
        "semantic_score": round(semantic_score, 2),
        "skill_score": round(skill_score, 2),
        "final_score": round(final_score, 2),
        "matched_skills": skill_result.get("matched_skills", []),
        "missing_skills": skill_result.get("missing_skills", [])
    }


def evaluate_application(application):
    """
    Evaluates an Application instance by extracting resume text,
    combining with profile skills, executing the hybrid AI matcher,
    and persisting the computed scores.
    """
    if not application:
        return None

    try:
        from .resume_parser import extract_resume_text
        from accounts.models import CandidateProfile

        candidate_skills = ""
        try:
            profile = CandidateProfile.objects.filter(user=application.candidate).first()
            if profile and profile.skills:
                candidate_skills = profile.skills
        except Exception as e:
            logger.debug(f"Could not load CandidateProfile for {application.candidate}: {e}")

        resume_text = ""
        if application.resume:
            try:
                if hasattr(application.resume, "path") and os.path.exists(application.resume.path):
                    resume_text = extract_resume_text(application.resume.path)
            except Exception as e:
                logger.warning(f"Failed to access resume file for application {application.id}: {e}")

        result = calculate_final_match(
            resume_text=resume_text,
            candidate_skills=candidate_skills,
            job=application.job
        )

        application.semantic_score = result["semantic_score"]
        application.skill_score = result["skill_score"]
        application.final_score = result["final_score"]
        application.matched_skills = ", ".join(result["matched_skills"])
        application.missing_skills = ", ".join(result["missing_skills"])

        application.save(update_fields=[
            "semantic_score",
            "skill_score",
            "final_score",
            "matched_skills",
            "missing_skills"
        ])

        return result
    except Exception as e:
        logger.error(f"Error evaluating application {getattr(application, 'id', None)}: {e}")
        return None