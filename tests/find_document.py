from mongodriver.mongodriver import Driver

driver = Driver(
    connection_url="mongodb+srv://example:SecurePassword@testcluster.e2lhq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
    db_name="example_db", collection_name="example_collection")

search_query = {"foo": 1}
documents = driver.find(search_query)  # returns a list of documents
for document in documents:
    print(document)
