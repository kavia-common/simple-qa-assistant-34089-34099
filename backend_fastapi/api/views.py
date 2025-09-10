import os
from typing import Any, Dict, Optional

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .serializers import AskRequestSerializer, AskResponseSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    """
    Simple health check endpoint.

    Returns:
        200 OK with {"message": "Server is up!"}
    """
    return Response({"message": "Server is up!"})


# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def ask(request):
    """
    Handle question submission and return AI-generated answer.

    Summary:
        Submit a question and receive an AI-generated answer.

    Request:
        Content-Type: application/json
        Body:
            {
              "question": "Your question here"
            }

    Environment variables:
        - OPENAI_API_KEY: Your OpenAI API key. Must be configured in the environment.
        - OPENAI_MODEL (optional): The model to use (default: "gpt-4o-mini" if available).
        - OPENAI_API_BASE (optional): Custom base URL if using a proxy or Azure OpenAI compatible endpoint.

    Returns:
        - 200 OK: {"answer": "<text>", "model": "<model>", "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}}
        - 400 Bad Request: {"error": "<message>"} for validation errors.
        - 500 Internal Server Error: {"error": "<message>"} when provider fails.

    Notes:
        - Configure environment variables in the deployment environment (.env). Do not hardcode secrets.
        - For local development, create a .env file at project root and ensure your process loads it.
    """
    # Validate input body
    serializer = AskRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    question = serializer.validated_data["question"].strip()
    if not question:
        return Response({"error": "Question must not be empty."}, status=status.HTTP_400_BAD_REQUEST)

    # Read environment variables (do not hardcode)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return Response(
            {"error": "Missing OPENAI_API_KEY environment variable."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    api_base = os.getenv("OPENAI_API_BASE")  # Optional override

    # Defer importing openai client to allow the server to start without the package when not used
    try:
        # Official OpenAI Python SDK (>=1.0)
        from openai import OpenAI  # type: ignore
        client = OpenAI(api_key=api_key, base_url=api_base) if api_base else OpenAI(api_key=api_key)
        # Use the newer responses API if available
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": question},
                ],
                temperature=0.2,
            )
            answer_text = (resp.choices[0].message.content or "").strip()
            usage = getattr(resp, "usage", None)
            usage_dict: Optional[Dict[str, Any]] = None
            if usage:
                # Normalize usage fields if present
                usage_dict = {
                    "input_tokens": getattr(usage, "prompt_tokens", None) or getattr(usage, "input_tokens", None) or 0,
                    "output_tokens": getattr(usage, "completion_tokens", None) or getattr(usage, "output_tokens", None) or 0,
                    "total_tokens": getattr(usage, "total_tokens", None) or 0,
                }
        except Exception:
            # Fallback to legacy completions if needed or SDK variant differences
            completion = client.completions.create(
                model=model,
                prompt=question,
                temperature=0.2,
            )
            answer_text = (completion.choices[0].text or "").strip()
            usage = getattr(completion, "usage", None)
            usage_dict = {
                "input_tokens": getattr(usage, "prompt_tokens", 0) if usage else 0,
                "output_tokens": getattr(usage, "completion_tokens", 0) if usage else 0,
                "total_tokens": getattr(usage, "total_tokens", 0) if usage else 0,
            }

    except ImportError:
        # If openai package isn't installed, return a helpful message
        return Response(
            {
                "error": "OpenAI SDK not installed. Please add 'openai' to requirements and install dependencies.",
                "hint": "pip install openai"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        return Response(
            {"error": f"Provider error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Validate and return standardized response
    out = {"answer": answer_text, "model": model}
    if usage_dict:
        out["usage"] = usage_dict

    response_serializer = AskResponseSerializer(data=out)
    response_serializer.is_valid(raise_exception=False)
    return Response(response_serializer.data, status=status.HTTP_200_OK)
