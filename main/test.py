import uuid

# Random UUID (most common)
random_id = uuid.uuid4()
print("Random UUID:", random_id)

# Time-based UUID
time_id = uuid.uuid1()
print("Time-based UUID:", time_id)

# Namespace-based UUID (MD5)
name_id = uuid.uuid3(uuid.NAMESPACE_DNS, 'example.com')
print("UUID3:", name_id)

# Namespace-based UUID (SHA-1)
name_id_sha = uuid.uuid5(uuid.NAMESPACE_DNS, 'example.com')
print("UUID5:", name_id_sha)