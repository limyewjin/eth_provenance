import uuid

class DataStore:
    def __init__(self):
        self.store = {}

    async def upsert(self, documents):
        ids = []
        for doc in documents:
            doc_id = str(uuid.uuid4())
            self.store[doc_id] = doc
            ids.append(doc_id)
        return ids
