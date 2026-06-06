"""Sample travel site content for testing the translation pipeline."""

from multi_lingual_content_translator.integrations.schemas import (
    HotelContent,
    RoomContent,
    WhitelabelContentBundle,
)
from multi_lingual_content_translator.models.schemas import ContentType

SAMPLE_HOTEL_DESCRIPTION = """
Grand Marina Resort & Spa — Bangkok

Located in the heart of Sukhumvit, Grand Marina Resort offers stunning city views
and world-class amenities. Enjoy free cancellation on select rates, breakfast included
packages, and instant confirmation when you book today.

Amenities: rooftop pool, fitness center, free Wi-Fi, 24-hour front desk.

Cancellation: Free cancellation until 48 hours before check-in. Non-refundable rates
are also available at a discounted price of {price} THB per night.
""".strip()

SAMPLE_UI_STRINGS = {
    "search_placeholder": "Where are you going?",
    "book_now": "Book Now",
    "free_cancellation": "Free Cancellation",
    "pay_at_hotel": "Pay at Hotel",
    "rooms_left": "Only {count} rooms left!",
    "price_per_night": "From {price} per night",
}

SAMPLE_BUNDLE = WhitelabelContentBundle(
    partner_id="partner_th_001",
    brand_name="TravelAsia Partner",
    locale="en",
    hotel=HotelContent(
        hotel_id="HTL-98765",
        name="Grand Marina Resort & Spa",
        description=SAMPLE_HOTEL_DESCRIPTION,
        address="123 Sukhumvit Road",
        city="Bangkok",
        country="Thailand",
        star_rating=4.5,
        amenities=["Pool", "Spa", "Restaurant", "Free Wi-Fi"],
        rooms=[
            RoomContent(
                room_id="RM-DLX-01",
                name="Deluxe King Room",
                description=(
                    "Spacious 35 sqm room with king bed, city view, "
                    "and complimentary minibar. Breakfast included."
                ),
                amenities=["King Bed", "City View", "Minibar"],
                bed_type="King",
                max_occupancy=2,
            ),
            RoomContent(
                room_id="RM-STD-02",
                name="Standard Twin Room",
                description="Comfortable 28 sqm room with twin beds. Ideal for friends traveling together.",
                amenities=["Twin Beds", "Garden View"],
                bed_type="Twin",
                max_occupancy=2,
            ),
        ],
        cancellation_policy=(
            "Free cancellation until 48 hours before check-in. "
            "Cancellations within 48 hours are non-refundable."
        ),
    ),
    ui_strings=SAMPLE_UI_STRINGS,
    policies={
        ContentType.PAYMENT_TERMS: (
            "Pay at hotel option available. Credit card required to guarantee booking. "
            "Prices shown in USD unless otherwise stated."
        ),
    },
)
