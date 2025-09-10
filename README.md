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

Proxy configuration notes:
- Do NOT pass a 'proxies' parameter to the OpenAI SDK client; it is not supported and will cause: "Unsupported client parameter 'proxies'".
- If you need a proxy, set standard environment variables handled by the HTTP stack:
  - HTTP_PROXY and/or HTTPS_PROXY (e.g., HTTPS_PROXY=http://user:pass@host:port)
- If using a custom gateway or Azure-compatible endpoint, set:
  - OPENAI_API_BASE to your custom base URL (e.g., https://your-proxy.example.com/v1)
- The backend only initializes OpenAI with allowed parameters: api_key and optional base_url. No proxy kwargs are used.

Swagger/OpenAPI docs:
- Visit /docs/ on the running server (e.g., http://localhost:8000/docs/)
- JSON schema is available at /swagger.json