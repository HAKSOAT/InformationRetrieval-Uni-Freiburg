import re
from functools import reduce
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
                    if self.inverted_list[word][-1] == document_id:
                        pass
                    else:
                        self.inverted_list[word].append(document_id)
                except KeyError:
                    self.inverted_list[word] = [document_id]

    def intersect(self, term_one, term_two):
        intersection = []
        try:
            if isinstance(term_one, list):
                term_one_postings_list = term_one
            else:
                term_one_postings_list = self.inverted_list[term_one.lower()]

            if isinstance(term_two, list):
                term_two_postings_list = term_two
            else:
                term_two_postings_list = self.inverted_list[term_two.lower()]
        except KeyError:
            return intersection

        index_one = 0
        index_two = 0

        while index_one < len(term_one_postings_list) and index_two < len(term_two_postings_list):
            if term_one_postings_list[index_one] == term_two_postings_list[index_two]:
                intersection.append(term_one_postings_list[index_one])
                index_one += 1
                index_two += 1
            elif term_one_postings_list[index_one] < term_two_postings_list[index_two]:
                index_one += 1
            else:
                index_two += 1

        return intersection

    def apply_and_boolean(self, query, number_of_matches=None):
        terms = query.split()
        if len(terms) == 0:
            results = []
        elif len(terms) == 1:
            results = self.inverted_list.get(terms[0], [])
        else:
            results = reduce(self.intersect, terms)

        if number_of_matches:
            x_results = results[:number_of_matches]
            return x_results

        return results


def run_search_engine(number_of_matches):
    collection_file_name = sys.argv[1]
    inverted_index = InvertedIndex()
    documents = inverted_index.fetch_documents(collection_file_name)
    print("Please wait while the documents get indexed...")
    inverted_index.populate_inverted_list(documents)
    print("Done")
    while True:
        query = input('Enter query:\t')
        results = inverted_index.apply_and_boolean(query, number_of_matches)
        print(f'{len(results)} matching records:')
        for result in results:
            print(f'Doc id: {result}')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python inverted_index.py <filename>')
        sys.exit(1)
    else:
        number_of_matches = int(input('You want to get how many matching records: '))
        run_search_engine(number_of_matches)
