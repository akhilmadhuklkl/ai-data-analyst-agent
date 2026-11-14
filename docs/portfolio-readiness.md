# Portfolio readiness review

## Current strengths

- A working Next.js + FastAPI interface with CSV and SQLite flows.
- Streamlit `app.py` retained as a backup interface.
- Local Ollama support with a deterministic fallback.
- Read-only SQL validation, row limits, shared error types, and safe logging boundaries.
- Sample data, sample database, guided questions, visual summaries, exports, and responsive layout.
- 55 Python tests, Ruff checks, frontend type-checking, production build, and GitHub Actions CI.

## Remaining gaps before deployment

1. Add a production deployment configuration for the API and frontend.
2. Move the API URL to deployment environment variables and remove local-only defaults.
3. Add upload size limits and stricter file-type validation at the API boundary.
4. Add authentication and rate limiting if the service becomes public.
5. Add browser-level tests for file upload, sample loading, analysis, and exports.
6. Add a deployment smoke test and health-check monitoring.
7. Document Ollama installation, model download, and CPU/memory expectations.

## Recommended deployment order

1. Finish browser-level testing and API boundary hardening.
2. Containerize the FastAPI service and frontend build.
3. Deploy the frontend and API separately with environment-based configuration.
4. Run smoke tests against the deployed health and analysis endpoints.
5. Add authentication and observability before sharing the public URL widely.

## Definition of portfolio-ready

The project is portfolio-ready for source-code review and local demonstration now. Deployment-ready means the deployment configuration, public-environment security controls, browser tests, and smoke checks above are complete.
