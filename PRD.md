# Product Requirements Document (PRD)

**Problem Statement ID:** 26027
**Title:** AI-Powered Automatic Block Planning to Maximize Asset Availability for Train Operations on Indian Railways
**Status:** Draft v1.0

---

## 1. Project Overview

**Objective:** Transform the current decentralized and manual block planning system into a data-driven, coordinated process. The system integrates data from multiple legacy systems to generate optimized, conflict-free maintenance schedules that maximize infrastructure uptime and support reliable train operations.

---

## 2. Target Audience & Users

| User Group | Value Delivered |
|---|---|
| Railway Division Controllers & Planners | Eliminates manual scheduling conflicts and reduces the administrative burden of coordinating blocks across multiple departments. |
| Maintenance Crews (Track, OHE, Signal) | Receive predictable, consolidated "mega-blocks" and guaranteed safe working windows without train interruptions. |
| Train Operations & Passengers | Benefit from higher network throughput (more train paths) and fewer unscheduled halts. |

---

## 3. Core System Functions

### Data Integration (Collect)
Utilize automated ETL pipelines to ingest maintenance defects, overdue tasks, and block requests from Engineering, S&T (Signal & Telecommunication), and TRD (Traction Distribution). Requires integrating TMS, SMMS, TDMS, BDMS, and COA systems.

### AI-Driven Prioritization (Prioritize)
Implement machine learning models to score and prioritize tasks based on safety risk, criticality, and urgency.

### Constraint Optimization (Check & Optimize)
Deploy a mathematical solver to check task compatibility, available resources, and corridor availability against train operations, merging compatible tasks into highly efficient maintenance blocks.

### Explainable Recommendations (Recommend)
Provide a dashboard that generates transparent block plans over weekly and monthly horizons for authorized personnel to review and approve, ensuring a human-in-the-loop safety net.

---

## 4. Technical Architecture

The system utilizes a modular, software-first approach designed for high availability and easy scalability.

| Layer | Technology | Purpose |
|---|---|---|
| Database | PostgreSQL | Relational storage for structured legacy data and normalized data ingestion pipelines. |
| Backend API | Python (FastAPI / Django) | Robust API services to handle data routing, engine triggers, and real-time conflict polling. |
| AI/ML Layer | Python (Scikit-learn) | Calculates maintenance priority scores based on defect severity data. |
| Optimization Engine | Google OR-Tools (CP-SAT) | Constraint programming solver to handle complex mathematical scheduling and enforce hard safety constraints. |
| Frontend UI | React.js / TypeScript | Interactive scheduling dashboards to visualize block plans and facilitate human approval. |
| Deployment | Docker | Containerized deployment for reliable, scalable operations. |

---

## 5. VS Code Implementation Strategy

### Phase 1 — Database & API Scaffolding

- **Initialize the Backend:** Create a new Python virtual environment and set up a FastAPI or Django project.
- **Define the Schema (PostgreSQL):** Create normalized tables to act as the single source of truth:
  - `tms_defects` — Track conditions, coordinates, and severity.
  - `smms_failures` — Signal statuses and overdue maintenance tasks.
  - `tdms_equipment` — Overhead equipment status and power block requirements.
  - `train_schedule` — Timetables and goods train forecasts from the Control Office.

### Phase 2 — The AI Prioritization Engine

- **Generate Simulated Datasets:** Create mock datasets representing track defects, signal failures, and equipment logs to simulate the legacy TMS, SMMS, and TDMS systems.
- **Train the Scikit-Learn Model:** Build a Python module to train a regression model. The model must evaluate defect severity, age, and location, outputting a numerical Priority Score (w_i) for each requested task.

### Phase 3 — The CP-SAT Optimization Solver (The Core)

This module requires strict algorithmic logic, making it ideal for step-by-step development in VS Code.

- **Define Variables:** For each task `i`, use `cp_model.CpModel()` to define start times, end times, and execution intervals.
- **Apply Hard Safety Constraints:**
  - **No Overrides:** Implement `AddNoOverlap` constraints to ensure maintenance blocks strictly avoid active train operation windows.
  - **Departmental Coordination:** Merge tasks. For example, if a signal repair (SMMS) requires power isolation (TDMS), enforce a constraint that the TDMS block completely encapsulates the SMMS task window.
- **Define the Objective:** Instruct the solver to maximize the sum of Priority Scores (w_i) for completed tasks while minimizing total infrastructure downtime.

### Phase 4 — Frontend Dashboard & Human-in-the-Loop

- **Scaffold React App:** Set up a React project using TypeScript to build the interactive scheduling dashboards.
- **Build Core Views:**
  - **Unified View:** A dashboard showing real-time ingestion from all legacy systems.
  - **Interactive Timeline:** A Gantt chart visualizing the OR-Tools solver's recommended "mega-blocks" against the regular train timetable.
  - **Approval Workflow:** An interface where authorized controllers can review the explainable AI recommendations and approve the block, fulfilling the critical human-in-the-loop requirement.