from django.db import migrations, models


def seed_tables(apps, schema_editor):
    DiningTable = apps.get_model("pos_app", "DiningTable")
    seed_rows = [
        ("Table 1", "1st", "tables-01.svg", 6, "Available"),
        ("Table 2", "1st", "tables-02.svg", 4, "Available"),
        ("Table 3", "1st", "tables-01.svg", 6, "Booked"),
        ("Table 4", "1st", "tables-04.svg", 10, "Booked"),
        ("Table 5", "1st", "tables-05.svg", 10, "Booked"),
        ("Table 6", "1st", "tables-06.svg", 10, "Available"),
        ("Table 7", "1st", "tables-01.svg", 6, "Available"),
        ("Table 8", "1st", "tables-01.svg", 6, "Booked"),
        ("Table 9", "2nd", "tables-01.svg", 6, "Available"),
        ("Table 10", "2nd", "tables-01.svg", 6, "Booked"),
        ("Table 11", "2nd", "tables-02.svg", 4, "Available"),
        ("Table 12", "2nd", "tables-06.svg", 10, "Available"),
        ("Table 13", "3rd", "tables-02.svg", 4, "Available"),
        ("Table 14", "3rd", "tables-14.svg", 10, "Available"),
        ("Table 15", "3rd", "tables-02.svg", 4, "Available"),
        ("Table 16", "3rd", "tables-06.svg", 10, "Available"),
    ]
    for name, floor, image_name, guest_capacity, status in seed_rows:
        DiningTable.objects.get_or_create(
            name=name,
            defaults={
                "floor": floor,
                "image_name": image_name,
                "guest_capacity": guest_capacity,
                "status": status,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("pos_app", "0015_auditlog"),
    ]

    operations = [
        migrations.CreateModel(
            name="DiningTable",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80, unique=True)),
                ("floor", models.CharField(choices=[("1st", "1st"), ("2nd", "2nd"), ("3rd", "3rd")], max_length=10)),
                (
                    "image_name",
                    models.CharField(
                        choices=[
                            ("tables-01.svg", "Table 1"),
                            ("tables-02.svg", "Table 2"),
                            ("tables-04.svg", "Table 4"),
                            ("tables-05.svg", "Table 5"),
                            ("tables-06.svg", "Table 6"),
                            ("tables-14.svg", "Table 14"),
                            ("tables-17.svg", "Table 17"),
                            ("tables-18.svg", "Table 18"),
                            ("tables-19.svg", "Table 19"),
                        ],
                        default="tables-01.svg",
                        max_length=20,
                    ),
                ),
                ("guest_capacity", models.PositiveIntegerField(default=4)),
                ("status", models.CharField(choices=[("Available", "Available"), ("Booked", "Booked")], default="Available", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.RunPython(seed_tables, migrations.RunPython.noop),
    ]
