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
        """
        Post-initialization method for the Document class.
        Removes '_id' from variables if present and initializes Variable instances for each variable.
        """
        if "_id" in self.variables.keys():
            self.variables.pop("_id")
        for variable in self.variables.keys():
            class_value = Variable(
                self._id, variable, self.variables[variable], self.client, self
            )
            setattr(self, variable, class_value)
        self._initialized = True

    def set(self, new_values: dict):
        """
        Adds new variables to the document and updates the database.

        Parameters:
        new_values (dict): A dictionary of new values to be added to the document.
        """
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
        """
        Removes the document from the database.
        """
        self.client.find_one_and_delete({"_id": ObjectId(self._id)})

    def asdict(self) -> dict:
        """
        Converts the document to a dictionary.

        Returns:
        dict: A dictionary representation of the document's variables.
        """
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
        """
       Updates the value of the variable in the database and the parent document.

       Parameters:
       new_value (Any): The new value to update the variable with.
       """
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
        """
        Removes the variable from the database and the parent document.
        """
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
        """
        Connect to the MongoDB database using the provided connection URL, database name, and collection name.
        """
        self.client = pymongo.MongoClient(self.connection_url)[self.db_name][
            self.collection_name
        ]

    def create(self, data: dict) -> Document:
        """
        Create a new document in the MongoDB collection from a dictionary and return it as a Document object.

        Parameters:
        data (dict): A dictionary containing the data to be inserted into the collection.

        Returns:
        Document: A Document object representing the newly created document.
        """
        document = self.client.insert_one(data)
        python_document = Document(document.inserted_id, data, self.client)
        return python_document

    def update(
            self, data: dict | Document, new_values: dict, sort: dict = None
    ) -> Document:
        """
        Update an existing document in the MongoDB collection with new values.

        Parameters:
        data (dict | Document): The document to be updated, either as a dictionary or a Document object.
        new_values (dict): A dictionary of new values to update the document with.
        sort (dict, optional): A dictionary specifying the sort order for the update operation.

        Returns:
        Document: A Document object representing the updated document.
        """
        if "_id" in new_values.keys():
            new_values.pop("_id")
        if sort is not None:
            sort = sort.items()
        if isinstance(data, Document):

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
                update={"$set": new_values},
                sort=sort,
                return_document=True,
            )
            return Document(document.inserted_id, data, self.client)

    def remove(self, data: dict | Document):
        """
        Remove a document from the MongoDB collection.

        Parameters:
        data (dict | Document): The document to be removed, either as a dictionary or a Document object.
        """
        if isinstance(data, Document):
            self.client.find_one_and_delete({"_id": ObjectId(data._id)})
        else:
            if "_id" in data.keys() and not isinstance(data["_id"], ObjectId):
                data["_id"] = ObjectId(data["_id"])
            self.client.find_one_and_delete(data)

    def load(self) -> List[Document]:
        """
        Load all documents from the MongoDB collection into Document objects.

        Returns:
        List[Document]: A list of Document objects representing all documents in the collection.
        """
        documents = self.client.find({})
        loaded_documents = []
        for document in documents:
            doc_id = document["_id"]
            document.pop("_id")
            python_document = Document(str(doc_id), document, self.client)
            loaded_documents.append(python_document)
        return loaded_documents

    def find(self, search_terms: dict) -> List[Document]:
        """
        Find documents in the MongoDB collection that match the search terms and return them as Document objects.

        Parameters:
        search_terms (dict): A dictionary of search terms to filter the documents.

        Returns:
        List[Document]: A list of Document objects representing the matching documents.
        """
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
        """
       Find a single document in the MongoDB collection that matches the search terms and return it as a Document object.

       Parameters:
       search_terms (dict): A dictionary of search terms to filter the documents.

       Returns:
       Document | None: A Document object representing the matching document, or None if no document is found.
       """
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
