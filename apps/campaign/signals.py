import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.campaign.models import Campaign
from apps.core.consts import CostModel
from apps.medium.models import Publisher
from apps.payments.models import Transaction


logger = logging.getLogger(__name__)


@receiver(post_save, sender=Campaign)
def create_transaction(sender, instance, created, **kwargs):
    logger.debug(
        f'[create transaction signal received]-[campaign id: {instance.id}]-[created: {created}]'
        f'-[previous status: {instance._b_status}]-[current status: {instance.status}]'
    )

    trans_type = None

    # if status changed
    if instance._b_status != instance.status:
        # if changed to waiting or approved
        if instance.status in (Campaign.STATUS_WAITING, Campaign.STATUS_APPROVED):
            trans_type = Transaction.TYPE_DEDUCT
        # if changed to rejected
        if instance.status == Campaign.STATUS_REJECTED:
            trans_type = Transaction.TYPE_REFUND

    # when duplicate a campaign, create a deduct transaction
    if created and instance.status in (Campaign.STATUS_WAITING, Campaign.STATUS_APPROVED):
        trans_type = Transaction.TYPE_DEDUCT

    if trans_type:
        Transaction.objects.create(user=instance.owner,
                                   value=-instance.total_budget,
                                   transaction_type=trans_type,
                                   campaign=instance,
                                   )

    # Updating Final Publisher field
    if instance._b_status == Campaign.STATUS_DRAFT and instance.status == Campaign.STATUS_WAITING:
        instance.update_final_publishers()
