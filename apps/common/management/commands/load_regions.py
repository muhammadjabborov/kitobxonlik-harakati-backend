import openpyxl

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.common.models import District, Neighborhood, Region


class Command(BaseCommand):
    help = "Load regions, districts, and neighborhoods from region_data/regions.xlsx"

    def handle(self, *args, **kwargs):
        path = settings.BASE_DIR / "region_data" / "regions.xlsx"
        wb = openpyxl.load_workbook(filename=path)
        ws = wb.active

        rows = iter(ws.rows)
        next(rows)  # skip header

        region_cache: dict[str, Region] = {}
        district_cache: dict[tuple, District] = {}

        created_regions = created_districts = created_neighborhoods = 0

        for row in rows:
            region_name = row[1].value
            district_name = row[3].value
            neighborhood_name = row[5].value

            if not region_name or not district_name or not neighborhood_name:
                continue

            region_name = region_name.strip()
            district_name = district_name.strip()
            neighborhood_name = neighborhood_name.strip()

            # Region
            if region_name not in region_cache:
                region, created = Region.objects.get_or_create(name=region_name)
                if created:
                    created_regions += 1
                region_cache[region_name] = region
            region = region_cache[region_name]

            # District
            district_key = (region.pk, district_name)
            if district_key not in district_cache:
                district, created = District.objects.get_or_create(
                    region=region, name=district_name
                )
                if created:
                    created_districts += 1
                district_cache[district_key] = district
            district = district_cache[district_key]

            # Neighborhood
            _, created = Neighborhood.objects.get_or_create(
                district=district, name=neighborhood_name
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
