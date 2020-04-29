import jsonschema
from django.core.exceptions import ValidationError


def validate_utm(value):
    schema = {
        "type": "object",
        "properties": {
            "source": {"type": "string"},
            "campaign": {"type": "string"},
            "medium": {"type": "number"},
        },
        "additionalProperties": False
    }

    try:
        jsonschema.validate(value, schema)
    except jsonschema.ValidationError as e:
        raise ValidationError(e.message)
