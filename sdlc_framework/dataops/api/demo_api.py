"""Demo script to test the DataOps REST API.

This script demonstrates:
1. Starting the FastAPI server
2. Testing endpoints with sample requests
3. Viewing OpenAPI documentation

Usage:
    python -m sdlc_framework.dataops.api.demo_api
"""

import asyncio
import json

print("=" * 70)
print("DataOps REST API Demo")
print("=" * 70)

print("""
To start the API server, run:

    uvicorn sdlc_framework.dataops.api.app:app --reload --port 8000

Then access:
    • API Documentation (Swagger UI): http://localhost:8000/docs
    • Alternative Docs (ReDoc): http://localhost:8000/redoc
    • OpenAPI Schema: http://localhost:8000/openapi.json
    • Health Check: http://localhost:8000/health

Example API Requests:
───────────────────────────────────────────────────────────────────────

1. Health Check (no auth required):
   curl http://localhost:8000/health

2. List Templates (requires auth):
   curl -H "Authorization: Bearer demo-token" \\
        http://localhost:8000/v1/dataops/templates

3. Get Template by ID:
   curl -H "Authorization: Bearer demo-token" \\
        http://localhost:8000/v1/dataops/templates/{template_id}

4. Filter Templates by Industry:
   curl -H "Authorization: Bearer demo-token" \\
        "http://localhost:8000/v1/dataops/templates?industry=fintech"

5. Get Template Recommendations:
   curl -X POST http://localhost:8000/v1/dataops/templates/recommend \\
        -H "Authorization: Bearer demo-token" \\
        -H "Content-Type: application/json" \\
        -d '{
          "client_metadata": {
            "industry": "fintech",
            "use_case": "developer_productivity",
            "company_size": "mid_market"
          },
          "dataset_types": ["confluence_pages", "github_repos"],
          "stage": "sandbox"
        }'

6. List Datasets (requires auth):
   curl -H "Authorization: Bearer demo-token" \\
        http://localhost:8000/v1/dataops/datasets

7. Filter Datasets by Client and Stage:
   curl -H "Authorization: Bearer demo-token" \\
        "http://localhost:8000/v1/dataops/datasets?client_id={uuid}&stage=sandbox"

───────────────────────────────────────────────────────────────────────

API Features:
✅ RESTful endpoints for datasets and templates
✅ OAuth 2.0 Bearer token authentication
✅ Query parameter filtering and pagination
✅ Pydantic schema validation
✅ Auto-generated OpenAPI documentation
✅ HATEOAS links in responses
✅ RFC 7807 error responses
✅ CORS middleware

""")

print("=" * 70)
