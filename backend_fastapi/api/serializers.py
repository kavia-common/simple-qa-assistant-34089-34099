from rest_framework import serializers


class AskRequestSerializer(serializers.Serializer):
    """
    Serializer to validate incoming POST body for /ask endpoint.
    """
    question = serializers.CharField(
        required=True,
        allow_blank=False,
        help_text="User's question to be sent to the AI model."
    )


class AskResponseSerializer(serializers.Serializer):
    """
    Serializer for the standardized response from /ask endpoint.
    """
    answer = serializers.CharField(help_text="AI-generated answer text.")
    model = serializers.CharField(help_text="Model used to generate the answer.")
    usage = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Token usage information as returned by the provider.",
        required=False
    )
