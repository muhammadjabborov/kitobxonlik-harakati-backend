import openpyxl
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.common.models import Region


class Command(BaseCommand):
    """
    example:
    python manage.py load_regions
    """

    help = "Load regions, districts, and neighborhoods from excel_data/regions.xlsx"

    def handle(self, *args, **kwargs):
        path = settings.BASE_DIR / "excel_data" / "regions.xlsx"
        wb = openpyxl.load_workbook(filename=path)
        ws = wb.active

        rows = iter(ws.rows)
        next(rows)  # skip header

        region_cache: dict[str, Region] = {}
        district_cache: dict[str, Region] = {}

        created_regions = created_districts = created_neighborhoods = 0

        for row in rows:
            region_code = row[0].value
            region_name = row[1].value
            district_code = row[2].value
            district_name = row[3].value
            neighborhood_code = row[4].value
            neighborhood_name = row[5].value

            if not region_name or not district_name or not neighborhood_name:
                continue

            region_name = str(region_name).strip()
            district_name = str(district_name).strip()
            neighborhood_name = str(neighborhood_name).strip()

            # Region (level 0)
            if region_code not in region_cache:
                region, created = Region.objects.update_or_create(
                    soato=str(region_code),
                    defaults={"name": region_name, "parent": None},
                )
                if created:
                    created_regions += 1
                region_cache[region_code] = region
            region = region_cache[region_code]

            # District (level 1)
            if district_code not in district_cache:
                district, created = Region.objects.update_or_create(
                    soato=str(district_code),
                    defaults={"name": district_name, "parent": region},
                )
                if created:
                    created_districts += 1
                district_cache[district_code] = district
            district = district_cache[district_code]

            # Neighborhood (level 2)
            _, created = Region.objects.update_or_create(
                soato=str(neighborhood_code),
                defaults={"name": neighborhood_name, "parent": district},
            )
            if created:
                created_neighborhoods += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done! Created: {created_regions} regions, "
                f"{created_districts} districts, "
                f"{created_neighborhoods} neighborhoods."
            )
        )
