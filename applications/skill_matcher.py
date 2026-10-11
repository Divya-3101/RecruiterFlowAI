import re


def normalize_text(text):
    """
    Normalize text for easier skill matching.
    """
    if not text:
        return ""

    text = text.lower()

    # Convert punctuation/separators into spaces
    text = re.sub(r"[/|_\-]+", " ", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_skill(skill):
    """
    Normalize an individual skill.
    """
    return normalize_text(skill)


def extract_required_skills(required_skills):
    """
    Supports:
    Python,Django,MySQL
    Python;Django;MySQL
    Python
    Django
    MySQL
    """
    if not required_skills:
        return []

    # Convert semicolon and newlines into commas
    skills_text = required_skills.replace(";", ",")
    skills_text = skills_text.replace("\n", ",")

    skills = [
        normalize_skill(skill)
        for skill in skills_text.split(",")
        if skill.strip()
    ]

    return skills


# Common skill aliases
SKILL_ALIASES = {
    "js": "javascript",
    "react js": "react",
    "reactjs": "react",
    "restful api": "rest api",
    "restful apis": "rest api",
    "apis": "api",
    "py": "python",
    "postgres": "postgresql",
    "node": "node.js",
    "nodejs": "node.js",
}


def apply_alias(skill):
    """
    Convert common variations into a standard form.
    """
    return SKILL_ALIASES.get(skill, skill)


def skill_present_in_text(skill, text):
    """
    Check whether a skill or one of its common variations
    exists in the text.
    """

    normalized_text = normalize_text(text)
    normalized_skill = normalize_skill(skill)

    # Direct match
    if normalized_skill in normalized_text:
        return True

    # Alias match
    canonical_skill = apply_alias(normalized_skill)

    if canonical_skill in normalized_text:
        return True

    # Reverse alias matching
    for alias, canonical in SKILL_ALIASES.items():

        if canonical == normalized_skill:
            if alias in normalized_text:
                return True

    return False


def extract_skills_from_text(text, required_skills):

    matched_skills = []

    normalized_required_skills = [
        normalize_skill(skill)
        for skill in required_skills
        if skill.strip()
    ]

    for skill in normalized_required_skills:

        if skill_present_in_text(skill, text):
            matched_skills.append(skill)

    return matched_skills


def calculate_resume_match(
    resume_text,
    candidate_skills,
    required_skills
):
    """
    Calculate explicit skill match using both:
    1. Resume text
    2. Candidate profile skills
    """

    required = extract_required_skills(required_skills)

    if not required:
        return {
            "score": 0,
            "matched_skills": [],
            "missing_skills": []
        }

    # Combine resume + candidate profile skills
    combined_text = f"""
    {resume_text}

    Candidate Profile Skills:
    {candidate_skills}
    """

    matched = extract_skills_from_text(
        combined_text,
        required
    )

    missing = [
        skill
        for skill in required
        if skill not in matched
    ]

    score = (
        len(matched) / len(required)
    ) * 100

    return {
        "score": round(score, 2),
        "matched_skills": matched,
        "missing_skills": missing
    }