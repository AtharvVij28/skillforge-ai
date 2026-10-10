"""Seed approved question bank and study-material catalog."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.assessment import Question
from app.models.competency import Competency
from app.models.learning import LearningResource, LearningResourceCompetency

QUESTION_BANK: tuple[tuple[str, str, list[dict[str, str]], str, str, str], ...] = (
    (
        "PYTHON",
        "SEED:PYTHON:1",
        "Which Python construct is most appropriate for iterating a list while building another list?",
        [
            {"key": "A", "text": "A list comprehension"},
            {"key": "B", "text": "A class decorator"},
            {"key": "C", "text": "A metaclass"},
            {"key": "D", "text": "A context-manager lock"},
        ],
        "A",
        "List comprehensions are the idiomatic way to transform sequences in Python.",
    ),
    (
        "PYTHON",
        "SEED:PYTHON:2",
        "Why should official statistics scripts avoid relying on hidden notebook state?",
        [
            {"key": "A", "text": "Reproducibility requires explicit inputs and a clear run order"},
            {"key": "B", "text": "Python forbids notebooks in government work"},
            {"key": "C", "text": "Hidden state makes programs run faster"},
            {"key": "D", "text": "Notebooks cannot import pandas"},
        ],
        "A",
        "Auditability depends on being able to rerun the same code with explicit inputs.",
    ),
    (
        "SQL_DATABASES",
        "SEED:SQL:1",
        "Which SQL join returns only rows that match in both tables?",
        [
            {"key": "A", "text": "INNER JOIN"},
            {"key": "B", "text": "FULL OUTER JOIN"},
            {"key": "C", "text": "CROSS JOIN"},
            {"key": "D", "text": "LEFT JOIN with no filter"},
        ],
        "A",
        "INNER JOIN keeps matching keys from both sides and drops unmatched rows.",
    ),
    (
        "SQL_DATABASES",
        "SEED:SQL:2",
        "What does GROUP BY typically require when mixing aggregated and non-aggregated columns?",
        [
            {"key": "A", "text": "Non-aggregated columns in the SELECT list should appear in GROUP BY"},
            {"key": "B", "text": "All columns must be hashed"},
            {"key": "C", "text": "Indexes must be dropped first"},
            {"key": "D", "text": "The table must be temporary"},
        ],
        "A",
        "SQL grouping is valid when non-aggregated selected columns are part of the grouping key.",
    ),
    (
        "STATISTICS",
        "SEED:STATS:1",
        "A simple random sample is primarily used to...",
        [
            {"key": "A", "text": "Give each unit a known, equal chance of selection"},
            {"key": "B", "text": "Guarantee the sample mean equals the population mean"},
            {"key": "C", "text": "Remove the need for sampling weights"},
            {"key": "D", "text": "Replace the census in all cases"},
        ],
        "A",
        "SRS provides a known selection probability, which underpins unbiased design-based inference.",
    ),
    (
        "STATISTICS",
        "SEED:STATS:2",
        "Sampling error is best described as...",
        [
            {"key": "A", "text": "Variation because only a sample, not the full population, is observed"},
            {"key": "B", "text": "A coding mistake in the questionnaire"},
            {"key": "C", "text": "A server outage during data collection"},
            {"key": "D", "text": "Deliberate falsification of records"},
        ],
        "A",
        "Sampling error is the uncertainty from observing a subset of the population.",
    ),
    (
        "DATA_GOVERNANCE",
        "SEED:GOV:1",
        "Which practice most improves stewardship of official microdata?",
        [
            {"key": "A", "text": "Document lineage, access rules, and quality checks"},
            {"key": "B", "text": "Share raw files in public chat groups for speed"},
            {"key": "C", "text": "Overwrite source files after each analysis"},
            {"key": "D", "text": "Avoid metadata because it is optional"},
        ],
        "A",
        "Governance needs lineage, controlled access, and recorded quality processes.",
    ),
    (
        "MACHINE_LEARNING",
        "SEED:ML:1",
        "What is the main risk of evaluating a model on the same rows used for training?",
        [
            {"key": "A", "text": "Overly optimistic performance from leakage / overfitting"},
            {"key": "B", "text": "The model cannot overfit by definition"},
            {"key": "C", "text": "Cross-validation becomes mandatory in SQL"},
            {"key": "D", "text": "Coefficients become unbiased automatically"},
        ],
        "A",
        "Training-set evaluation leaks information and inflates accuracy.",
    ),
    (
        "DATA_VISUALIZATION",
        "SEED:DV:1",
        "For comparing magnitudes across categories, which chart is usually clearest?",
        [
            {"key": "A", "text": "A bar chart with a zero baseline"},
            {"key": "B", "text": "A pie chart with 18 slices"},
            {"key": "C", "text": "A 3D exploding donut"},
            {"key": "D", "text": "A dual-axis chart with unrelated scales"},
        ],
        "A",
        "Bar charts with a zero baseline make magnitude comparisons easier to read.",
    ),
    (
        "DATA_SCIENCE",
        "SEED:DS:1",
        "What should happen before modelling a survey-derived dataset?",
        [
            {"key": "A", "text": "Inspect missingness, definitions, and whether weights are required"},
            {"key": "B", "text": "Fit the most complex model immediately"},
            {"key": "C", "text": "Drop all categorical variables"},
            {"key": "D", "text": "Ignore sampling design because the file is rectangular"},
        ],
        "A",
        "Data science on official statistics starts with quality, definitions, and design metadata.",
    ),
)

RESOURCES: tuple[tuple[str, str, str, str, str, str, str, float], ...] = (
    (
        "INTERNAL-PYTHON-TUTORIAL",
        "Python",
        "Python official tutorial",
        "INTERNAL",
        "Language fundamentals for reproducible data scripts.",
        "https://docs.python.org/3/tutorial/",
        "BEGINNER",
        8,
    ),
    (
        "INTERNAL-SQL-POSTGRES",
        "SQL_DATABASES",
        "PostgreSQL tutorial",
        "INTERNAL",
        "SQL querying for statistical datasets stored in PostgreSQL.",
        "https://www.postgresql.org/docs/current/tutorial.html",
        "BEGINNER",
        6,
    ),
    (
        "INTERNAL-STATS-NIST",
        "STATISTICS",
        "NIST Engineering Statistics Handbook",
        "INTERNAL",
        "Reference material for estimation, variation, and statistical thinking.",
        "https://www.itl.nist.gov/div898/handbook/",
        "INTERMEDIATE",
        10,
    ),
    (
        "INTERNAL-DV-W3",
        "DATA_VISUALIZATION",
        "W3C data visualization notes via MDN charts primer",
        "INTERNAL",
        "Clear visual encoding and accessible presentation of numbers.",
        "https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial",
        "BEGINNER",
        4,
    ),
    (
        "INTERNAL-ML-GLOSSARY",
        "MACHINE_LEARNING",
        "Google Machine Learning glossary",
        "INTERNAL",
        "Core ML terms used when assessing model validity.",
        "https://developers.google.com/machine-learning/glossary",
        "BEGINNER",
        5,
    ),
    (
        "INTERNAL-GOV-UNFPOS",
        "DATA_GOVERNANCE",
        "UN Fundamental Principles of Official Statistics",
        "INTERNAL",
        "Professional principles for quality, confidentiality, and impartiality.",
        "https://unstats.un.org/unsd/dnss/gp/fundprinciples.aspx",
        "INTERMEDIATE",
        3,
    ),
    (
        "INTERNAL-DS-CRISP",
        "DATA_SCIENCE",
        "CRISP-DM overview (Wikipedia)",
        "INTERNAL",
        "A structured process from business understanding to deployment.",
        "https://en.wikipedia.org/wiki/Cross-industry_standard_process_for_data_mining",
        "BEGINNER",
        4,
    ),
)


def ensure_learning_catalog(db: Session) -> None:
    competencies = {row.code: row for row in db.scalars(select(Competency)).all()}
    if not competencies:
        return

    created_questions = False
    existing_excerpts = {
        row.source_excerpt
        for row in db.scalars(select(Question).where(Question.source_excerpt.is_not(None))).all()
    }
    for code, seed_id, stem, options, correct, explanation in QUESTION_BANK:
        competency = competencies.get(code)
        if competency is None or seed_id in existing_excerpts:
            continue
        db.add(
            Question(
                stem=stem,
                options=options,
                correct_option=correct,
                explanation=explanation,
                difficulty="MEDIUM",
                competency_id=competency.id,
                source_excerpt=seed_id,
                generation_method="MANUAL",
                is_approved=True,
            )
        )
        created_questions = True
    if created_questions:
        db.commit()

    created_resources = False
    existing_external = {
        row.external_id for row in db.scalars(select(LearningResource).where(LearningResource.external_id.is_not(None))).all()
    }
    for external_id, competency_code, title, provider, description, url, difficulty, hours in RESOURCES:
        if external_id in existing_external:
            continue
        competency = competencies.get(competency_code)
        if competency is None:
            continue
        resource = LearningResource(
            external_id=external_id,
            title=title,
            provider=provider,
            description=description,
            url=url,
            estimated_hours=Decimal(str(hours)),
            difficulty=difficulty,
            is_mock=True,
        )
        resource.competency_links.append(
            LearningResourceCompetency(competency_id=competency.id, weight=Decimal("1.00"))
        )
        db.add(resource)
        created_resources = True
    if created_resources:
        db.commit()
