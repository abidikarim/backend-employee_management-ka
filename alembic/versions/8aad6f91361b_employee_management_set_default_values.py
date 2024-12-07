"""Employee Management set default values 

Revision ID: 8aad6f91361b
Revises: f506aea6d487
Create Date: 2024-10-24 20:02:48.303642

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8aad6f91361b"
down_revision: Union[str, None] = "f506aea6d487"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("employees", "account_status", server_default="Inactive")
    op.alter_column("accounts_activation", "status", server_default="Pending")
    op.alter_column("reset_passwords", "status", server_default="Pending")


def downgrade() -> None:
    op.alter_column("employees", "account_status", server_default=None)
    op.alter_column("accounts_activation", "status", server_default=None)
    op.alter_column("reset_passwords", "status", server_default=None)
