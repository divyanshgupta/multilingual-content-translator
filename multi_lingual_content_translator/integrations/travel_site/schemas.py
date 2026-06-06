from pydantic import BaseModel, Field

from multi_lingual_content_translator.models.schemas import ContentType


class RoomContent(BaseModel):
    room_id: str
    name: str
    description: str
    amenities: list[str] = Field(default_factory=list)
    bed_type: str = ""
    max_occupancy: int = 2


class HotelContent(BaseModel):
    hotel_id: str
    name: str
    description: str
    address: str
    city: str
    country: str
    star_rating: float = 0.0
    amenities: list[str] = Field(default_factory=list)
    rooms: list[RoomContent] = Field(default_factory=list)
    cancellation_policy: str = ""
    check_in_time: str = "15:00"
    check_out_time: str = "12:00"


class WhitelabelContentBundle(BaseModel):
    """Content bundle from a travel site."""

    partner_id: str
    brand_name: str
    locale: str = "en"
    hotel: HotelContent | None = None
    ui_strings: dict[str, str] = Field(default_factory=dict)
    policies: dict[ContentType, str] = Field(default_factory=dict)

    def extract_translatable_items(self) -> list[dict]:
        items: list[dict] = []

        if self.hotel:
            items.append(
                {
                    "key": f"hotel.{self.hotel.hotel_id}.name",
                    "text": self.hotel.name,
                    "content_type": ContentType.HOTEL_DESCRIPTION,
                }
            )
            items.append(
                {
                    "key": f"hotel.{self.hotel.hotel_id}.description",
                    "text": self.hotel.description,
                    "content_type": ContentType.HOTEL_DESCRIPTION,
                }
            )
            for room in self.hotel.rooms:
                items.append(
                    {
                        "key": f"room.{room.room_id}.name",
                        "text": room.name,
                        "content_type": ContentType.ROOM_DESCRIPTION,
                    }
                )
                items.append(
                    {
                        "key": f"room.{room.room_id}.description",
                        "text": room.description,
                        "content_type": ContentType.ROOM_DESCRIPTION,
                    }
                )

        for key, text in self.ui_strings.items():
            items.append(
                {
                    "key": f"ui.{key}",
                    "text": text,
                    "content_type": ContentType.UI_STRING,
                }
            )

        for content_type, text in self.policies.items():
            items.append(
                {
                    "key": f"policy.{content_type.value}",
                    "text": text,
                    "content_type": content_type,
                }
            )

        return items
