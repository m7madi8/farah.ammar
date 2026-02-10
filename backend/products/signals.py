"""
Signals to update InventoryLog when product stock changes.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Product, InventoryLog


@receiver(post_save, sender=Product)
def product_stock_changed(sender, instance, created, update_fields, **kwargs):
    """
    When stock_quantity changes (create or update), log the change.
    We only have current state in post_save; for 'adjustment' we use quantity_after = current.
    For new products we don't log initial 0; for updates we need previous value.
    """
    if created:
        # Optionally log initial stock if > 0
        if instance.stock_quantity != 0:
            InventoryLog.objects.create(
                product=instance,
                change_qty=instance.stock_quantity,
                quantity_after=instance.stock_quantity,
                reason='restock',
                reference_type='initial',
                notes='Initial stock',
            )
        return
    if update_fields is not None and 'stock_quantity' not in update_fields:
        return
    # For updates we'd need previous value; post_save doesn't have it. So we only
    # log on explicit stock change from code that calls update() with stock_quantity,
    # or from order fulfillment. To avoid duplicate logs, we don't auto-log every save.
    # Instead: log from orders app when deducting stock (sale), and from admin/API when
    # doing restock/adjustment. So we leave this signal to only handle initial stock.
    # If you want to log every change, use pre_save to store old stock and then in
    # post_save create log with change_qty = new - old.
    pass


def log_stock_change(product, change_qty, reason, reference_type=None, reference_id=None, notes='', user=None):
    """
    Helper to create an inventory log and optionally update product stock.
    Call this from orders (sale) or from API (restock/adjustment).
    """
    new_qty = product.stock_quantity + change_qty
    if new_qty < 0 and not product.allow_backorder:
        raise ValueError('Insufficient stock.')
    product.stock_quantity = new_qty
    product.save(update_fields=['stock_quantity', 'updated_at'])
    InventoryLog.objects.create(
        product=product,
        change_qty=change_qty,
        quantity_after=new_qty,
        reason=reason,
        reference_type=reference_type or '',
        reference_id=reference_id,
        notes=notes,
        created_by=user,
    )
