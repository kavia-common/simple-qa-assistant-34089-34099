# simple-qa-assistant-34089-34099

Backend (Django REST) provides:
- GET /api/health/ – health check
- POST /api/ask/ – submit a JSON body {"question": "Your question"} to receive an AI-generated answer

Environment variables (configure in your deployment environment or a .env file loaded by your process):
- OPENAI_API_KEY: Required. Your OpenAI API key.
- OPENAI_MODEL: Optional. Defaults to "gpt-4o-mini".
- OPENAI_API_BASE: Optional. Custom base URL if using a proxy/Azure-compatible endpoint.

Example request:
curl -X POST http://localhost:8000/api/ask/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the capital of France?"}'

Response:
{"answer": "Paris is the capital of France.", "model": "gpt-4o-mini", "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}}

Swagger/OpenAPI docs:
- Visit /docs/ on the running server (e.g., http://localhost:8000/docs/)
- JSON schema is available at /swagger.json