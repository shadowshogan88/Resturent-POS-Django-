from django.db import migrations, models


def seed_sort_order(apps, schema_editor):
    DiningTable = apps.get_model("pos_app", "DiningTable")
    for floor in ["1st", "2nd", "3rd"]:
        rows = list(DiningTable.objects.filter(floor=floor).order_by("id"))
        for index, row in enumerate(rows, start=1):
            row.sort_order = index
            row.save(update_fields=["sort_order"])


class Migration(migrations.Migration):

    dependencies = [
        ("pos_app", "0016_diningtable"),
    ]

    operations = [
        migrations.AddField(
            model_name="diningtable",
            name="sort_order",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.RunPython(seed_sort_order, migrations.RunPython.noop),
    ]
