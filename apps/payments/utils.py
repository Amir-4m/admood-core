import requests
from django.conf import settings


def payment_request(endpoint, method, data=None):
    headers = {
        "Authorization": f"TOKEN {settings.PAYMENT_SERVICE_SECRET}",
        "Content-Type": "application/json"
    }
    methods = {
        'get': requests.get,
        'post': requests.post
    }

    response = methods[method](f"{settings.PAYMENT_API_URL}{endpoint}/", headers=headers, json=data)
    response.raise_for_status()
    return response
