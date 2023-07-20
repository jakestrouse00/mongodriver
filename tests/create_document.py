from mongodriver.src.mongodriver import Driver

driver = Driver(
        connection_url="mongodb+srv://example:SecurePassword@testcluster.e2lhq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
        db_name="example_db", collection_name="example_collection")

json_document = {"foo": 1, "bar": 2}
new_document = driver.create(json_document)

# print the value of "foo"
print(new_document.foo)  # 1

# change the value of "foo"
new_document.foo = 2
print(new_document.foo)  # 2

