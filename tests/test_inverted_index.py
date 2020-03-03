from unittest.mock import patch
from math import inf

import pytest

from ir.inverted_index import InvertedIndex


class TestInvertedIndex:
    @patch('ir.inverted_index.InvertedIndex.fetch_documents')
    def test_populate_index(self, fetch_documents_patch):
        fetch_documents_patch.return_value = ['first first document', 'second document document',
                                              'third document document third']
        inverted_index = InvertedIndex()
        documents = inverted_index.fetch_documents('testing')
        inverted_index.populate_inverted_list(documents, bm25=False, position=False)
        assert inverted_index.inverted_list == {'first': [[1, 2]], 'document': [[1,1], [2, 2], [3, 2]],
                                                'second': [[2, 1]], 'third': [[3, 2]]}

    @patch('ir.inverted_index.InvertedIndex.fetch_documents')
    def test_bm25_k_at_infinity(self, fetch_documents_patch):
        fetch_documents_patch.return_value = ['Movie 1 Animated movie.', 'Movie 2 Non-animated film.',
                                              'Movie 3 Short animation.', 'Movie 4 Short animated short film']
        inverted_index = InvertedIndex()
        documents = inverted_index.fetch_documents('testing')
        inverted_index.populate_inverted_list(documents, inf, 0, position=False)
        result = inverted_index.inverted_list
        expected_result = {
            'animated': [[1, 0.415], [2, 0.415], [4, 0.415]],
            'animation': [[3, 2.0]],
            'film': [[2, 1.0], [4, 1.0]],
            'movie': [[1, 0.0], [2, 0.0], [3, 0.0], [4, 0.0]],
            'non': [[2, 2.0]],
            'short': [[3, 1.0], [4, 2.0]]
        }
        assert result == expected_result

    @patch('ir.inverted_index.InvertedIndex.fetch_documents')
    def test_bm25_k_b_at_defaults(self, fetch_documents_patch):
        fetch_documents_patch.return_value = ['Movie 1 Animated movie.', 'Movie 2 Non-animated film.',
                                              'Movie 3 Short animation.', 'Movie 4 Short animated short film']
        inverted_index = InvertedIndex()
        documents = inverted_index.fetch_documents('testing')
        inverted_index.populate_inverted_list(documents, position=False)
        result = inverted_index.inverted_list
        expected_result = {
            'movie': [[1, 0.0], [2, 0.0], [3, 0.0], [4, 0.0]],
            'animated': [[1, 0.459], [2, 0.402], [4, 0.358]],
            'non': [[2, 1.938]], 'film': [[2, 0.969], [4, 0.863]],
            'short': [[3, 1.106], [4, 1.313]],
            'animation': [[3, 2.211]]
        }
        assert result == expected_result

    @patch('ir.inverted_index.InvertedIndex.fetch_documents')
    def test_merge(self, fetch_documents_patch):
        fetch_documents_patch.return_value = []
        inverted_index = InvertedIndex()
        inverted_index.fetch_documents('testing')
        postings_one = [[1, 2.1], [5, 3.2]]
        postings_two = [[1, 1.7], [2, 1.3], [5, 3.3]]
        result = inverted_index.merge(postings_one, postings_two)
        expected_result = [[1, 3.8], [2, 1.3], [5, 6.5]]
        assert result == expected_result


