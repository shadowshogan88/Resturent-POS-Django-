from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pos_app", "0011_userpermissionoverride"),
    ]

    operations = [
        migrations.CreateModel(
            name="PrintSetting",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("enable_print", models.BooleanField(default=True)),
                ("show_store_details", models.BooleanField(default=True)),
                ("show_customer_details", models.BooleanField(default=True)),
                ("page_size", models.CharField(choices=[("A1", "A1"), ("A2", "A2"), ("A3", "A3"), ("A4", "A4"), ("A5", "A5")], default="A4", max_length=2)),
                ("header", models.TextField(blank=True)),
                ("footer", models.TextField(blank=True)),
                ("show_notes", models.BooleanField(default=True)),
                ("print_tokens", models.BooleanField(default=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["id"],
            },
        ),
    ]
