"""Initial Phase 1 schema

Revision ID: 20260830_0001
Revises: 
Create Date: 2026-08-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260830_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tms_defects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_system", sa.String(length=50), nullable=False, server_default="TMS"),
        sa.Column("railway_zone", sa.String(length=50), nullable=True),
        sa.Column("division", sa.String(length=100), nullable=True),
        sa.Column("section_code", sa.String(length=50), nullable=True),
        sa.Column("route_code", sa.String(length=50), nullable=True),
        sa.Column("track_id", sa.String(length=100), nullable=True),
        sa.Column("km_post", sa.Numeric(precision=10, scale=3), nullable=True),
        sa.Column("latitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("longitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("defect_type", sa.String(length=100), nullable=True),
        sa.Column("defect_description", sa.Text(), nullable=True),
        sa.Column("severity", sa.String(length=30), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("is_critical", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        sa.Column("priority_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("reported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("estimated_repair_hours", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tms_defects_id"), "tms_defects", ["id"], unique=False)
    op.create_index(op.f("ix_tms_defects_section_code"), "tms_defects", ["section_code"], unique=False)
    op.create_index(op.f("ix_tms_defects_route_code"), "tms_defects", ["route_code"], unique=False)

    op.create_table(
        "smms_failures",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_system", sa.String(length=50), nullable=False, server_default="SMMS"),
        sa.Column("railway_zone", sa.String(length=50), nullable=True),
        sa.Column("division", sa.String(length=100), nullable=True),
        sa.Column("section_code", sa.String(length=50), nullable=True),
        sa.Column("route_code", sa.String(length=50), nullable=True),
        sa.Column("signal_id", sa.String(length=100), nullable=True),
        sa.Column("equipment_id", sa.String(length=100), nullable=True),
        sa.Column("failure_type", sa.String(length=100), nullable=True),
        sa.Column("failure_description", sa.Text(), nullable=True),
        sa.Column("severity", sa.String(length=30), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("overdue_hours", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("failure_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("requires_power_isolation", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        sa.Column("related_block_request_id", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_smms_failures_id"), "smms_failures", ["id"], unique=False)
    op.create_index(op.f("ix_smms_failures_section_code"), "smms_failures", ["section_code"], unique=False)
    op.create_index(op.f("ix_smms_failures_route_code"), "smms_failures", ["route_code"], unique=False)

    op.create_table(
        "tdms_equipment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_system", sa.String(length=50), nullable=False, server_default="TDMS"),
        sa.Column("railway_zone", sa.String(length=50), nullable=True),
        sa.Column("division", sa.String(length=100), nullable=True),
        sa.Column("section_code", sa.String(length=50), nullable=True),
        sa.Column("route_code", sa.String(length=50), nullable=True),
        sa.Column("equipment_id", sa.String(length=100), nullable=True),
        sa.Column("equipment_type", sa.String(length=100), nullable=True),
        sa.Column("substation_id", sa.String(length=100), nullable=True),
        sa.Column("health_status", sa.String(length=30), nullable=True),
        sa.Column("power_block_required", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        sa.Column("isolation_window_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("isolation_window_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_maintenance_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("criticality_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("equipment_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tdms_equipment_id"), "tdms_equipment", ["id"], unique=False)
    op.create_index(op.f("ix_tdms_equipment_section_code"), "tdms_equipment", ["section_code"], unique=False)
    op.create_index(op.f("ix_tdms_equipment_route_code"), "tdms_equipment", ["route_code"], unique=False)

    op.create_table(
        "train_schedule",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_system", sa.String(length=50), nullable=False, server_default="COA"),
        sa.Column("railway_zone", sa.String(length=50), nullable=True),
        sa.Column("division", sa.String(length=100), nullable=True),
        sa.Column("section_code", sa.String(length=50), nullable=True),
        sa.Column("route_code", sa.String(length=50), nullable=True),
        sa.Column("train_no", sa.String(length=50), nullable=True),
        sa.Column("service_type", sa.String(length=30), nullable=True),
        sa.Column("scheduled_date", sa.Date(), nullable=True),
        sa.Column("origin_station", sa.String(length=100), nullable=True),
        sa.Column("destination_station", sa.String(length=100), nullable=True),
        sa.Column("direction", sa.String(length=20), nullable=True),
        sa.Column("arrival_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("departure_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_goods", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("last_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_train_schedule_id"), "train_schedule", ["id"], unique=False)
    op.create_index(op.f("ix_train_schedule_section_code"), "train_schedule", ["section_code"], unique=False)
    op.create_index(op.f("ix_train_schedule_route_code"), "train_schedule", ["route_code"], unique=False)
    op.create_index(op.f("ix_train_schedule_train_no"), "train_schedule", ["train_no"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_train_schedule_train_no"), table_name="train_schedule")
    op.drop_index(op.f("ix_train_schedule_route_code"), table_name="train_schedule")
    op.drop_index(op.f("ix_train_schedule_section_code"), table_name="train_schedule")
    op.drop_index(op.f("ix_train_schedule_id"), table_name="train_schedule")
    op.drop_table("train_schedule")

    op.drop_index(op.f("ix_tdms_equipment_route_code"), table_name="tdms_equipment")
    op.drop_index(op.f("ix_tdms_equipment_section_code"), table_name="tdms_equipment")
    op.drop_index(op.f("ix_tdms_equipment_id"), table_name="tdms_equipment")
    op.drop_table("tdms_equipment")

    op.drop_index(op.f("ix_smms_failures_route_code"), table_name="smms_failures")
    op.drop_index(op.f("ix_smms_failures_section_code"), table_name="smms_failures")
    op.drop_index(op.f("ix_smms_failures_id"), table_name="smms_failures")
    op.drop_table("smms_failures")

    op.drop_index(op.f("ix_tms_defects_route_code"), table_name="tms_defects")
    op.drop_index(op.f("ix_tms_defects_section_code"), table_name="tms_defects")
    op.drop_index(op.f("ix_tms_defects_id"), table_name="tms_defects")
    op.drop_table("tms_defects")
