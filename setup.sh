#!/usr/bin/env bash

# Install OSX libraries
brew install mongodb
brew install python
brew install pip

pip install pymongo
pip install flask

# Import documents into mongodb
mongoimport --db unicornstore --collection unicornstore --jsonArray --file static/data.json

# Create mongodb indexes from within console
# db.unicornstore.createIndex( { "id": 1 }, { unique: true } )
# db.unicornstore.createIndex( { "location": "2d" } )
