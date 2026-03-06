from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


DEFAULT_ROLE_NAMES = [
    "Admin",
    "Supervisor",
    "Cashier",
    "Chef",
    "Waiter",
    "Accountant",
    "System Operator",
]

DEFAULT_MODULES = [
    "dashboard",
    "pos",
    "products",
    "categories",
    "customers",
    "hold_resume_sale",
    "refund_return",
    "reports",
    "settings",
]


def seed_role_permissions(apps, schema_editor):
    Role = apps.get_model("pos_app", "Role")
    RolePermission = apps.get_model("pos_app", "RolePermission")

    for role_name in DEFAULT_ROLE_NAMES:
        role, _ = Role.objects.get_or_create(
            name=role_name,
            defaults={"is_active": True, "created_on": django.utils.timezone.now().date()},
        )
        for module_key in DEFAULT_MODULES:
            RolePermission.objects.get_or_create(
                role=role,
                module=module_key,
            )


class Migration(migrations.Migration):

    dependencies = [
        ("pos_app", "0009_customer_customer_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="Role",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80, unique=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_on", models.DateField(default=django.utils.timezone.now)),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="RolePermission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("module", models.CharField(max_length=50)),
                ("can_view", models.BooleanField(default=False)),
                ("can_add", models.BooleanField(default=False)),
                ("can_edit", models.BooleanField(default=False)),
                ("can_delete", models.BooleanField(default=False)),
                ("can_export", models.BooleanField(default=False)),
                ("can_approve_void", models.BooleanField(default=False)),
                ("role", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="permissions", to="pos_app.role")),
            ],
            options={
                "ordering": ["role_id", "module"],
                "unique_together": {("role", "module")},
            },
        ),
        migrations.RunPython(seed_role_permissions, migrations.RunPython.noop),
    ]
