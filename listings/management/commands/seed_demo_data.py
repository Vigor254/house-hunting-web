from django.core.management.base import BaseCommand
from listings.models import Landlord, Property
from listings.integrations import TUM_LATITUDE, TUM_LONGITUDE, calculate_distance_km


SAMPLE_LISTINGS = [
    dict(title="Sunrise Bedsitter", room_type="bedsitter", price_per_month=5500,
         location_name="Tudor, 5 min walk from main gate", lat=-4.0555, lng=39.6650,
         description="Cozy self-contained bedsitter a 5-minute walk from the main gate. "
                      "Tiled floors, own kitchenette and bathroom, reliable water supply."),
    dict(title="Green View Single Room", room_type="single", price_per_month=3200,
         location_name="Near Tom Mboya stage", lat=-4.0610, lng=39.6600,
         description="Affordable single room ideal for a student on a tight budget. "
                      "Shared bathroom, quiet compound, close to shops and matatu stage."),
    dict(title="Coast Comfort 1BR", room_type="1br", price_per_month=9000,
         location_name="Along Nkrumah Road", lat=-4.0500, lng=39.6700,
         description="Spacious one-bedroom unit, great for a student who wants extra room "
                      "or plans to share with a roommate. Balcony with sea breeze."),
    dict(title="Tudor Twin 2BR", room_type="2br", price_per_month=14000,
         location_name="Tudor Estate", lat=-4.0650, lng=39.6550,
         description="Two-bedroom apartment in a secure compound, well suited for splitting "
                      "rent with a roommate. Fitted kitchen and ample storage."),
    dict(title="Comrade Hostel", room_type="hostel", price_per_month=4200,
         location_name="Right next to campus", lat=-4.0590, lng=39.6640,
         description="Popular hostel right next to campus with multiple bed spaces available. "
                      "Includes study room, common kitchen and 24/7 security."),
    dict(title="Baraka Guest House", room_type="guesthouse", price_per_month=6000,
         location_name="Off Mwembe Tayari", lat=-4.0530, lng=39.6580,
         description="Guest house offering private and shared rooms with daily cleaning "
                      "service, popular with visiting students and short-stay tenants."),
]


class Command(BaseCommand):
    help = "Seeds a handful of sample Blueprint Housing listings so the site isn't empty on first run."

    def handle(self, *args, **options):
        landlord, _ = Landlord.objects.get_or_create(
            name="Demo Landlord",
            defaults={"phone_number": "0700000000", "is_subscribed": True},
        )

        created_count = 0
        for item in SAMPLE_LISTINGS:
            if Property.objects.filter(title=item["title"]).exists():
                continue
            distance = calculate_distance_km(TUM_LATITUDE, TUM_LONGITUDE, item["lat"], item["lng"])
            Property.objects.create(
                landlord=landlord,
                title=item["title"],
                room_type=item["room_type"],
                description=item["description"],
                price_per_month=item["price_per_month"],
                location_name=item["location_name"],
                latitude=item["lat"],
                longitude=item["lng"],
                distance_from_campus_km=distance,
                is_approved=True,
                is_active=True,
                added_by_john=True,
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {created_count} demo listings."))
