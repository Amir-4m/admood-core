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

    if created:
        # when duplicate a campaign, create a deduct transaction
        if instance.status == Campaign.STATUS_APPROVED:
            Transaction.objects.create(user=instance.owner,
                                       value=-instance.total_budget,
                                       transaction_type=Transaction.TYPE_DEDUCT,
                                       campaign=instance,
                                       )
    else:
        # when users ask to approve a campaign, create a deduct transaction
        if instance._b_status == Campaign.STATUS_DRAFT and instance.status == Campaign.STATUS_WAITING:
            Transaction.objects.create(user=instance.owner,
                                       value=-instance.total_budget,
                                       transaction_type=Transaction.TYPE_DEDUCT,
                                       campaign=instance,
                                       )
        # when a campaign rejected, create a refund transaction
        if instance._b_status == Campaign.STATUS_WAITING and instance.status == Campaign.STATUS_REJECTED:
            Transaction.objects.create(user=instance.owner,
                                       value=instance.total_budget,
                                       transaction_type=Transaction.TYPE_REFUND,
                                       campaign=instance,
                                       )
        # when a rejected campaign change to waiting or approved status, create a deduct transaction
        elif instance._b_status == Campaign.STATUS_REJECTED and instance.status in [Campaign.STATUS_WAITING,
                                                                                    Campaign.STATUS_APPROVED]:
            Transaction.objects.create(user=instance.owner,
                                       value=-instance.total_budget,
                                       transaction_type=Transaction.TYPE_DEDUCT,
                                       campaign=instance,
                                       )
    # Updating Final Publisher field
    if instance._b_status == Campaign.STATUS_DRAFT and instance.status == Campaign.STATUS_WAITING:
        # TODO Implement This
        # publishers_by_categories_ids = Publisher.get_by_categories(
        #     categories=instance.categories.all()
        # ).values_list('id', flat=True)
        # print(publishers_by_categories_ids)
        # current_publisher_ids = instance.publisher_price.all().values_list('publisher_id')
        # inserting_publisher = set(current_publisher_ids) - set(publishers_by_categories_ids)
        #
        # for publisher in Publisher.objects.filter(id__in=inserting_publisher):
        #     try:
        #         price = publisher.cost_models.filter(
        #                 cost_model=CostModel.CPV
        #             ).order_by('-publisher_price').first().publisher_price
        #     except:
        #         price = 0
        #     instance.publisher_price.create(
        #         publisher=publisher,
        #         publisher_price=price
        #     )
        #
        # current_publisher_ids = instance.publisher_price.all().values_list('publisher_id')
        # deleting_publisher_ids = set(publishers_by_categories_ids) - set(current_publisher_ids)
        # instance.publisher_price.filter(publisher_id__in=deleting_publisher_ids).delete()

        instance.finalpublisher_set.all().delete()

        publishers_by_categories = Publisher.get_by_categories(
            categories=instance.categories.all()
        )
        for publisher in publishers_by_categories:
            try:
                price = publisher.cost_models.filter(
                        cost_model=CostModel.CPV
                    ).order_by('-publisher_price').first().publisher_price
            except:
                price = 0
            instance.finalpublisher_set.create(publisher=publisher, tariff=price)

