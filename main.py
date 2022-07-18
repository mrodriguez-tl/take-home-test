import click
import json
import typer

from sqlmodel import Session

from model import create_table, StarlinkRecord, engine

app = typer.Typer()


@app.command(name="initialize_db")
def init_db():
    create_table()


@app.command(name="load_data")
def load_data():
    with open("data/starlink_historical_data.json", "r") as json_file:
        data = json.load(json_file)
    with Session(engine) as session:
        for row in data:
            creation_date = row["spaceTrack"]["CREATION_DATE"]
            latitude = row["latitude"]
            longitude = row["longitude"]
            satelite_id = row["id"]

            starlink_record = StarlinkRecord(
                creation_date=creation_date,
                latitude=latitude,
                longitude=longitude,
                satelite_id=satelite_id,
            )
            session.add(starlink_record)
        session.commit()


@app.command()
def main(name: str):
    print(f"Henlo {name}")


if __name__ == "__main__":
    app()
