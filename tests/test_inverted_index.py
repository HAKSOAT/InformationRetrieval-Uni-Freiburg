from unittest.mock import patch

import pytest

from ir.inverted_index import InvertedIndex


class TestInvertedIndex:
    @patch('ir.inverted_index.InvertedIndex.fetch_documents')
    def test_populate_index(self, fetch_documents_patch):
        fetch_documents_patch.return_value = ['first first document', 'second document document',
                                              'third document document third']
        inverted_index = InvertedIndex()
        documents = inverted_index.fetch_documents('testing')
        inverted_index.populate_inverted_list(documents)
        assert inverted_index.inverted_list == {'first': [1], 'document': [1, 2, 3], 'second': [2], 'third': [3]}

    @patch('ir.inverted_index.InvertedIndex.fetch_documents')
    def test_intersection(self, fetch_documents_patch):
        fetch_documents_patch.return_value = ['first document', 'second document', 'third document',
                                              'first second third document']
        inverted_index = InvertedIndex()
        documents = inverted_index.fetch_documents('testing')
        inverted_index.populate_inverted_list(documents)
        intersection = inverted_index.intersect('document', 'third')
        assert intersection == [3, 4]
        intersection = inverted_index.intersect('document', 'first')
        assert intersection == [1, 4]
        intersection = inverted_index.intersect('document', 'none')
        assert intersection == []

    @patch('ir.inverted_index.InvertedIndex.fetch_documents')
    def test_query_and(self, fetch_documents_patch):
        fetch_documents_patch.return_value = ['first document', 'second document', 'third document',
                                              'first second third document']
        inverted_index = InvertedIndex()
        documents = inverted_index.fetch_documents('testing')
        inverted_index.populate_inverted_list(documents)
        result = inverted_index.apply_and_boolean('second document')
        assert result == [2, 4]
        result = inverted_index.apply_and_boolean('document first')
        assert result == [1, 4]
        result = inverted_index.apply_and_boolean('document')
        assert result == [1, 2, 3, 4]
        result = inverted_index.apply_and_boolean('none')
        assert result == []


