"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-28

"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users
    op.create_table(
        "users",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("nickname", sa.String(50), nullable=False),
        sa.Column("avatar", sa.String(500), nullable=False, server_default=""),
        sa.Column("phone", sa.String(20), unique=True, nullable=True),
        sa.Column("email", sa.String(200), unique=True, nullable=True),
        sa.Column("password_hash", sa.String(200), nullable=True),
        sa.Column("wechat_openid", sa.String(100), unique=True, nullable=True),
        sa.Column("wechat_unionid", sa.String(100), unique=True, nullable=True),
        sa.Column("level", sa.Integer, nullable=False, server_default="1"),
        sa.Column("exp", sa.Integer, nullable=False, server_default="0"),
        sa.Column("balance", sa.Float, nullable=False, server_default="0"),
        sa.Column("total_earned", sa.Float, nullable=False, server_default="0"),
        sa.Column("total_withdrawn", sa.Float, nullable=False, server_default="0"),
        sa.Column("is_member", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("member_plan", sa.String(50), nullable=True),
        sa.Column("member_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_trial", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("trial_ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("daily_free_used", sa.Integer, nullable=False, server_default="0"),
        sa.Column("daily_free_reset_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # companies
    op.create_table(
        "companies",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("logo", sa.String(500), nullable=False, server_default=""),
        sa.Column("priority", sa.Integer, nullable=False, server_default="99"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
    )

    # positions
    op.create_table(
        "positions",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("category", sa.String(50), nullable=False, server_default="engineering"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
    )

    # questions
    op.create_table(
        "questions",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("answer", sa.Text, nullable=True),
        sa.Column("uploader_id", sa.String(32), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("position_id", sa.String(50), sa.ForeignKey("positions.id"), nullable=False),
        sa.Column("recruit_type", sa.String(20), nullable=False),
        sa.Column("round", sa.String(20), nullable=False),
        sa.Column("interview_year", sa.Integer, nullable=True),
        sa.Column("interview_quarter", sa.Integer, nullable=True),
        sa.Column("leetcode_number", sa.Integer, nullable=True),
        sa.Column("leetcode_url", sa.String(500), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="approved"),
        sa.Column("confirm_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("reward_total", sa.Float, nullable=False, server_default="0"),
        sa.Column("comment_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("favorite_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # question_companies
    op.create_table(
        "question_companies",
        sa.Column("question_id", sa.String(32), sa.ForeignKey("questions.id"), primary_key=True),
        sa.Column("company_id", sa.String(50), sa.ForeignKey("companies.id"), primary_key=True),
    )

    # comments
    op.create_table(
        "comments",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("question_id", sa.String(32), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("user_id", sa.String(32), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("upvotes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("downvotes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # comment_votes
    op.create_table(
        "comment_votes",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("comment_id", sa.String(32), sa.ForeignKey("comments.id"), nullable=False),
        sa.Column("user_id", sa.String(32), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("vote_type", sa.String(10), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("comment_id", "user_id"),
    )

    # original_confirms
    op.create_table(
        "original_confirms",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("question_id", sa.String(32), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("user_id", sa.String(32), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("question_id", "user_id"),
    )

    # favorites
    op.create_table(
        "favorites",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("user_id", sa.String(32), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("question_id", sa.String(32), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "question_id"),
    )

    # notes
    op.create_table(
        "notes",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("user_id", sa.String(32), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("question_id", sa.String(32), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "question_id"),
    )

    # subscriptions
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("user_id", sa.String(32), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("plan_type", sa.String(50), nullable=False),
        sa.Column("apple_transaction_id", sa.String(200), unique=True, nullable=True),
        sa.Column("apple_product_id", sa.String(200), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("auto_renew", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # wallet_transactions
    op.create_table(
        "wallet_transactions",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("user_id", sa.String(32), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("question_id", sa.String(32), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="completed"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # withdrawals
    op.create_table(
        "withdrawals",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("user_id", sa.String(32), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("account", sa.String(200), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ai_answer_cache
    op.create_table(
        "ai_answer_cache",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("question_id", sa.String(32), sa.ForeignKey("questions.id"), unique=True, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Seed data
    op.bulk_insert(
        sa.table("companies",
            sa.column("id"), sa.column("name"), sa.column("logo"), sa.column("priority"), sa.column("is_active")
        ),
        [
            {"id": "comp_baidu", "name": "百度", "logo": "", "priority": 1, "is_active": True},
            {"id": "comp_alibaba", "name": "阿里巴巴", "logo": "", "priority": 2, "is_active": True},
            {"id": "comp_bytedance", "name": "字节跳动", "logo": "", "priority": 3, "is_active": True},
            {"id": "comp_tencent", "name": "腾讯", "logo": "", "priority": 4, "is_active": True},
            {"id": "comp_meituan", "name": "美团", "logo": "", "priority": 5, "is_active": True},
            {"id": "comp_didi", "name": "滴滴", "logo": "", "priority": 6, "is_active": True},
            {"id": "comp_netease", "name": "网易", "logo": "", "priority": 7, "is_active": True},
            {"id": "comp_jd", "name": "京东", "logo": "", "priority": 8, "is_active": True},
            {"id": "comp_kuaishou", "name": "快手", "logo": "", "priority": 9, "is_active": True},
            {"id": "comp_pdd", "name": "拼多多", "logo": "", "priority": 10, "is_active": True},
        ]
    )

    op.bulk_insert(
        sa.table("positions",
            sa.column("id"), sa.column("name"), sa.column("category"), sa.column("is_active")
        ),
        [
            {"id": "pos_frontend", "name": "前端", "category": "engineering", "is_active": True},
            {"id": "pos_backend", "name": "后端/服务端", "category": "engineering", "is_active": True},
            {"id": "pos_algorithm", "name": "算法/机器学习", "category": "engineering", "is_active": True},
            {"id": "pos_mobile", "name": "客户端(iOS/Android)", "category": "engineering", "is_active": True},
            {"id": "pos_test", "name": "测试/QA", "category": "engineering", "is_active": True},
            {"id": "pos_data", "name": "数据开发/数据分析", "category": "engineering", "is_active": True},
            {"id": "pos_pm", "name": "产品经理", "category": "product", "is_active": True},
        ]
    )


def downgrade() -> None:
    op.drop_table("ai_answer_cache")
    op.drop_table("withdrawals")
    op.drop_table("wallet_transactions")
    op.drop_table("subscriptions")
    op.drop_table("notes")
    op.drop_table("favorites")
    op.drop_table("original_confirms")
    op.drop_table("comment_votes")
    op.drop_table("comments")
    op.drop_table("question_companies")
    op.drop_table("questions")
    op.drop_table("positions")
    op.drop_table("companies")
    op.drop_table("users")
