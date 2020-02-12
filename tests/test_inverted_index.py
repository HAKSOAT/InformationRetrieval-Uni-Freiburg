from unittest.mock import patch

import pytest

from ir.inverted_index import InvertedIndex


class TestInvertedIndex:
    @patch('ir.inverted_index.InvertedIndex.fetch_documents')
    def test_populate_index(self, fetch_documents_patch):
        fetch_documents_patch.return_value = ['first document', 'second document', 'third document']
        inverted_index = InvertedIndex()
        documents = inverted_index.fetch_documents('testing')
        inverted_index.populate_inverted_list(documents)
        assert inverted_index.inverted_list == {'first': [1], 'document': [1, 2, 3], 'second': [2], 'third': [3]}
