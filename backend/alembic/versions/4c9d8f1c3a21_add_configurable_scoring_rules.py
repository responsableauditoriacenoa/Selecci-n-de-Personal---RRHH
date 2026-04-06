"""add configurable scoring rules

Revision ID: 4c9d8f1c3a21
Revises: 2f7c1a9b4d12
Create Date: 2026-04-06 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4c9d8f1c3a21"
down_revision = "2f7c1a9b4d12"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("job_profiles", sa.Column("scoring_dimensions_json", sa.JSON(), nullable=True))

    op.add_column("job_requirements", sa.Column("dimension", sa.String(length=100), nullable=True))
    op.add_column("job_requirements", sa.Column("keywords_json", sa.JSON(), nullable=True))
    op.add_column("job_requirements", sa.Column("match_mode", sa.String(length=20), nullable=True))
    op.add_column("job_requirements", sa.Column("failure_mode", sa.String(length=20), nullable=True))

    op.add_column("job_questions", sa.Column("dimension", sa.String(length=100), nullable=True))
    op.add_column("job_questions", sa.Column("opciones_json", sa.JSON(), nullable=True))
    op.add_column("job_questions", sa.Column("respuestas_aceptadas_json", sa.JSON(), nullable=True))
    op.add_column("job_questions", sa.Column("failure_mode", sa.String(length=20), nullable=True))

    op.add_column("application_scores", sa.Column("dimension_scores_json", sa.JSON(), nullable=True))

    op.execute("UPDATE job_profiles SET scoring_dimensions_json = '[]' WHERE scoring_dimensions_json IS NULL")
    op.execute("UPDATE job_requirements SET dimension = COALESCE(tipo, 'general') WHERE dimension IS NULL")
    op.execute("UPDATE job_requirements SET keywords_json = '[]' WHERE keywords_json IS NULL")
    op.execute("UPDATE job_requirements SET match_mode = 'any' WHERE match_mode IS NULL")
    op.execute("UPDATE job_requirements SET failure_mode = CASE WHEN obligatorio THEN 'revisar' ELSE 'revisar' END WHERE failure_mode IS NULL")
    op.execute("UPDATE job_questions SET dimension = 'preguntas' WHERE dimension IS NULL")
    op.execute("UPDATE job_questions SET opciones_json = '[]' WHERE opciones_json IS NULL")
    op.execute("UPDATE job_questions SET respuestas_aceptadas_json = '[]' WHERE respuestas_aceptadas_json IS NULL")
    op.execute("UPDATE job_questions SET failure_mode = CASE WHEN eliminatoria THEN 'descarte' ELSE 'revisar' END WHERE failure_mode IS NULL")
    op.execute("UPDATE application_scores SET dimension_scores_json = '[]' WHERE dimension_scores_json IS NULL")

    op.alter_column("job_profiles", "scoring_dimensions_json", nullable=False)
    op.alter_column("job_requirements", "dimension", nullable=False)
    op.alter_column("job_requirements", "keywords_json", nullable=False)
    op.alter_column("job_requirements", "match_mode", nullable=False)
    op.alter_column("job_requirements", "failure_mode", nullable=False)
    op.alter_column("job_questions", "dimension", nullable=False)
    op.alter_column("job_questions", "opciones_json", nullable=False)
    op.alter_column("job_questions", "respuestas_aceptadas_json", nullable=False)
    op.alter_column("job_questions", "failure_mode", nullable=False)
    op.alter_column("application_scores", "dimension_scores_json", nullable=False)


def downgrade() -> None:
    op.drop_column("application_scores", "dimension_scores_json")

    op.drop_column("job_questions", "failure_mode")
    op.drop_column("job_questions", "respuestas_aceptadas_json")
    op.drop_column("job_questions", "opciones_json")
    op.drop_column("job_questions", "dimension")

    op.drop_column("job_requirements", "failure_mode")
    op.drop_column("job_requirements", "match_mode")
    op.drop_column("job_requirements", "keywords_json")
    op.drop_column("job_requirements", "dimension")

    op.drop_column("job_profiles", "scoring_dimensions_json")