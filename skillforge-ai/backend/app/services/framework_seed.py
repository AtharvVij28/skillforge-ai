"""Idempotent seed for departments and the competency framework."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.competency import Competency, CompetencyCategory, RoleCompetency
from app.models.user import Department
from app.services.competency_service import DEFAULT_PROFICIENCY_LEVELS

DEFAULT_DEPARTMENTS: tuple[tuple[str, str, str], ...] = (
    ("MOSPI", "Ministry of Statistics and Programme Implementation", "Central statistical ministry"),
    ("NSO", "National Statistical Office", "Survey operations and national accounts"),
    ("NSSTA", "National Statistical Systems Training Academy", "Training wing"),
    ("DATA_ANALYTICS", "Data & Analytics", "Analytics and DPI-facing teams"),
)

DEFAULT_CATEGORIES: tuple[tuple[str, str, str, int], ...] = (
    ("STATISTICAL", "Statistical", "Survey methods, estimation, and official statistics", 1),
    ("TECHNICAL", "Technical", "Programming, data systems, and engineering foundations", 2),
    ("DIGITAL", "Digital", "AI, machine learning, and digital public infrastructure skills", 3),
    ("GOVERNANCE", "Governance", "Data quality, ethics, and statistical governance", 4),
    ("BEHAVIOURAL", "Behavioural", "Communication, collaboration, and professional practice", 5),
)

DEFAULT_COMPETENCIES: tuple[tuple[str, str, str, str, str], ...] = (
    ("PYTHON", "Python", "TECHNICAL", "Core programming for data and automation workflows.", "HIGH"),
    ("SQL_DATABASES", "SQL & Databases", "TECHNICAL", "Querying and managing statistical datasets.", "HIGH"),
    ("ALGORITHMS", "Algorithms & Data Structures", "TECHNICAL", "Problem-solving patterns for efficient computation.", "MEDIUM"),
    ("WEB_DEVELOPMENT", "Web Development", "TECHNICAL", "Building accessible web applications and portals.", "MEDIUM"),
    ("OPERATING_SYSTEMS", "Operating Systems", "TECHNICAL", "OS concepts for secure and reliable computing.", "LOW"),
    ("COMPUTER_NETWORKS", "Computer Networks", "TECHNICAL", "Network fundamentals for digital public systems.", "MEDIUM"),
    ("CLOUD_COMPUTING", "Cloud Computing", "TECHNICAL", "Cloud platforms for scalable data workloads.", "MEDIUM"),
    ("CYBERSECURITY", "Cybersecurity", "TECHNICAL", "Security awareness for data and digital services.", "HIGH"),
    ("STATISTICS", "Statistics", "STATISTICAL", "Survey methods, estimation, and statistical reasoning.", "HIGH"),
    ("DATA_SCIENCE", "Data Science", "STATISTICAL", "End-to-end analysis from data prep to insight.", "HIGH"),
    ("DATA_VISUALIZATION", "Data Visualization", "STATISTICAL", "Clear charts and briefing-ready visual communication.", "MEDIUM"),
    ("MACHINE_LEARNING", "Machine Learning", "DIGITAL", "Foundations of supervised and unsupervised learning.", "MEDIUM"),
    ("ARTIFICIAL_INTELLIGENCE", "Artificial Intelligence", "DIGITAL", "Responsible AI concepts for public-sector analytics.", "MEDIUM"),
    ("DATA_GOVERNANCE", "Data Governance", "GOVERNANCE", "Quality, metadata, and stewardship of official data.", "HIGH"),
    ("OFFICIAL_STATISTICS", "Official Statistics", "GOVERNANCE", "Principles and practice of the national statistical system.", "HIGH"),
    ("COMMUNICATION", "Communication", "BEHAVIOURAL", "Briefing, writing, and stakeholder communication.", "MEDIUM"),
    ("COLLABORATION", "Collaboration", "BEHAVIOURAL", "Working across teams and departments.", "MEDIUM"),
)

DEFAULT_ROLE_REQUIREMENTS: tuple[tuple[str, str, int, str], ...] = (
    ("STATISTICAL_OFFICER", "PYTHON", 80, "HIGH"),
    ("STATISTICAL_OFFICER", "STATISTICS", 85, "HIGH"),
    ("STATISTICAL_OFFICER", "SQL_DATABASES", 75, "HIGH"),
    ("STATISTICAL_OFFICER", "DATA_VISUALIZATION", 70, "MEDIUM"),
    ("STATISTICAL_OFFICER", "DATA_GOVERNANCE", 80, "HIGH"),
    ("DATA_ANALYST", "PYTHON", 75, "HIGH"),
    ("DATA_ANALYST", "SQL_DATABASES", 85, "HIGH"),
    ("DATA_ANALYST", "DATA_SCIENCE", 70, "HIGH"),
    ("DATA_ANALYST", "MACHINE_LEARNING", 60, "MEDIUM"),
)


def ensure_default_departments(db: Session) -> dict[str, Department]:
    existing = {
        row.code: row
        for row in db.scalars(select(Department).where(Department.code.in_([c[0] for c in DEFAULT_DEPARTMENTS]))).all()
    }
    created = False
    for code, name, description in DEFAULT_DEPARTMENTS:
        if code not in existing:
            row = Department(code=code, name=name, description=description)
            db.add(row)
            existing[code] = row
            created = True
    if created:
        db.commit()
    return existing


def ensure_competency_framework(db: Session) -> None:
    ensure_default_departments(db)

    categories = {
        row.code: row
        for row in db.scalars(
            select(CompetencyCategory).where(CompetencyCategory.code.in_([c[0] for c in DEFAULT_CATEGORIES]))
        ).all()
    }
    created_categories = False
    for code, name, description, sort_order in DEFAULT_CATEGORIES:
        if code not in categories:
            row = CompetencyCategory(code=code, name=name, description=description, sort_order=sort_order)
            db.add(row)
            categories[code] = row
            created_categories = True
    if created_categories:
        db.commit()
        categories = {row.code: row for row in db.scalars(select(CompetencyCategory)).all()}

    competencies = {
        row.code: row
        for row in db.scalars(select(Competency).where(Competency.code.in_([c[0] for c in DEFAULT_COMPETENCIES]))).all()
    }
    created_competencies = False
    for code, name, category_code, description, priority in DEFAULT_COMPETENCIES:
        if code not in competencies:
            category = categories[category_code]
            row = Competency(
                code=code,
                name=name,
                category_id=category.id,
                description=description,
                proficiency_levels=DEFAULT_PROFICIENCY_LEVELS,
                default_priority=priority,
                is_active=True,
            )
            db.add(row)
            competencies[code] = row
            created_competencies = True
    if created_competencies:
        db.commit()
        competencies = {row.code: row for row in db.scalars(select(Competency)).all()}

    created_requirements = False
    for role_code, competency_code, score, priority in DEFAULT_ROLE_REQUIREMENTS:
        competency = competencies.get(competency_code)
        if competency is None:
            continue
        existing = db.scalar(
            select(RoleCompetency).where(
                RoleCompetency.role_code == role_code,
                RoleCompetency.competency_id == competency.id,
                RoleCompetency.department_id.is_(None),
            )
        )
        if existing is None:
            db.add(
                RoleCompetency(
                    role_code=role_code,
                    department_id=None,
                    competency_id=competency.id,
                    required_score=Decimal(score),
                    priority=priority,
                    relevance_weight=Decimal("1.00"),
                )
            )
            created_requirements = True
    if created_requirements:
        db.commit()
