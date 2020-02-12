import re
import sys


class InvertedIndex:
    def __init__(self):
        self.inverted_list = {}

    def fetch_documents(self, file_name):
        with open(file_name) as collection:
            documents = collection.readlines()
        return documents

    def populate_inverted_list(self, documents):
        document_id = 0
        for document in documents:
            document_id += 1
            words = re.findall(r'[A-Za-z]+', document.lower())
            for word in words:
                try:
                    self.inverted_list[word].append(document_id)
                except KeyError:
                    self.inverted_list[word] = [document_id]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python inverted_index.py <filename>')
        sys.exit(1)
    else:
        collection_file_name = sys.argv[1]
        inverted_index = InvertedIndex()
        documents = inverted_index.fetch_documents(collection_file_name)
        inverted_index.populate_inverted_list(documents)
        for word, postings_list in inverted_index.inverted_list.items():
            print(f'Word: {word}\tDocument frequency: {len(postings_list)}')
