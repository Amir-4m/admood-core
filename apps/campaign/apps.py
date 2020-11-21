from django.apps import AppConfig


class CampaignConfig(AppConfig):
    name = 'apps.campaign'

    def ready(self):
        import apps.campaign.signals