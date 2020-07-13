import re

from django.core.exceptions import ValidationError


def national_id_validator(value):
    if not re.search(r'^\d{10}$', value):
        raise ValidationError(message='{identifier_code} is not valid'.format(identifier_code=value))

    check = int(value[9])
    s = sum([int(value[x]) * (10 - x) for x in range(9)]) % 11
    if (2 > s == check) or (s >= 2 and check + s == 11):
        return True
    else:
        raise ValidationError(message='{identifier_code} is not valid'.format(identifier_code=value))
