import click
import json
import typer

from dateutil.parser import parse
from haversine import haversine
from sqlmodel import col, select, Session
from sqlmodel.sql.expression import Select, SelectOfScalar

# This is needed to avoid SAWarning messages when running CLI commands
SelectOfScalar.inherit_cache = True
Select.inherit_cache = True

from model import create_table, StarlinkRecord, engine

app = typer.Typer()


@app.command(name="initialize_db")
def init_db_and_data():
    """Create the starlinkrecord table and load data
    from the provided json file"""

    create_table()

    with open("data/starlink_historical_data.json", "r") as json_file:
        data = json.load(json_file)

    with Session(engine) as session:
        for row in data:
            creation_date = row["spaceTrack"]["CREATION_DATE"]
            latitude = str(row["latitude"])
            longitude = str(row["longitude"])
            satellite_id = row["id"]

            starlink_record = StarlinkRecord(
                creation_date=creation_date,
                latitude=latitude,
                longitude=longitude,
                satellite_id=satellite_id,
            )
            session.add(starlink_record)

        session.commit()


@app.command(name="get_by_id")
def get_position_by_id(id: str, datetime: str) -> str:
    """Get the last known position of a satellite by id at a given time
    """
    with Session(engine) as session:
        statement = select(StarlinkRecord).where(
            col(StarlinkRecord.satellite_id) == id,
            col(StarlinkRecord.creation_date) <= parse(datetime),
        )
        result = session.exec(statement).first()
        if result:
            print(f"({result.latitude}, {result.longitude})")
        else:
            print("Not found")


@app.command(name="get_closest_satellite")
def get_closest_satellite_by_position_and_datetime(
    position: tuple[float, float], datetime: str
):
    """Get the closest satellite (id) by position at a given datetime,
    using the haversine formula to calculate the distance.
    """

    # First, find the closest timestamp that is present in the database for the given datetime
    # This is needed because it doesn't make much sense to compare distances at different
    # times, since we are not considering any other satellite data such as speed, etc.
    closest_datetime_in_db = None
    with Session(engine) as session:
        statement = select(StarlinkRecord).where(
            col(StarlinkRecord.creation_date) <= parse(datetime)
        )
        results = session.exec(statement).all()
        if results:
            closest_datetime_in_db = sorted(
                [result.creation_date for result in results], reverse=True
            )[0]

    # Fetch all records for the closest timestamp in the DB, and calculate the haversine distance
    if closest_datetime_in_db is not None:
        satellites_by_distance = []
        with Session(engine) as session:
            statement = select(StarlinkRecord).where(
                col(StarlinkRecord.creation_date) == closest_datetime_in_db
            )
            results = session.exec(statement).all()
            for result in results:
                distance = haversine(
                    position, (float(result.latitude), float(result.longitude))
                )
                satellites_by_distance.append((result.satellite_id, distance))

        print(sorted(satellites_by_distance, key=lambda x: x[1])[0][0])
    else:
        print("No records found for the provided time")


if __name__ == "__main__":
    app()
