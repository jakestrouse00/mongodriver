import pymongo
from typing import Any, List, Union, Dict
from dataclasses import dataclass, field
from bson import ObjectId


@dataclass
class Document:
    _id: str = field(repr=True)
    variables: dict
    client: pymongo.collection.Collection = field(repr=False)
    _initialized: bool = field(repr=False, default=False)

    def __post_init__(self):
        if "_id" in self.variables.keys():
            self.variables.pop("_id")
        for variable in self.variables.keys():
            class_value = Variable(
                self._id, variable, self.variables[variable], self.client, self
            )
            setattr(self, variable, class_value)
        self._initialized = True

    def set(self, new_values: dict):
        """ADDS NEW VARIABLES TO THE DOCUMENT"""
        # removing _id in case it was passed. Don't want to try and update that lol
        if "_id" in new_values.keys():
            new_values.pop("_id")
        self.client.find_one_and_update(
            {"_id": ObjectId(self._id)},
            {"$set": new_values},
        )
        for variable in new_values.keys():
            class_value = Variable(
                self._id, variable, new_values[variable], self.client, self
            )

            self.variables[variable] = new_values[variable]
            # setattr(self, variable, class_value)
            self.__dict__[variable] = class_value

    def remove(self):
        self.client.find_one_and_delete({"_id": ObjectId(self._id)})

    def asdict(self) -> dict:
        return self.variables

    def __setattr__(self, key, value):
        """UPDATE VARIABLES DIRECTLY
        Document.variable = 10
        instead of
        Document.variable.update(10)
        """
        try:
            var = getattr(self, key)
            if str(key) in self.variables.keys() and var != value:
                var.update(value)
            else:
                self.__dict__[key] = value
        except Exception:
            if self._initialized:
                # object has been initialized, so we are making a new variable
                self.set({key: value})
            else:
                # object has not yet been initialized, so we are just updating the __dict__
                self.__dict__[key] = value


@dataclass
class Variable:
    _id: str = field(repr=False)
    key: str
    value: Any
    client: pymongo.collection.Collection = field(repr=False)
    parent_document: Document = field(repr=False)

    def __repr__(self):
        return str(self.value)

    def update(self, new_value: Any):
        self.client.find_one_and_update(
            {"_id": ObjectId(self._id)},
            {
                "$set": {
                    self.key: new_value,
                }
            },
        )
        self.value = new_value
        self.parent_document.variables[self.key] = new_value

    def remove(self):
        self.client.find_one_and_update(
            {"_id": ObjectId(self._id)}, {"$unset": {self.key: ""}}
        )
        self.parent_document.variables.pop(self.key)
        self.parent_document.__dict__.pop(self.key)


@dataclass
class Driver:
    connection_url: str = field(repr=True)
    db_name: str = field(repr=True)
    collection_name: str = field(repr=True)

    def __post_init__(self):
        """CONNECT TO THE DB"""
        self.client = pymongo.MongoClient(self.connection_url)[self.db_name][
            self.collection_name
        ]

    def create(self, data: dict) -> Document:
        """CREATE A DOCUMENT FROM A DICT AND RETURN THE Document OBJECT"""
        document = self.client.insert_one(data)
        python_document = Document(document.inserted_id, data, self.client)
        return python_document

    def update(
            self, data: dict | Document, new_values: dict, sort: dict = None
    ) -> Document:
        if "_id" in new_values.keys():
            new_values.pop("_id")
        if isinstance(data, Document):
            if sort is not None:
                sort = sort.items()
            self.client.find_one_and_update(
                filter={"_id": ObjectId(data._id)},
                update={"$set": new_values},
                sort=sort,
                return_document=True,
            )
            for _, (key, value) in enumerate(new_values.items()):
                class_value = Variable(data._id, key, value, self.client, data)

                data.variables[key] = new_values[key]
                # setattr(self, variable, class_value)
                data.__dict__[key] = class_value
            return data
        else:
            if "_id" in data.keys() and not isinstance(data["_id"], ObjectId):
                data["_id"] = ObjectId(data["_id"])
            document = self.client.find_one_and_update(
                filter=data,
                update={"$set": update},
                sort=sort.items(),
                return_document=True,
            )
            return Document(document.inserted_id, data, self.client)

    def remove(self, data: dict | Document):
        if isinstance(data, Document):
            self.client.find_one_and_delete({"_id": ObjectId(data._id)})
        else:
            if "_id" in data.keys() and not isinstance(data["_id"], ObjectId):
                data["_id"] = ObjectId(data["_id"])
            self.client.find_one_and_delete(data)

    def load(self) -> List[Document]:
        """LOADS ALL DOCUMENTS FROM DB INTO Document CLASSES"""
        documents = self.client.find({})
        loaded_documents = []
        for document in documents:
            doc_id = document["_id"]
            document.pop("_id")
            python_document = Document(str(doc_id), document, self.client)
            loaded_documents.append(python_document)
        return loaded_documents

    def find(self, search_terms: dict) -> List[Document]:
        """FIND A DOCUMENT AND RETURN IT AS A Document CLASS"""
        if "_id" in search_terms.keys() and not isinstance(
                search_terms["_id"], ObjectId
        ):
            search_terms["_id"] = ObjectId(search_terms["_id"])
        processed_documents = []
        documents = self.client.find(search_terms)
        for document in documents:
            doc_id = str(document["_id"])
            python_document = Document(doc_id, document, self.client)
            processed_documents.append(python_document)
        return processed_documents

    def find_one(self, search_terms: dict) -> Document | None:
        if "_id" in search_terms.keys() and not isinstance(
                search_terms["_id"], ObjectId
        ):
            search_terms["_id"] = ObjectId(search_terms["_id"])
        document = self.client.find_one(search_terms)
        if document is None:
            return None
        doc_id = str(document["_id"])
        python_document = Document(doc_id, document, self.client)
        return python_document


class ObjectPacker:
    # packing and unpacking objects is simple and technically this implementation may not be needed.
    # But I thought it was a nice touch just in case :)

    @staticmethod
    def pack(input_dict: dict, packed_name: str = "PackedObject"):
        """PACK A DICT INTO A PYTHON CLASS"""
        packed_obj = type(packed_name, (object,), input_dict)()
        return packed_obj

    @staticmethod
    def unpack(input_object):
        """UNPACK A PYTHON CLASS INTO IT'S DICT"""
        return input_object.__dict__


if __name__ == "__main__":
    # mongodb+srv://Influxes:test@testcluster.e2lhq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority
    x = Driver(
        connection_url="mongodb+srv://Influxes:test@testcluster.e2lhq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
        db_name="ev_runtime",
        collection_name="test_model",
    )
    # x.remove({"_id": "64b94bcbc98f284f29a7a502"})
    # doc = x.create({"name": "dude", "year": 2007})
    # print(doc)
    # doc.size = "UP"
    # print(doc)
    # x.update(doc, {"name": "charlie"})
    # print(doc)
    # x.remove(doc)
    print(x.find_one({"_id": "64b94bcbc98f284f29a7a503"}))
