from pydantic import BaseModel
from pydantic.types import condecimal

# Create Address Schema (Pydantic Model)
class AddressCreate(BaseModel):
    locality: str
    city: str
    latitude: condecimal(max_digits=9,decimal_places=6)
    longitude: condecimal(max_digits=9,decimal_places=6)


# Complete Address Schema (Pydantic Model)
class Address(BaseModel):
    address_id: int
    locality: str
    city: str
    latitude: condecimal(max_digits=9,decimal_places=6)
    longitude: condecimal(max_digits=9,decimal_places=6)

    class Config:
        from_attributes = True
