# apps/accounts/migrations/0002_create_groups.py
from django.db import migrations

def create_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    # Cria grupos
    admin_group, _ = Group.objects.get_or_create(name="Admin")
    manager_group, _ = Group.objects.get_or_create(name="Manager")
    seller_group, _ = Group.objects.get_or_create(name="Seller")

    # Permissões disponíveis
    all_permissions = Permission.objects.all()

    # Admin → todas permissões
    admin_group.permissions.set(all_permissions)

    # Manager → pode ver relatórios e gerenciar vendas
    manager_perms = all_permissions.filter(
        codename__in=[
            "view_dailysales", "change_dailysales",
            "view_account", "change_account"
        ]
    )
    manager_group.permissions.set(manager_perms)

    # Seller → só pode lançar e ver vendas
    seller_perms = all_permissions.filter(
        codename__in=[
            "add_dailysales", "view_dailysales"
        ]
    )
    seller_group.permissions.set(seller_perms)

def remove_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=["Admin", "Manager", "Seller"]).delete()

class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),  # depende da migração inicial
    ]

    operations = [
        migrations.RunPython(create_groups, remove_groups),
    ]
