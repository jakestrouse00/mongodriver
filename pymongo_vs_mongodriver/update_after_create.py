from pymongo import MongoClient
from mongodriver.src.mongodriver import Driver


def creating_document_and_updating_with_mongodriver():
    client = Driver(
        connection_url="mongodb+srv://Influxes:test@testcluster.e2lhq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
        db_name="ev_runtime",
        collection_name="test_model",
    )
    document = client.create({"name": "bobby", "year": 2003})
    document.year = 2004


def creating_document_and_updating_with_pymongo():
    client = MongoClient(
        "mongodb+srv://Influxes:test@testcluster.e2lhq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
    )["ev_runtime"]["test_model"]
    document = client.insert_one({"name": "bobby", "year": 2003})
    client.find_one_and_update(
        {"_id": document.inserted_id},
        {
            "$set": {
                "year": 2004,
            }
        },
    )
