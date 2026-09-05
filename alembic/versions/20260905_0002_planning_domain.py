"""Add the normalized railway planning domain."""

from alembic import op

from app.models.base import Base
from app.models import planning

revision = "20260905_0002"
down_revision = "20260830_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    tables = [
        planning.RailwayZone.__table__,
        planning.RailwayDivision.__table__,
        planning.RailwayCorridor.__table__,
        planning.RailwaySection.__table__,
        planning.RailwayAsset.__table__,
        planning.MaintenanceRequest.__table__,
        planning.BlockRequest.__table__,
        planning.Train.__table__,
        planning.TrainMovement.__table__,
        planning.OptimizationRun.__table__,
        planning.Recommendation.__table__,
        planning.Approval.__table__,
        planning.Conflict.__table__,
        planning.recommendation_requests,
    ]
    Base.metadata.create_all(bind=op.get_bind(), tables=tables)


def downgrade() -> None:
    for table in [
        planning.recommendation_requests,
        planning.Conflict.__table__,
        planning.Approval.__table__,
        planning.Recommendation.__table__,
        planning.OptimizationRun.__table__,
        planning.TrainMovement.__table__,
        planning.Train.__table__,
        planning.BlockRequest.__table__,
        planning.MaintenanceRequest.__table__,
        planning.RailwayAsset.__table__,
        planning.RailwaySection.__table__,
        planning.RailwayCorridor.__table__,
        planning.RailwayDivision.__table__,
        planning.RailwayZone.__table__,
    ]:
        table.drop(op.get_bind(), checkfirst=True)
