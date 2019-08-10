#######################
from __future__ import print_function, unicode_literals

#######################
"""
Handlers for various signals in the IT Management application.

This module is imported by models.py, so signal handlers get registered
at runtime.
"""

################################################################


def ipaddress_fk_pre_save(sender, instance, raw, **kwargs):
    """
    Update IP usage when an object with an IPAddress ForeignKey is saved.

    This signal handler can be registered for any model which
    has an IPAddress ForeignKey field named 'ip_address'.
    """
    if raw:
        return  # do not change other fields in this case.

    if instance.pk:
        # fetch old instance to look for a change
        old_instance = sender.objects.get(pk=instance.pk)
        if old_instance.ip_address != instance.ip_address:
            if old_instance.ip_address:
                old_instance.ip_address.in_use = False
                old_instance.ip_address.save()

    if instance.ip_address and not instance.ip_address.in_use:
        instance.ip_address.in_use = True
        instance.ip_address.save()


################################################################


def ipaddress_fk_pre_delete(sender, instance, **kwargs):
    """
    Update IP usage when an object with an IPAddress ForeignKey is deleted.

    This signal handler can be registered for any model which
    has an IPAddress ForeignKey field named 'ip_address'.
    """
    if instance.ip_address:
        instance.ip_address.in_use = False
        instance.ip_address.save()
    instance.ip_address = None


################################################################


def computer_asset_sync_post_save(sender, instance, created, raw, **kwargs):
    """
    Synchronize updates between Computer records and a corresponding
    Asset record.
    
    This signal handler should only be registered for Computer objects.
    """
    if raw:
        return
    if instance.asset is None:
        return

    save = False
    if instance.asset.person != instance.person:
        instance.asset.person = instance.person
        save = True
    if instance.asset.room != instance.room:
        instance.asset.room = instance.room
        save = True
    if save:
        instance.asset.save()


################################################################


def asset_computer_sync_post_save(sender, instance, created, raw, **kwargs):
    """
    Synchronize updates between Asset records and a corresponding
    Computer record.
    
    This signal handler should only be registered for Asset objects.
    """
    if raw:
        return
    if not instance.pk:
        # we will not be able to find the corresponding computer in this case
        # should log/alert about this, maybe?
        print("asset_computer_sync_post_save(): No instance pk / doing nothing.")
        return

    related_computer_list = instance.computer_set.all()
    if related_computer_list.count() != 1:
        return

    computer = related_computer_list.get()
    save = False
    if computer.person != instance.person:
        computer.person = instance.person
        save = True
    if computer.room != instance.room:
        computer.room = instance.room
        save = True
    if save:
        computer.save()


################################################################


def create_api_key(sender, instance, created, raw, **kwargs):
    """
    A signal for hooking up automatic ``ComputerKey`` creation.
    
    Register with:
    models.signals.post_save.connect(handlers.create_api_key, sender=Computer)
    """
    if raw:
        return
    if kwargs.get("created") is True:
        from .models import ComputerKey

        ComputerKey.objects.create(computer=kwargs.get("instance"))


################################################################
