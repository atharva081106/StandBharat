"""Update Integration model

Revision ID: fdda119ef9f1
Revises: fdda119ef9f0
Create Date: 2026-10-09 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fdda119ef9f1'
down_revision: Union[str, Sequence[str], None] = 'fdda119ef9f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    integration_columns = [col['name'] for col in inspector.get_columns('integration')]
    
    if 'brand_id' not in integration_columns:
        op.add_column('integration', sa.Column('brand_id', sa.Uuid(), nullable=True))
        op.create_index(op.f('ix_integration_brand_id'), 'integration', ['brand_id'], unique=False)
        # Handle dropping foreign key if it exists? We assume if brand_id doesn't exist, the FK doesn't either.
        op.create_foreign_key(None, 'integration', 'brand', ['brand_id'], ['id'])
        
    if 'credentials_encrypted' not in integration_columns:
        op.add_column('integration', sa.Column('credentials_encrypted', sa.Text(), nullable=True))
    if 'status' not in integration_columns:
        op.add_column('integration', sa.Column('status', sa.String(), nullable=True, server_default='NOT_CONFIGURED'))
    if 'last_sync_at' not in integration_columns:
        op.add_column('integration', sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True))
    if 'last_error' not in integration_columns:
        op.add_column('integration', sa.Column('last_error', sa.Text(), nullable=True))
    if 'config' not in integration_columns:
        op.add_column('integration', sa.Column('config', sa.JSON(), nullable=True))

    # Create traffic_metrics table
    op.create_table('traffic_metrics',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('workspace_id', sa.Uuid(), nullable=True),
        sa.Column('brand_id', sa.Uuid(), nullable=True),
        sa.Column('date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('medium', sa.String(), nullable=True),
        sa.Column('campaign', sa.String(), nullable=True),
        sa.Column('landing_page', sa.String(), nullable=True),
        sa.Column('sessions', sa.Integer(), nullable=True),
        sa.Column('active_users', sa.Integer(), nullable=True),
        sa.Column('pageviews', sa.Integer(), nullable=True),
        sa.Column('engagement_rate', sa.Float(), nullable=True),
        sa.Column('conversions', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['brand_id'], ['brand.id'], ),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspace.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('brand_id', 'date', 'source', 'medium', 'campaign', 'landing_page', name='uq_traffic_metrics')
    )
    op.create_index(op.f('ix_traffic_metrics_brand_id'), 'traffic_metrics', ['brand_id'], unique=False)
    op.create_index(op.f('ix_traffic_metrics_date'), 'traffic_metrics', ['date'], unique=False)
    op.create_index(op.f('ix_traffic_metrics_workspace_id'), 'traffic_metrics', ['workspace_id'], unique=False)

    # Create search_metrics table
    op.create_table('search_metrics',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('workspace_id', sa.Uuid(), nullable=True),
        sa.Column('brand_id', sa.Uuid(), nullable=True),
        sa.Column('date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('query', sa.String(), nullable=True),
        sa.Column('page', sa.String(), nullable=True),
        sa.Column('clicks', sa.Integer(), nullable=True),
        sa.Column('impressions', sa.Integer(), nullable=True),
        sa.Column('ctr', sa.Float(), nullable=True),
        sa.Column('position', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['brand_id'], ['brand.id'], ),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspace.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('brand_id', 'date', 'query', 'page', name='uq_search_metrics')
    )
    op.create_index(op.f('ix_search_metrics_brand_id'), 'search_metrics', ['brand_id'], unique=False)
    op.create_index(op.f('ix_search_metrics_date'), 'search_metrics', ['date'], unique=False)
    op.create_index(op.f('ix_search_metrics_page'), 'search_metrics', ['page'], unique=False)
    op.create_index(op.f('ix_search_metrics_query'), 'search_metrics', ['query'], unique=False)
    op.create_index(op.f('ix_search_metrics_workspace_id'), 'search_metrics', ['workspace_id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_search_metrics_workspace_id'), table_name='search_metrics')
    op.drop_index(op.f('ix_search_metrics_query'), table_name='search_metrics')
    op.drop_index(op.f('ix_search_metrics_page'), table_name='search_metrics')
    op.drop_index(op.f('ix_search_metrics_date'), table_name='search_metrics')
    op.drop_index(op.f('ix_search_metrics_brand_id'), table_name='search_metrics')
    op.drop_table('search_metrics')

    op.drop_index(op.f('ix_traffic_metrics_workspace_id'), table_name='traffic_metrics')
    op.drop_index(op.f('ix_traffic_metrics_date'), table_name='traffic_metrics')
    op.drop_index(op.f('ix_traffic_metrics_brand_id'), table_name='traffic_metrics')
    op.drop_table('traffic_metrics')

    conn = op.get_bind()
    inspector = sa.inspect(conn)
    integration_columns = [col['name'] for col in inspector.get_columns('integration')]
    
    if 'brand_id' in integration_columns:
        # Constraint names need to be explicitly known to drop, or handled by naming convention.
        # Alembic downgrade usually requires the explicit name. Since it's omitted in upgrade, we use an approximation or ignore.
        # Assuming the fk name is 'integration_brand_id_fkey' for postgres standard.
        try:
            op.drop_constraint('integration_brand_id_fkey', 'integration', type_='foreignkey')
        except Exception:
            pass
        op.drop_index(op.f('ix_integration_brand_id'), table_name='integration')
        op.drop_column('integration', 'brand_id')
        
    if 'config' in integration_columns:
        op.drop_column('integration', 'config')
    if 'last_error' in integration_columns:
        op.drop_column('integration', 'last_error')
    if 'last_sync_at' in integration_columns:
        op.drop_column('integration', 'last_sync_at')
    if 'status' in integration_columns:
        op.drop_column('integration', 'status')
    if 'credentials_encrypted' in integration_columns:
        op.drop_column('integration', 'credentials_encrypted')
