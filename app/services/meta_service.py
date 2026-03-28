from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.meta import Company, Position
from app.models.question import Question, QuestionCompany


ROUNDS = [
    {"id": "first", "name": "一面"},
    {"id": "second", "name": "二面"},
    {"id": "third", "name": "三面"},
    {"id": "hr", "name": "HR面"},
    {"id": "written", "name": "笔试"},
]


class MetaService:
    @staticmethod
    async def get_companies(db: AsyncSession) -> list:
        result = await db.execute(
            select(Company).where(Company.is_active == True).order_by(Company.priority)
        )
        companies = result.scalars().all()
        return [{"id": c.id, "name": c.name, "logo": c.logo, "priority": c.priority} for c in companies]

    @staticmethod
    async def get_positions(db: AsyncSession) -> list:
        result = await db.execute(select(Position).where(Position.is_active == True))
        positions = result.scalars().all()
        return [{"id": p.id, "name": p.name, "category": p.category} for p in positions]

    @staticmethod
    def get_rounds() -> list:
        return ROUNDS

    @staticmethod
    async def get_company_stats(db: AsyncSession) -> list:
        companies_result = await db.execute(
            select(Company).where(Company.is_active == True).order_by(Company.priority)
        )
        companies = companies_result.scalars().all()

        stats = []
        for c in companies:
            total = (await db.execute(
                select(func.count(Question.id))
                .join(QuestionCompany, Question.id == QuestionCompany.question_id)
                .where(QuestionCompany.company_id == c.id, Question.status == "approved")
            )).scalar() or 0

            bagu = (await db.execute(
                select(func.count(Question.id))
                .join(QuestionCompany, Question.id == QuestionCompany.question_id)
                .where(QuestionCompany.company_id == c.id, Question.type == "bagu", Question.status == "approved")
            )).scalar() or 0

            stats.append({
                "company": {"id": c.id, "name": c.name, "logo": c.logo, "priority": c.priority},
                "total_questions": total,
                "bagu_count": bagu,
                "leetcode_count": total - bagu,
                "latest_question_at": None,
            })
        return stats
