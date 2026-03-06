from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pos_app", "0012_printsetting"),
    ]

    operations = [
        migrations.CreateModel(
            name="StoreSetting",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("store_image", models.FileField(blank=True, null=True, upload_to="store/")),
                ("store_name", models.CharField(default="", max_length=160)),
                ("address_1", models.CharField(default="", max_length=255)),
                ("address_2", models.CharField(blank=True, default="", max_length=255)),
                ("country", models.CharField(choices=[("United States", "United States"), ("Canada", "Canada"), ("Germany", "Germany"), ("France", "France")], default="United States", max_length=50)),
                ("state", models.CharField(choices=[("California", "California"), ("New York", "New York"), ("Texas", "Texas"), ("Florida", "Florida")], default="California", max_length=50)),
                ("city", models.CharField(choices=[("Los Angeles", "Los Angeles"), ("San Diego", "San Diego"), ("Fresno", "Fresno"), ("San Francisco", "San Francisco")], default="Los Angeles", max_length=80)),
                ("pincode", models.CharField(default="", max_length=20)),
                ("email", models.EmailField(default="", max_length=254)),
                ("phone", models.CharField(default="", max_length=30)),
                ("currency", models.CharField(choices=[("USD", "USD"), ("AED", "AED"), ("EUR", "EUR"), ("INR", "INR")], default="USD", max_length=10)),
                ("enable_qr_menu", models.BooleanField(default=True)),
                ("enable_take_away", models.BooleanField(default=True)),
                ("enable_dine_in", models.BooleanField(default=True)),
                ("enable_reservation", models.BooleanField(default=False)),
                ("enable_order_via_qr_menu", models.BooleanField(default=True)),
                ("enable_delivery", models.BooleanField(default=True)),
                ("enable_table", models.BooleanField(default=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["id"],
            },
        ),
    ]
