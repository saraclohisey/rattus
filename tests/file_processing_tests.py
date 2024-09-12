import unittest
from unittest.mock import patch, mock_open, MagicMock
from file_processing import validate_input_file, process_csv

class TestFileProcessing(unittest.TestCase):
    def test_validate_input_file_valid(self):
        """Test validate_input_file with a valid CSV file."""
        mock_file_content = "Mouse Gene\nGene1"
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            # No exception should be raised for a valid file
            validate_input_file("dummy_path.csv")

    def test_validate_input_file_empty(self):
        """Test validate_input_file with an empty CSV file."""
        mock_file_content = ""
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            with self.assertRaises(ValueError) as context:
                validate_input_file("dummy_path.csv")
            self.assertTrue("The input CSV file is empty." in str(context.exception))

    def test_validate_input_file_missing_column(self):
        """Test validate_input_file with a missing 'Mouse Gene' column."""
        mock_file_content = "Wrong Header\nValue"
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            with self.assertRaises(ValueError) as context:
                validate_input_file("dummy_path.csv")
            self.assertTrue("The input CSV file must contain a column named 'Mouse Gene'." in str(context.exception))

    @patch('file_processing.EnsemblAPI')
    @patch('file_processing.csv.DictWriter')
    @patch('file_processing.csv.DictReader')
    @patch("builtins.open", new_callable=mock_open, read_data="Mouse Gene\nGene1")
    def test_process_csv(self, mock_open, mock_dict_reader, mock_dict_writer, mock_api):
        """Test process_csv with a mock API and CSV files."""
        mock_api_instance = MagicMock()
        mock_api.return_value = mock_api_instance
        mock_api_instance.get_human_ortholog.return_value = ([{'mouse_gene': 'Gene1', 'gene_symbol': 'HumanGene1', 'type': 'ortholog', 'identity': 98, 'positivity': 95}], False)

        # Mocking the reader to return a specific row
        mock_dict_reader.return_value = [{'Mouse Gene': 'Gene1'}]
        mock_dict_reader.fieldnames = ['Mouse Gene']

        process_csv("input.csv", "output.csv", mock_api_instance)

        # Assert the API was called with the correct gene
        mock_api_instance.get_human_ortholog.assert_called_with('Gene1')

        # Assert the writer was used to write the correct row
        mock_dict_writer.return_value.writerow.assert_called_with({'Mouse Gene': 'Gene1', 'Human Ortholog Gene Symbol': 'HumanGene1', 'Type': 'ortholog', 'Identity (%)': 98, 'Positivity (%)': 95})

if __name__ == '__main__':
    unittest.main()