"""
Challenge endpoints.

GET  /api/v1/characters/{character_id}/challenge
  Returns the 5-question challenge for a character.

POST /api/v1/challenges/submit
  Grades answers, awards points, updates match status.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db, get_open_ended_grader
from api.session import require_session_owner
from core.config import settings
from models.db_models import MatchStatus
from models.schemas import (
    ChallengeAttemptResponse,
    ChallengeQuestion,
    ChallengeQuestionsResponse,
    ChallengeResult,
    ChallengeSubmission,
    LevelChallengeResult,
    LevelChallengeSubmission,
    OpenEndedGradeResult,
    OpenEndedGradeSubmission,
)
from services import db_postgres as db
from services.level_challenges import get_level_definition
from services.open_ended_grading_service import (
    OpenEndedGradingError,
    OpenEndedGradingService,
)

router = APIRouter(tags=["challenges"])


async def _validate_challenge_access(
    session: AsyncSession,
    user_id: UUID,
    character_id: UUID,
):
    user = await db.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    character = await db.get_character(session, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found.")

    match = await db.get_match(session, user_id, character_id)
    if not match or match.status == MatchStatus.SWIPED_LEFT:
        raise HTTPException(
            status_code=403,
            detail="You must match with this character first.",
        )

    return user, character, match


@router.get(
    "/characters/{character_id}/challenge",
    response_model=ChallengeQuestionsResponse,
)
async def get_challenge(
    character_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    character = await db.get_character(session, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found.")

    challenge = await db.get_challenge_for_character(session, character_id)
    if not challenge:
        raise HTTPException(
            status_code=404,
            detail="No challenge available for this character.",
        )

    # Strip correct_answer_index before sending to client
    questions = [
        ChallengeQuestion(
            id=q["id"],
            question=q["question"],
            options=q["options"],
        )
        for q in challenge.questions
    ]
    return ChallengeQuestionsResponse(
        character_id=character_id,
        questions=questions,
    )


@router.get("/challenges/result", response_model=ChallengeAttemptResponse)
async def get_challenge_result(
    user_id: UUID = Query(..., description="Current user's UUID"),
    character_id: UUID = Query(..., description="Character UUID"),
    session: AsyncSession = Depends(get_db),
):
    await _validate_challenge_access(session, user_id, character_id)
    attempt = await db.get_challenge_attempt(session, user_id, character_id)
    if not attempt:
        raise HTTPException(
            status_code=404,
            detail="No submitted challenge result for this character.",
        )
    return ChallengeAttemptResponse.model_validate(attempt)


@router.post("/challenges/submit", response_model=ChallengeResult)
async def submit_challenge(
    request: Request,
    body: ChallengeSubmission,
    session: AsyncSession = Depends(get_db),
):
    require_session_owner(request, body.user_id)

    _, character, _ = await _validate_challenge_access(
        session, body.user_id, body.character_id
    )

    # Characters with phase-level challenges are scored exclusively through
    # /challenges/level/submit. Reject the legacy flat-challenge path for them
    # so the two scoring ledgers can't both award the same character.
    if get_level_definition(character.slug.replace("_", "-"), 1) is not None:
        raise HTTPException(
            status_code=409,
            detail="This character uses phase-level challenges; submit each level instead.",
        )

    # Load challenge first so we can grade.
    challenge = await db.get_challenge_for_character(session, body.character_id)
    if not challenge:
        raise HTTPException(
            status_code=404,
            detail="No challenge available for this character.",
        )

    questions = challenge.questions
    if len(body.answers) != len(questions):
        raise HTTPException(
            status_code=422,
            detail=f"Expected {len(questions)} answers, got {len(body.answers)}.",
        )

    # Grade.
    score = 0
    explanations: list[str] = []
    correct_answers: list[int] = []
    for q, user_answer in zip(questions, body.answers):
        correct_index = q["correct_answer_index"]
        correct_answers.append(correct_index)
        if user_answer == correct_index:
            score += 1
        explanations.append(q.get("explanation", ""))

    total = len(questions)
    passed = score >= settings.CHALLENGE_PASS_THRESHOLD

    # Points per PRD §6.5: completion bonus + (optional) pass bonus only.
    points = settings.POINTS_CHALLENGE_COMPLETE
    if passed:
        points += settings.POINTS_CHALLENGE_PASS_BONUS

    # Retake handling: if the user has a previous attempt for this character,
    # roll back the points they earned then so total_score reflects only the
    # latest attempt. Then replace the attempt row in place.
    existing_attempt = await db.get_challenge_attempt(
        session,
        body.user_id,
        body.character_id,
    )
    if existing_attempt is not None:
        await db.add_points(session, body.user_id, -existing_attempt.points_earned)

    await db.add_points(session, body.user_id, points)

    if passed:
        await db.update_match_status(
            session,
            body.user_id,
            body.character_id,
            MatchStatus.CHALLENGE_PASSED,
        )

    if existing_attempt is not None:
        existing_attempt.answers = body.answers
        existing_attempt.score = score
        existing_attempt.total = total
        existing_attempt.passed = passed
        existing_attempt.points_earned = points
        existing_attempt.explanations = explanations
        await session.commit()
    else:
        await db.create_challenge_attempt(
            session,
            user_id=body.user_id,
            character_id=body.character_id,
            answers=body.answers,
            score=score,
            total=total,
            passed=passed,
            points_earned=points,
            explanations=explanations,
        )

    return ChallengeResult(
        score=score,
        total=total,
        passed=passed,
        points_earned=points,
        explanations=explanations,
        correct_answers=correct_answers,
    )


@router.post("/challenges/level/submit", response_model=LevelChallengeResult)
async def submit_level_challenge(
    request: Request,
    body: LevelChallengeSubmission,
    session: AsyncSession = Depends(get_db),
    grader: OpenEndedGradingService = Depends(get_open_ended_grader),
):
    require_session_owner(request, body.user_id)

    user, character, _ = await _validate_challenge_access(
        session, body.user_id, body.character_id
    )

    # The DB stores underscore slugs (chi_pheo); the level data and the FE's
    # level_results are keyed by the hyphen form (chi-pheo). Normalize so the
    # award lands on the same slot the client syncs.
    character_slug = character.slug.replace("_", "-")
    definition = get_level_definition(character_slug, body.level)
    if not definition:
        raise HTTPException(
            status_code=404,
            detail="No challenge available for this character level.",
        )

    questions = definition["questions"]
    if len(body.answers) != len(questions):
        raise HTTPException(
            status_code=422,
            detail=f"Expected {len(questions)} answers, got {len(body.answers)}.",
        )

    # Grade every question first; only persist the award if grading succeeds so
    # a grader failure leaves the user's score untouched (they can retry).
    score = 0
    correct_answers: list[int] = []
    open_grades: dict[str, OpenEndedGradeResult] = {}
    for question, answer in zip(questions, body.answers):
        if question["type"] == "open_ended":
            correct_answers.append(-1)
            answer_text = answer.strip() if isinstance(answer, str) else ""
            try:
                grade = await grader.grade(
                    character_slug=character_slug,
                    character_name=character.name,
                    work_title=character.work_title,
                    phase_title=definition.get("phaseTitle"),
                    question=question["text"],
                    answer=answer_text,
                    rubric=question.get("rubric") or "",
                    evidence=question.get("evidence"),
                )
            except OpenEndedGradingError as exc:
                raise HTTPException(
                    status_code=502,
                    detail="Không chấm được câu tự luận. Vui lòng thử lại.",
                ) from exc
            open_grades[question["id"]] = OpenEndedGradeResult(**grade)
            if int(grade.get("score", 0)) == 1:
                score += 1
        else:
            correct_index = int(question["answer"])
            correct_answers.append(correct_index)
            # bool is an int subclass, so reject it explicitly as a non-answer.
            if not isinstance(answer, bool) and answer == correct_index:
                score += 1

    total = len(questions)
    passed = score >= settings.CHALLENGE_PASS_THRESHOLD
    points = settings.POINTS_LEVEL_COMPLETE
    if passed:
        points += settings.POINTS_LEVEL_PASS_BONUS

    await db.record_level_award(
        session,
        body.user_id,
        character_slug,
        body.level,
        points,
        score=score,
        total=total,
        passed=passed,
    )
    total_score = await db.get_effective_total_score(session, user)

    return LevelChallengeResult(
        level=body.level,
        phase_title=definition.get("phaseTitle"),
        score=score,
        total=total,
        passed=passed,
        points_earned=points,
        correct_answers=correct_answers,
        open_grades=open_grades,
        total_score=total_score,
    )


@router.post(
    "/challenges/grade-open-ended",
    response_model=OpenEndedGradeResult,
)
async def grade_open_ended_challenge_answer(
    body: OpenEndedGradeSubmission,
    grader: OpenEndedGradingService = Depends(get_open_ended_grader),
):
    try:
        result = await grader.grade(
            character_slug=body.character_slug,
            character_name=body.character_name,
            work_title=body.work_title,
            phase_title=body.phase_title,
            question=body.question,
            answer=body.answer,
            rubric=body.rubric,
            evidence=body.evidence,
        )
    except OpenEndedGradingError as exc:
        raise HTTPException(
            status_code=502,
            detail="Không chấm được câu tự luận. Vui lòng thử lại.",
        ) from exc
    return OpenEndedGradeResult(**result)
