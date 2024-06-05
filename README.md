# Introduction

This is a basic project showing how to use fastapi along with the Motor library, which is a async driver for MongoDB.

# Setup dev environment

- Install and run MongoDB: [Instructions](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/)

- Seed the database. Run:
```
python3 playing_fast_api/seeds/db_seed.py
```

- Install poetry: [Instructions](https://www.digitalocean.com/community/tutorials/how-to-install-poetry-to-manage-python-dependencies-on-ubuntu-22-04)

- Use a virtual environment
```
# Create
python3 -m venv my_venv

# Activate
. ./my_venv/bin/activate
```

- Install dependencies

In the root folder, run:
```
poetry install
```

# Running the server

Go to the folder where is the file `server.py` and run:
```
uvicorn server:app --reload
```

Then you can check the available APIs on http://127.0.0.1:8000/docs