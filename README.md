# NexusRail

NexusRail is a PostgreSQL-first railway maintenance planning platform designed to coordinate engineering, signaling, and traction data into safer and more efficient maintenance windows.

## Development roadmap

The project is organized around the following four phases:

1. Phase 1 — Database & API Foundation — COMPLETED
   - PostgreSQL schema and API scaffolding for the core legacy-system ingestion tables.
   - FastAPI application structure and validation against the live Docker PostgreSQL instance.

2. Phase 2 — Simulated Data & AI Prioritization — UPCOMING
   - Synthetic legacy-system datasets and ML-driven priority scoring.

3. Phase 3 — CP-SAT Optimization Engine — UPCOMING
   - Conflict-aware maintenance scheduling and block optimization with OR-Tools CP-SAT.

4. Phase 4 — Dashboard & Human-in-the-Loop — UPCOMING
   - Interactive scheduling dashboard with operational review and approval workflows.

## Current status

This repository currently reflects the completed Phase 1 implementation and validation work for the database and API foundation.

## Local development

- PostgreSQL is expected to run as a Docker container using Docker Compose.
- The runtime configuration uses a PostgreSQL connection string in `.env`.
- `.env.example` documents the required format without exposing credentials.

## Safety note

This repository is intentionally configured to avoid committing secrets, local environment files, or generated artifacts.
