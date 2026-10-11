def normalize_skills(skills):

    return {
        skill.strip().lower()
        for skill in skills.split(',')
        if skill.strip()
    }


def calculate_match_score(
    candidate_skills,
    required_skills
):

    candidate = normalize_skills(
        candidate_skills
    )

    required = normalize_skills(
        required_skills
    )

    if not required:
        return 0

    matched = candidate.intersection(
        required
    )

    score = (
        len(matched) / len(required)
    ) * 100

    return round(score, 2)