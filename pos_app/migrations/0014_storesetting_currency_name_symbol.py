from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pos_app", "0013_storesetting"),
    ]

    operations = [
        migrations.AddField(
            model_name="storesetting",
            name="currency_name",
            field=models.CharField(default="US Dollar", max_length=50),
        ),
        migrations.AddField(
            model_name="storesetting",
            name="currency_symbol",
            field=models.CharField(default="$", max_length=10),
        ),
    ]
