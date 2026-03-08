from django.core.management.base import BaseCommand

from pos_app.models import Item, OrderItem


class Command(BaseCommand):
    help = "Normalize existing OrderItem.item_name values to clean base menu item names."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Persist the normalized names. Without this flag the command runs in dry-run mode.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Limit the number of rows inspected.",
        )

    def handle(self, *args, **options):
        apply_changes = bool(options["apply"])
        limit = max(int(options["limit"] or 0), 0)

        item_name_map = {
            item.name.strip().lower(): item.name.strip()
            for item in Item.objects.only("name").exclude(name__isnull=True)
        }

        queryset = OrderItem.objects.all().order_by("id")
        if limit:
            queryset = queryset[:limit]

        inspected = 0
        changed = 0
        updated_rows = []

        for order_item in queryset.iterator() if hasattr(queryset, "iterator") else queryset:
            inspected += 1
            current_name = (order_item.item_name or "").strip()
            normalized_name = self._normalize_name(current_name, item_name_map)
            if not normalized_name or normalized_name == current_name:
                continue

            changed += 1
            if apply_changes:
                order_item.item_name = normalized_name[:150]
                updated_rows.append(order_item)

        if apply_changes and updated_rows:
            OrderItem.objects.bulk_update(updated_rows, ["item_name"], batch_size=500)

        mode = "APPLY" if apply_changes else "DRY-RUN"
        self.stdout.write(self.style.SUCCESS(
            f"[{mode}] inspected={inspected} changed={changed}"
        ))

        if not apply_changes:
            self.stdout.write("Run with --apply to persist the cleaned names.")

    def _normalize_name(self, raw_name, item_name_map):
        name = str(raw_name or "").strip()
        if not name:
            return ""

        base_name = name.split(" + ", 1)[0].strip()
        if " (" in base_name and base_name.endswith(")"):
            base_name = base_name.rsplit(" (", 1)[0].strip()

        return item_name_map.get(base_name.lower(), base_name)
