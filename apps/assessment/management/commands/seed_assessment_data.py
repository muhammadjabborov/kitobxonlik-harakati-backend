"""
Management command: seed_assessment_data

Creates a full set of sample data for the competition and assessment apps so
that all APIs can be tested immediately without any manual admin work.

Usage:
    python manage.py seed_assessment_data
    python manage.py seed_assessment_data --flush   # wipe existing data first
"""

import random
from datetime import date, datetime, time

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.assessment.enums import QuestionTypeChoices
from apps.assessment.models import (
    AssessmentQuestion,
    AssessmentQuestionDistribution,
    MonthlyAssessment,
    QuestionOption,
    UserMonthlyAssessmentAttempt,
    UserQuestionAnswer,
)
from apps.competition.models import (
    CompetitionMonth,
    CompetitionMonthGrade,
    CompetitionSeason,
)
from apps.users.choices import GradeChoices
from apps.users.models import User


class Command(BaseCommand):
    help = "Seed sample data for competition and assessment apps (development / testing only)"

    # ── Season ────────────────────────────────────────────────────────────────
    SEASON_TITLE = "2025-2026 o'quv yili"
    SEASON_YEAR = 2026

    # ── Months — mix of past (available) and future (locked) ──────────────────
    MONTHS = [
        date(2026, 1, 1),  # past – available
        date(2026, 2, 1),  # past – available
        date(2026, 3, 1),  # past – available
        date(2026, 4, 1),  # past – available
        date(2026, 5, 1),  # past – available
        date(2026, 6, 1),  # current month – available
        date(2026, 7, 1),  # future – locked
        date(2026, 8, 1),  # future – locked
    ]

    # ── Question pool per assessment ──────────────────────────────────────────
    MCQ_PER_ASSESSMENT = 10  # questions in the pool
    SHORT_PER_ASSESSMENT = 5  # questions in the pool
    DIST_MCQ = 7  # how many to pick per attempt
    DIST_SHORT = 3  # how many to pick per attempt
    OPTIONS_PER_MCQ = 4
    TIME_LIMIT_SECONDS = 3600  # 1 hour

    # ── Test users (one per grade) ────────────────────────────────────────────
    TEST_PASSWORD = "Test@12345"
    TEST_USERS = [
        {
            "full_name": "Test 1-5 sinf",
            "phone_number": "+998900000015",
            "grade": GradeChoices.GRADE_1_5,
        },
        {
            "full_name": "Test 6-sinf",
            "phone_number": "+998900000016",
            "grade": GradeChoices.GRADE_6,
        },
        {
            "full_name": "Test 7-sinf",
            "phone_number": "+998900000017",
            "grade": GradeChoices.GRADE_7,
        },
        {
            "full_name": "Test 8-sinf",
            "phone_number": "+998900000018",
            "grade": GradeChoices.GRADE_8,
        },
        {
            "full_name": "Test 9-sinf",
            "phone_number": "+998900000019",
            "grade": GradeChoices.GRADE_9,
        },
        {
            "full_name": "Test 10-sinf",
            "phone_number": "+998900000020",
            "grade": GradeChoices.GRADE_10,
        },
        {
            "full_name": "Test 11-sinf",
            "phone_number": "+998900000021",
            "grade": GradeChoices.GRADE_11,
        },
    ]

    # ─────────────────────────────────────────────────────────────────────────

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing competition and assessment data before seeding",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["flush"]:
            self._flush()

        season = self._seed_season()
        months = self._seed_months(season)
        month_grades = self._seed_month_grades(months)
        assessments = self._seed_assessments(month_grades)
        self._seed_questions(assessments)
        self._seed_test_users()

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Sample data seeded successfully."))
        self.stdout.write("")
        self.stdout.write(
            self.style.HTTP_INFO(f"Test user password: {self.TEST_PASSWORD}")
        )
        self.stdout.write("")
        self.stdout.write("Phone number       Grade")
        self.stdout.write("-" * 40)
        for u in self.TEST_USERS:
            self.stdout.write(f"{u['phone_number']}   {u['grade']}")

    # ── Steps ─────────────────────────────────────────────────────────────────

    def _flush(self):
        self.stdout.write("Flushing existing data...")
        UserQuestionAnswer.objects.all().delete()
        UserMonthlyAssessmentAttempt.objects.all().delete()
        AssessmentQuestion.objects.all().delete()
        AssessmentQuestionDistribution.objects.all().delete()
        MonthlyAssessment.objects.all().delete()
        CompetitionMonthGrade.objects.all().delete()
        CompetitionMonth.objects.all().delete()
        CompetitionSeason.objects.filter(title=self.SEASON_TITLE).delete()
        self.stdout.write("  Done.")

    def _seed_season(self):
        # Deactivate any other season so the unique constraint is satisfied
        CompetitionSeason.objects.exclude(title=self.SEASON_TITLE).update(
            is_active=False
        )

        season, created = CompetitionSeason.objects.update_or_create(
            title=self.SEASON_TITLE,
            defaults={"year": self.SEASON_YEAR, "is_active": True},
        )
        self.stdout.write(f"  Season: {season} ({'created' if created else 'exists'})")
        return season

    def _seed_months(self, season):
        months = []
        for month_start in self.MONTHS:
            month, _ = CompetitionMonth.objects.get_or_create(
                season=season,
                month_start=month_start,
                defaults={"is_active": True},
            )
            months.append(month)
        self.stdout.write(f"  Months: {len(months)}")
        return months

    def _seed_month_grades(self, months):
        month_grades = []
        grades = [g[0] for g in GradeChoices.choices]
        for month in months:
            for grade in grades:
                mg, _ = CompetitionMonthGrade.objects.get_or_create(
                    month=month,
                    grade=grade,
                )
                month_grades.append(mg)
        self.stdout.write(f"  Month-grade entries: {len(month_grades)}")
        return month_grades

    def _seed_assessments(self, month_grades):
        assessments = []
        for mg in month_grades:
            month_start = mg.month.month_start
            start_dt = timezone.make_aware(datetime.combine(month_start, time.min))
            end_dt = timezone.make_aware(datetime.combine(month_start, time.max))

            assessment, created = MonthlyAssessment.objects.get_or_create(
                month_grade=mg,
                defaults={
                    "start_time": start_dt,
                    "end_time": end_dt,
                    "time_limit": self.TIME_LIMIT_SECONDS,
                },
            )
            if created:
                AssessmentQuestionDistribution.objects.get_or_create(
                    monthly_assessment=assessment,
                    question_type=QuestionTypeChoices.MULTIPLE_CHOICE,
                    defaults={"question_count": self.DIST_MCQ},
                )
                AssessmentQuestionDistribution.objects.get_or_create(
                    monthly_assessment=assessment,
                    question_type=QuestionTypeChoices.SHORT_ANSWER,
                    defaults={"question_count": self.DIST_SHORT},
                )
            assessments.append(assessment)
        self.stdout.write(f"  Assessments: {len(assessments)}")
        return assessments

    def _seed_questions(self, assessments):
        questions_to_create = []
        for assessment in assessments:
            if assessment.questions.exists():
                continue  # already seeded for this assessment

            grade = assessment.month_grade.grade
            month_label = assessment.month_grade.month.month_start.strftime("%b %Y")

            for i in range(1, self.MCQ_PER_ASSESSMENT + 1):
                questions_to_create.append(
                    AssessmentQuestion(
                        monthly_assessment=assessment,
                        question_type=QuestionTypeChoices.MULTIPLE_CHOICE,
                        question=(
                            f"[{grade} | {month_label}] Test savoli #{i}: "
                            f"Kitob haqida quyidagi fikrlardan qaysi biri to'g'ri?"
                        ),
                        correct_answer="",
                        is_active=True,
                    )
                )

            for i in range(1, self.SHORT_PER_ASSESSMENT + 1):
                questions_to_create.append(
                    AssessmentQuestion(
                        monthly_assessment=assessment,
                        question_type=QuestionTypeChoices.SHORT_ANSWER,
                        question=(
                            f"[{grade} | {month_label}] Qisqa javob #{i}: "
                            f"Asardagi bosh qahramon ismini kiriting."
                        ),
                        correct_answer=f"qahramon{i}",
                        is_active=True,
                    )
                )

        if not questions_to_create:
            self.stdout.write("  Questions: already seeded, skipped.")
            return

        created_questions = AssessmentQuestion.objects.bulk_create(questions_to_create)

        options_to_create = []
        for q in created_questions:
            if q.question_type != QuestionTypeChoices.MULTIPLE_CHOICE:
                continue
            correct_index = random.randint(0, self.OPTIONS_PER_MCQ - 1)
            for j in range(self.OPTIONS_PER_MCQ):
                options_to_create.append(
                    QuestionOption(
                        question=q,
                        option_text=f"Variant {chr(65 + j)}",
                        is_correct=(j == correct_index),
                    )
                )

        QuestionOption.objects.bulk_create(options_to_create)
        self.stdout.write(
            f"  Questions: {len(created_questions)} created, "
            f"{len(options_to_create)} options created."
        )

    def _seed_test_users(self):
        hashed_password = make_password(self.TEST_PASSWORD)
        for data in self.TEST_USERS:
            User.objects.update_or_create(
                phone_number=data["phone_number"],
                defaults={
                    "full_name": data["full_name"],
                    "grade": data["grade"],
                    "password": hashed_password,
                    "is_active": True,
                },
            )
        self.stdout.write(f"  Test users: {len(self.TEST_USERS)}")
