class ServiceProvider:
    MTN = 1
    MCI = 2
    RTL = 3

    SERVICE_PROVIDER_CHOICES = (
        (MTN, "MTN"),
        (MCI, "MCI"),
        (RTL, "RTL"),
    )

    @classmethod
    def to_dict(cls):
        return [{'id': provider[0], 'title': provider[1]} for provider in cls.SERVICE_PROVIDER_CHOICES]
