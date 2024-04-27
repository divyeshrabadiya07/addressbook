from typing import List
from fastapi import FastAPI
from fastapi import FastAPI, HTTPException, Depends, status
from database import BaseClass, sqlite_engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from geopy import distance
import schemas
import models
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create a logger
logger = logging.getLogger(__name__)

# Create database
BaseClass.metadata.create_all(sqlite_engine)

# Initialize app
app = FastAPI()
logger.debug('FastAPI application instance created.')

# Function to get SQLite database session
def get_sqlite_db_session():

    db_session = SessionLocal()
    try:
        yield db_session
        logger.debug('SQLite database connection initiated.')
    finally:
        db_session.close()
        logger.debug('SQLite database connection closed.')


@app.get("/")
def root():
    return "Address Book Application."


@app.get("/addressBook/{address_id}", response_model=schemas.Address)
def read_address(address_id: int, db_session: Session = Depends(get_sqlite_db_session)):

    logger.debug(
        f"Recieved GET address request with address_id : {address_id}.")

    # fetch address with given address_id
    address = db_session.query(models.AddressBook).get(address_id)

    # make sure address with given address_id exists, else raise exception with HTTP 404 not found response
    if address:
        logger.debug(
            f"Address with given address_id : {address_id} fetched successfully.")
        return address
    else:
        logger.error(
            f"Address with given address_id : {address_id} not found in database.")
        raise HTTPException(
            status_code=404,
            detail=f"Address with given address_id : {address_id} not found in database.")


@app.post("/addressBook/", response_model=schemas.Address, status_code=status.HTTP_201_CREATED)
def create_address(address: schemas.AddressCreate, db_session: Session = Depends(get_sqlite_db_session)):

    logger.debug(f"Recieved POST address request with data : {address}.")

    # make sure given input for latitude & longitude is in range of (-90, 90) & (-180, 180) respectively
    if (-90 <= address.latitude <= 90) and (-180 <= address.longitude <= 180):

        # create an instance of AddressBook database model
        address = models.AddressBook(locality=address.locality, city=address.city, latitude=address.latitude,
                                     longitude=address.longitude)

        # add address into database and commit it
        db_session.add(address)
        db_session.commit()
        db_session.refresh(address)

        logger.debug(
            f"Address created & stored successfully.")
        return address
    else:
        logger.error(
            f"Coordinate {address.latitude,address.longitude} not in range latitude(-90,90) and longitude(-180,180).")
        raise HTTPException(
            status_code=404,
            detail=f"Coordinate {address.latitude,address.longitude} not in range latitude(-90,90) and longitude(-180,180).")


@app.put("/addressBook/{address_id}", response_model=schemas.Address)
def update_address(address_id: int, address_request: schemas.AddressCreate,
                   db_session: Session = Depends(get_sqlite_db_session)):

    logger.debug(
        f"Recieved PUT address request with address_id : {address_id} and data : {address_request}.")

    # fetch address with given address_id
    address = db_session.query(models.AddressBook).get(address_id)

    # update address with given address_id if exist, else raise exception with HTTP 404 not found response
    if (-90 <= address_request.latitude <= 90) and (-180 <= address_request.longitude <= 180):

        if address:
            update_address_encoded = jsonable_encoder(address_request)
            address.locality = update_address_encoded["locality"]
            address.city = update_address_encoded["city"]
            address.latitude = update_address_encoded["latitude"]
            address.longitude = update_address_encoded["longitude"]
            db_session.commit()

        if address:
            logger.debug(
                f"Address updated & stored successfully.")
            return address
        else:
            logger.error(
                f"Address with given address_id : {address_id} not found.")
            raise HTTPException(
                status_code=404, detail=f"Address with given address_id : {address_id} not found.")
    else:
        logger.error(
            f"""Coordinate {address_request.latitude, address_request.longitude} not in range 
            latitude(-90, 90) and longitude(-180, 180).""")
        raise HTTPException(
            status_code=404,
            detail=f"""Coordinate {address_request.latitude, address_request.longitude} not in range 
            latitude(-90, 90) and longitude(-180, 180).""")


@app.delete("/addressBook/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(address_id: int, db_session: Session = Depends(get_sqlite_db_session)):

    logger.debug(
        f"Recieved DELETE address request with address_id : {address_id}.")

    # fetch address with given address_id
    address = db_session.query(models.AddressBook).get(address_id)

    # make sure address with given address_id exists and hence delete it, else raise HTTP 404 not found response
    if address:
        db_session.delete(address)
        db_session.commit()
        logger.debug(f"Address deleted successfully.")
    else:
        logger.error(f"Address with given address_id : {address_id} not found.")
        raise HTTPException(
            status_code=404, detail=f"Address with given address_id : {address_id} not found.")

    return None


@app.get("/addressBook/", response_model=List[schemas.Address])
def read_address_list(db_session: Session = Depends(get_sqlite_db_session)):

    logger.debug(
        "Recieved GET request to fetch all the addresses present in database.")

    # fetch all addresses present in database
    address_list = db_session.query(models.AddressBook).all()

    logger.debug(f"All addresses fetched successfully.")

    return address_list


@app.get("/get_address_by_coordinate/", response_model=List[schemas.Address])
def get_address_by_coordinate(input_distance: float, latitude: float, longitude: float,
                              db_session: Session = Depends(get_sqlite_db_session)):

    logger.debug(
        f"""Recieved GET request to fetch the addresses that are within a
        given distance {input_distance} and location coordinate {(latitude, longitude)}.""")

    # prepare nearby address list from given input if exist, else raise exception with HTTP 404 not found response
    if (-90 <= latitude <= 90) and (-180 <= longitude <= 180):

        input_coordinate_tuple = (latitude, longitude)
        logger.debug(f"Input coordinate tuple : {input_coordinate_tuple}")

        radius = input_distance  # in km
        logger.debug(f"Input distance in km : {radius}")

        addressbook_data = db_session.query(models.AddressBook).all()

        nearby_address_list = []
        for address in addressbook_data:
            addressbook_coordinate_tuple = (
                address.latitude, address.longitude)
            logger.debug(
                f"Addressbook coordinate tuple : {addressbook_coordinate_tuple}")

            actual_distance = distance.distance(
                input_coordinate_tuple, addressbook_coordinate_tuple).km
            logger.debug(
                f"Actual distance between two coordinates in km : {actual_distance}")

            if actual_distance <= radius:
                nearby_address_list.append(address)

        logger.debug(
            f"Nearby addresses fetched successfully.")
        return nearby_address_list
    else:
        logger.error(
            f"Coordinate {latitude,longitude} not in range latitude(-90,90) and longitude(-180,180).")
        raise HTTPException(
            status_code=404,
            detail=f"Coordinate {latitude,longitude} not in range latitude(-90,90) and longitude(-180,180).")
