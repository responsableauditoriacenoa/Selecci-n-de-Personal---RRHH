"""add missing vacancy columns

Revision ID: 2f7c1a9b4d12
Revises: 8989f7e6d5e8
Create Date: 2026-03-31 20:25:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2f7c1a9b4d12"
down_revision = "8989f7e6d5e8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("vacancies", sa.Column("empresa", sa.String(length=100), nullable=True))
    op.add_column("vacancies", sa.Column("localidad", sa.String(length=100), nullable=True))
    op.add_column("vacancies", sa.Column("area", sa.String(length=100), nullable=True))
    op.add_column("vacancies", sa.Column("descriptivo_puesto", sa.Text(), nullable=True))
    op.add_column("vacancies", sa.Column("descriptivo_archivo_nombre", sa.String(length=255), nullable=True))
    op.add_column("vacancies", sa.Column("descriptivo_archivo_path", sa.String(length=500), nullable=True))
    op.add_column("vacancies", sa.Column("descriptivo_texto_extraido", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("vacancies", "descriptivo_texto_extraido")
    op.drop_column("vacancies", "descriptivo_archivo_path")
    op.drop_column("vacancies", "descriptivo_archivo_nombre")
    op.drop_column("vacancies", "descriptivo_puesto")
    op.drop_column("vacancies", "area")
    op.drop_column("vacancies", "localidad")
    op.drop_column("vacancies", "empresa")