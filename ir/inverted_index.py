from math import log, isnan
import re
from functools import reduce, partial
import sys


class InvertedIndex:
    def __init__(self):
        self.inverted_list = {}
        self.document_lengths = {}
        self.average_document_length = 0

    def fetch_documents(self, file_name):
        with open(file_name) as collection:
            documents = collection.readlines()
        return documents

    def populate_inverted_list(self, documents, k=1.75, b=0.75, bm25=True, position=True):
        document_id = 0
        for document in documents:
            document_id += 1
            words = re.findall(r'[A-Za-z]+', document.lower())
            self.document_lengths[document_id] = len(words)
            for word in words:
                try:
                    last_document_id = self.inverted_list[word][-1][0]
                    last_document_term_frequency = self.inverted_list[word][-1][1]
                    if last_document_id == document_id:
                        self.inverted_list[word][-1] = [last_document_id, last_document_term_frequency+1]
                    else:
                        self.inverted_list[word].append([document_id, 1])
                except KeyError:
                    self.inverted_list[word] = [[document_id, 1]]
        document_lengths = self.document_lengths.values()
        self.average_document_length = round(sum(document_lengths) / len(document_lengths), 5)

        if bm25:
            # Calculate BM25 value for every posting and replace term frequency with it
            words = self.inverted_list.keys()
            for word in words:
                postings = self.inverted_list[word]
                for index, posting in enumerate(postings):
                    bm25 = self.calculate_bm25(document_id, len(postings), posting[1], k, b,
                                               self.document_lengths[posting[0]], self.average_document_length)
                    if position:
                        position_ranking = (document_id - (posting[0] - 1))/document_id
                        bm25_position_influence = round(bm25 * position_ranking, 3)
                        postings[index] = [posting[0], bm25_position_influence]
                    else:
                        postings[index] = [posting[0], bm25]
                self.inverted_list[word] = postings

    def calculate_bm25(self, n, df, tf, k, b, dl, avdl):
        """ Calculate the BM25 value of a word in a collection or corpus rounded to 3 dp.
            This is done using the formula:

            bm25 = tf_extra * log(n/df)

            tf_extra = tf * ((k + 1)/(k * (1 - b + b * (dl/avdl)) + tf ))

            The log value is to base 2

            :returns bm25
        """
        alpha = (1 - b) + b * (dl / avdl)
        tf_extra = tf * ((k + 1) / (k * alpha + tf))
        tf_extra = tf if isnan(tf_extra) else tf_extra
        bm25 = tf_extra * log(n/df, 2)

        return round(bm25, 3) if bm25 > 0 else 0.0

    def intersect(self, term_one, term_two):
        """
        Intersects two postings list, adding their ranking values at intersections.
        """
        combination = []
        postings_one = self.fetch_postings(term_one)
        postings_two = self.fetch_postings(term_two)

        index_one = 0
        index_two = 0

        while index_one < len(postings_one) and index_two < len(postings_two):
            bm25_one = postings_one[index_one][1]
            bm25_two = postings_two[index_two][1]

            if postings_one[index_one][0] == postings_two[index_two][0]:
                combination.append([postings_one[index_one][0], round(bm25_one + bm25_two, 3)])
                index_one += 1
                index_two += 1
            elif postings_one[index_one][0] < postings_two[index_two][0]:
                index_one += 1
            else:
                index_two += 1

        return combination

    def merge(self, term_one, term_two):
        """
        Merges two postings list, adding their ranking values at intersections
        """
        combination = []
        postings_one = self.fetch_postings(term_one)
        postings_two = self.fetch_postings(term_two)

        index_one = 0
        index_two = 0

        while index_one < len(postings_one) and index_two < len(postings_two):
            bm25_one = postings_one[index_one][1]
            bm25_two = postings_two[index_two][1]

            if postings_one[index_one][0] == postings_two[index_two][0]:
                combination.append([postings_one[index_one][0], round(bm25_one + bm25_two, 3)])
                index_one += 1
                index_two += 1
            elif postings_one[index_one][0] < postings_two[index_two][0]:
                combination.append([postings_one[index_one][0], bm25_one])
                index_one += 1
                if not index_one < len(postings_one):
                    for posting in postings_two[index_two:]:
                        combination.append([posting[0], posting[1]])
            else:
                combination.append([postings_two[index_two][0], bm25_two])
                index_two += 1
                if not index_two < len(postings_two):
                    for posting in postings_one[index_one:]:
                        combination.append([posting[0], posting[1]])

        return combination

    def fetch_postings(self, term):
        if isinstance(term, list):
            postings = term
        else:
            postings = self.inverted_list.get(term.lower(), [])
        return postings

    def apply_query(self, query, is_intersect=False):
        terms = query.split()
        if len(terms) == 0:
            sorted_results = []
        elif len(terms) == 1:
            results = self.inverted_list.get(terms[0], [])
            sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
        else:
            if is_intersect:
                results = reduce(self.intersect, terms)
            else:
                results = reduce(self.merge, terms)
            sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
        return sorted_results

    def fetch_top_x_results(self, results, x=None):
        if x:
            x_results = results[:x]
            return x_results
        else:
            return results


def run_search_engine():
    collection_file_name = sys.argv[1]
    inverted_index = InvertedIndex()
    documents = inverted_index.fetch_documents(collection_file_name)
    print("Please wait while the documents get indexed...")
    inverted_index.populate_inverted_list(documents, k=1.75, b=0.1, position=True)
    print("Done")
    while True:
        number_top_records = int(input('You want to get how many top matching records: '))
        query = input('Enter query:\t')
        results = inverted_index.apply_query(query, is_intersect=False)
        top_x_results = inverted_index.fetch_top_x_results(results, number_top_records)
        print(f'{len(top_x_results)} matching records:')
        for result in top_x_results:
            print(f'Doc id: {result}')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python inverted_index.py <filename>')
        sys.exit(1)
    else:
        run_search_engine()
