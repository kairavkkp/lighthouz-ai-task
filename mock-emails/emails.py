from langchain_community.document_loaders import UnstructuredEmailLoader

loader = UnstructuredEmailLoader("test.eml")

data = loader.load()

print(data)
