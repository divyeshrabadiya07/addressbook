from sqlalchemy import Column, Integer, Numeric, String
from database import BaseClass

# Define Address Book class model
class AddressBook(BaseClass):
    __tablename__ = 'addressbook'

    address_id = Column(Integer, primary_key=True)
    locality = Column(String(256))
    city = Column(String(256))
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
