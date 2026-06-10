import random
from decimal import Decimal

from django.core.cache import cache
from django.db import transaction
from django.db.models import Prefetch
from django.utils import timezone

from apps.assessment.enums import QuestionTypeChoices
from apps.assessment.models import (
    AssessmentQuestion,
    AssessmentQuestionDistribution,
    QuestionOption,
    UserMonthlyAssessmentAttempt,
    UserQuestionAnswer,
)

QUESTIONS_CACHE_TIMEOUT = 60 * 60 * 24  # 24 hours


class AssessmentAttemptService:
    def __init__(self, user):
        self.user = user

    def start(self, assessment):
        questions_pool = self._get_cached_questions(assessment)
        selected_questions = self._pick_questions(assessment, questions_pool)
        attempt = self._create_attempt_with_answers(assessment, selected_questions)
        return self._fetch_attempt_with_questions(attempt.id)

    def get_attempt_with_questions(self, attempt):
        return self._fetch_attempt_with_questions(attempt.id)

    def submit(self, attempt, answers_data):
        db_answers = {
            a.id: a
            for a in UserQuestionAnswer.objects.select_related("question").filter(
                attempt=attempt
            )
        }

        submitted_ids = {item["user_question_id"] for item in answers_data}
        invalid_ids = submitted_ids - set(db_answers.keys())
        if invalid_ids:
            raise ValueError(f"Invalid question answer IDs: {invalid_ids}")

        option_ids = [
            item["selected_option_id"]
            for item in answers_data
            if item.get("selected_option_id")
        ]
        options_map = {
            o.id: o for o in QuestionOption.objects.filter(id__in=option_ids)
        }

        to_update = []
        correct_count = 0
        for item in answers_data:
            db_answer = db_answers[item["user_question_id"]]
            question_type = db_answer.question.question_type
            is_correct = False

            if question_type == QuestionTypeChoices.MULTIPLE_CHOICE:
                option_id = item.get("selected_option_id")
                if option_id:
                    option = options_map.get(option_id)
                    # Ensure the option belongs to the correct question (anti-cheat)
                    if option and option.question_id == db_answer.question_id:
                        db_answer.selected_option_id = option_id
                        is_correct = option.is_correct
            elif question_type == QuestionTypeChoices.SHORT_ANSWER:
                submitted = item.get("submitted_answer", "").strip()
                db_answer.submitted_answer = submitted
                is_correct = (
                    submitted.lower()
                    == db_answer.question.correct_answer.strip().lower()
                )

            db_answer.is_submitted = True
            db_answer.is_correct = is_correct
            if is_correct:
                correct_count += 1
            to_update.append(db_answer)

        total = len(db_answers)
        total_score = (
            Decimal(correct_count) / Decimal(total) * 100 if total > 0 else Decimal(0)
        )

        UserQuestionAnswer.objects.bulk_update(
            to_update,
            ["selected_option_id", "submitted_answer", "is_submitted", "is_correct"],
        )

        attempt.is_completed = True
        attempt.finished_at = timezone.now()
        attempt.spent_time_ms = int(
            (attempt.finished_at - attempt.started_at).total_seconds() * 1000
        )
        attempt.total_score = round(total_score, 2)
        attempt.save(
            update_fields=[
                "is_completed",
                "finished_at",
                "spent_time_ms",
                "total_score",
            ]
        )

        attempt.correct_count = correct_count
        attempt.total_count = total
        return attempt

    # ──────────────────────────── private ────────────────────────────

    def _get_cached_questions(self, assessment):
        cache_key = f"assessment_questions:{assessment.id}"
        questions = cache.get(cache_key)
        if questions is None:
            questions = list(
                AssessmentQuestion.objects.filter(
                    monthly_assessment=assessment,
                    is_active=True,
                )
            )
            cache.set(cache_key, questions, timeout=QUESTIONS_CACHE_TIMEOUT)
        return questions

    def _pick_questions(self, assessment, questions_pool):
        distributions = AssessmentQuestionDistribution.objects.filter(
            monthly_assessment=assessment
        )
        questions_by_type = {}
        for q in questions_pool:
            questions_by_type.setdefault(q.question_type, []).append(q)

        selected = []
        for dist in distributions:
            pool = questions_by_type.get(dist.question_type, [])
            count = min(dist.question_count, len(pool))
            selected.extend(random.sample(pool, count))

        random.shuffle(selected)
        return selected

    def _create_attempt_with_answers(self, assessment, selected_questions):
        with transaction.atomic():
            attempt = UserMonthlyAssessmentAttempt.objects.create(
                monthly_assessment=assessment,
                user=self.user,
            )
            UserQuestionAnswer.objects.bulk_create(
                [
                    UserQuestionAnswer(
                        attempt=attempt,
                        question=q,
                        order=i + 1,
                    )
                    for i, q in enumerate(selected_questions)
                ]
            )
        return attempt

    def _fetch_attempt_with_questions(self, attempt_id):
        return (
            UserMonthlyAssessmentAttempt.objects.select_related("monthly_assessment")
            .prefetch_related(
                Prefetch(
                    "user_question_answers",
                    queryset=UserQuestionAnswer.objects.order_by("order")
                    .select_related("question")
                    .prefetch_related("question__options"),
                )
            )
            .get(id=attempt_id)
        )
