import click
import json
import typer

from dateutil.parser import parse

from sqlmodel import col, select, Session
from sqlmodel.sql.expression import Select, SelectOfScalar

SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore

from model import create_table, StarlinkRecord, engine

app = typer.Typer()


@app.command(name="initialize_db")
def init_db():
    """Create the table `starlinkrecord` in the DB"""
    create_table()


@app.command(name="load_data")
def load_data():
    """Load data into the DB from the provided json file"""

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


@app.command()
def main(name: str):
    print(f"Henlo {name}")


if __name__ == "__main__":
    app()
