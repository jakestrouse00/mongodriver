from mongodriver.mongodriver import Driver

driver = Driver(
    connection_url="mongodb+srv://example:SecurePassword@testcluster.e2lhq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
    db_name="example_db", collection_name="example_collection")

documents = driver.load()  # loads all documents from db into local Document objects
for document in documents:
    print(document)


