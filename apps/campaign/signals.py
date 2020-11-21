from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.campaign.models import Campaign
from apps.payments.models import Transaction


@receiver(post_save, sender=Campaign)
def create_transaction(sender, instance, created, **kwargs):
    if created:
        # when duplicate a campaign create a deduct transaction
        if instance.status == Campaign.STATUS_APPROVED:
            Transaction.objects.create(user=instance.owner,
                                       value=-instance.total_budget,
                                       transaction_type=Transaction.TYPE_DEDUCT,
                                       campaign=instance,
                                       )
    else:
        # when users ask to approve a campaign create a deduct transaction
        if instance._b_status == Campaign.STATUS_DRAFT and instance.status == Campaign.STATUS_WAITING:
            Transaction.objects.create(user=instance.owner,
                                       value=-instance.total_budget,
                                       transaction_type=Transaction.TYPE_DEDUCT,
                                       campaign=instance,
                                       )
        # when a campaign rejected create a refund transaction
        if instance._b_status == Campaign.STATUS_WAITING and instance.status == Campaign.STATUS_REJECTED:
            Transaction.objects.create(user=instance.owner,
                                       value=instance.total_budget,
                                       transaction_type=Transaction.TYPE_REFUND,
                                       campaign=instance,
                                       )
        # when a rejected campaign change to waiting or approve create a deduct transaction
        elif instance._b_status == Campaign.STATUS_REJECTED and instance.status in [Campaign.STATUS_WAITING,
                                                                                    Campaign.STATUS_APPROVED]:
            Transaction.objects.create(user=instance.owner,
                                       value=-instance.total_budget,
                                       transaction_type=Transaction.TYPE_DEDUCT,
                                       campaign=instance,
                                       )
