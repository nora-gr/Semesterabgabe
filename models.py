"""
Pydantic-Modelle uebernommen aus der Uebung, nur um description ergaenzt
– werden von main.py fuer Request-Validierung genutzt.
"""
from pydantic import BaseModel, field_validator
from typing import Literal


class BookingCreate(BaseModel):
    """Schema fuer das Erstellen einer neuen Buchung (POST /bookings)."""
    booking_date: str
    booking_type: Literal["revenue", "expense"]
    category: str
    partner_name: str
    amount_net: float
    currency: str = "EUR"
    is_paid: bool = False
    description: str

    @field_validator("amount_net")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("amount_net muss groesser als 0 sein")
        return v


class BookingResponse(BookingCreate):
    """Schema fuer eine Buchung als Antwort (inkl. ID)."""
    booking_id: int

    class Config:
        from_attributes = True
