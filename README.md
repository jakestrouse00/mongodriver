# MongoDriver

An object-oriented package for interacting with MongoDB documents



Features
--------

* Object-oriented
* Update documents without needing to use json
* Use pymongo within the package as well
* Built with type hints
* Removes a lot of [boilerplate](pymongo_vs_mongodriver/README.md) code 
* So simple it works like ✨magic ✨


Quickstart
----------

Install MongoDriver
`python3 -m pip install mongodriver`

```python
from mongodriver.mongodriver import Driver

driver = Driver(
    connection_url="mongodb+srv://example:SecurePassword@testcluster.e2lhq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
    db_name="example_db", collection_name="example_collection")
```
   
Examples
----------
Here is a basic example on how to create a new document and then interact it

```python
from mongodriver.mongodriver import Driver

driver = Driver(
    connection_url="mongodb+srv://example:SecurePassword@testcluster.e2lhq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
    db_name="example_db", collection_name="example_collection")

new_document = driver.create({"foo": 1, "bar": 2})

# print the value of "foo"
print(new_document.foo)  # 1

# change the value of "foo"
new_document.foo = 2
print(new_document.foo)  # 2

# you can also change the value of an attribute with the Driver.Variable.update() method

new_document.foo.update(3)

print(new_document.foo)  # 3
```

Find a document

```python
from mongodriver.mongodriver import Driver

driver = Driver(
    connection_url="mongodb+srv://example:SecurePassword@testcluster.e2lhq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
    db_name="example_db", collection_name="example_collection")

search_query = {"foo": 1}
documents = driver.find(search_query)  # returns a list of documents
for document in documents:
    print(document)
```

Load all documents from MongoDB into Document objects

```python
from mongodriver.mongodriver import Driver

driver = Driver(
    connection_url="mongodb+srv://example:SecurePassword@testcluster.e2lhq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
    db_name="example_db", collection_name="example_collection")

documents = driver.load()  # loads all documents from db into local Document objects
for document in documents:
    print(document)
```

Add more keys into a document

```python
from mongodriver.mongodriver import Driver

driver = Driver(
    connection_url="mongodb+srv://example:SecurePassword@testcluster.e2lhq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
    db_name="example_db", collection_name="example_collection")

json_document = {"foo": 1, "bar": 2}
new_document = driver.create(json_document)

new_document.set({"new_val1": 15, "new_val2": 10})

# OR

new_document.new_val1 = 15
new_document.new_val2 = 10

print(new_document)

```