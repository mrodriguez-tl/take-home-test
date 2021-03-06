# take-home-test

## Initial Setup
- Clone the repo & `cd` into the directory
- Create a virtualenv using your preferred method (>3.8 should work fine)
- Install poetry
```py
pip install poetry
```
- Install the dependencies
```py
poetry install
```
- Spin up the postgres DB
```sh
make up
```

## Load data into the db
```py
poetry run python main.py initialize_db
```

## Get the last known position of a satellite (by id), at a give time
The time can be in `yyyymmdd` or `yyyy-mm-dd` formats, or in timestamp format: `yyyy-mm-ddTHH:MM:SS`
```py
poetry run python main.py get_by_id -- 5eed7714096e590006985660 20220101
```
```py
poetry run python main.py get_by_id -- 5eed7714096e590006985660 2020-03-01
```
```py
poetry run python main.py get_by_id -- 5eed7714096e590006985660 2021-01-26T19:34:00
```

## Get the closest satellite at a given time, and a given position
This funcion will first find the closest (earlier) timestamp that is present in the DB for the given time. This is needed because it doesn't make much sense to compare distances at different times, when no other information such as satellite velocity or direction is considered.
Then, it will calculate the (haversine) distance between the provided location and the satellites at that time, and will return the id of the closest one.

The arguments are `-- <lat> <long> <time>`
```py
poetry run python main.py get_closest_satellite -- 20.8272 2 20190126
```
```py
# Coordinates can be negative
poetry run python main.py get_closest_satellite -- -45.172 2 2021-01-26T23:16:00
```
```py
poetry run python main.py get_closest_satellite -- 45.172 2 2021-01-26T23:16:00
```
```py
poetry run python main.py get_closest_satellite -- 15.172 150 2021-02-01
```

## Notes
I decided to use an ORM (sqlmodel) instead of plain sql because this would allow a very easy integration into an api using fastapi, so that the DB could be queried via an endpoint instead of CLI arguments