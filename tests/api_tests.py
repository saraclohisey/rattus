import unittest
from unittest.mock import patch, MagicMock
from api import EnsemblAPI

class TestEnsemblAPI(unittest.TestCase):
    def setUp(self):
        self.api = EnsemblAPI()

    @patch('api.requests.Session.get')
    def test_fetch_data_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': 'test_data'}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = self.api.fetch_data('gene_symbol')
        self.assertEqual(result, {'data': 'test_data'})

    @patch('api.requests.Session.get')
    def test_fetch_data_failure(self, mock_get):
        mock_get.side_effect = Exception("Test exception")

        with patch('api.EnsemblAPI.handle_error') as mock_handle_error:
            result = self.api.fetch_data('gene_symbol')
            self.assertIsNone(result)
            mock_handle_error.assert_called()

    @patch('api.logging')
    def test_handle_error_http_error(self, mock_logging):
        mock_exception = MagicMock()
        mock_exception.response.status_code = 500
        mock_exception.response.text = "Server Error"
        self.api.handle_error(mock_exception, 0, 3, 'gene_symbol', 2)
        mock_logging.error.assert_called()

    @patch('api.EnsemblAPI.fetch_data')
    def test_get_human_ortholog_success(self, mock_fetch_data):
        mock_fetch_data.return_value = {
            'data': [{
                'homologies': [{
                    'target': {
                        'id': 'human_gene',
                        'species': 'homo_sapiens',
                        'perc_id': 98.76,
                        'perc_pos': 99.99
                    },
                    'type': 'ortholog_one2one'
                }]
            }]
        }

        result, error = self.api.get_human_ortholog('gene_symbol')
        self.assertFalse(error)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['gene_symbol'], 'human_gene')

    @patch('api.EnsemblAPI.fetch_data')
    def test_get_human_ortholog_failure(self, mock_fetch_data):
        mock_fetch_data.return_value = None

        result, error = self.api.get_human_ortholog('gene_symbol')
        self.assertTrue(error)
        self.assertEqual(result[0]['gene_symbol'], 'error - retries exceeded')

if __name__ == '__main__':
    unittest.main()