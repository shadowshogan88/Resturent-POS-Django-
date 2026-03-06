from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("pos_app", "0010_role_rolepermission"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserPermissionOverride",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("module", models.CharField(max_length=50)),
                ("can_view", models.BooleanField(default=False)),
                ("can_add", models.BooleanField(default=False)),
                ("can_edit", models.BooleanField(default=False)),
                ("can_delete", models.BooleanField(default=False)),
                ("can_export", models.BooleanField(default=False)),
                ("can_approve_void", models.BooleanField(default=False)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="permission_overrides", to="pos_app.user")),
            ],
            options={
                "ordering": ["user_id", "module"],
                "unique_together": {("user", "module")},
            },
        ),
    ]
