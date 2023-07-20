from mongodriver.src.mongodriver import Driver

driver = Driver(
        connection_url="mongodb+srv://example:SecurePassword@testcluster.e2lhq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
        db_name="example_db", collection_name="example_collection")

json_document = {"foo": 1, "bar": 2}
new_document = driver.create(json_document)

new_document.add({"new_val1": 15, "new_val2": 10})
print(new_document)

