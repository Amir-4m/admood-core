import jsonschema
from django.core.exceptions import ValidationError

from apps.medium.consts import Medium


def validate_campaign_utm(value):
    schema = {
        "type": "object",
        "properties": {
            "source": {"type": "string"},
            "campaign": {"type": "string"},
            "medium": {
                "type": "number",
                "enum": [i for i, _ in Medium.MEDIUM_CHOICES]
            },
        },
        "additionalProperties": False
    }

    try:
        jsonschema.validate(value, schema)
    except jsonschema.ValidationError as e:
        raise ValidationError(e.message)
