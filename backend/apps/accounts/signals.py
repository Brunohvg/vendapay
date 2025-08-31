# apps/accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import Account

@receiver(post_save, sender=Account)
def set_user_group(sender, instance, created, **kwargs):
    """
    Sempre que um usuário for criado, adiciona ele ao grupo correto
    baseado no user_type.
    """
    # Garante que os grupos existam
    for group_name in ['Admin', 'Seller', 'Manager']:
        Group.objects.get_or_create(name=group_name)

    # Limpa grupos atuais
    instance.groups.clear()

    # Mapeia o grupo certo
    if instance.user_type == Account.UserType.ADMIN:
        group = Group.objects.get(name='Admin')
    elif instance.user_type == Account.UserType.MANAGER:
        group = Group.objects.get(name='Manager')
    else:
        group = Group.objects.get(name='Seller')

    instance.groups.add(group)
