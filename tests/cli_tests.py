import unittest
from unittest.mock import patch, mock_open
import cli

class TestCLI(unittest.TestCase):
    @patch('cli.EnsemblAPI')
    @patch('cli.process_csv')
    @patch('cli.os.path.exists')
    @patch('cli.argparse.ArgumentParser.parse_args')
    def test_main_with_ensembl_id(self, mock_args, mock_exists, mock_process_csv, mock_api):
        mock_args.return_value = argparse.Namespace(ensembl_id='ENSMUSG00000000001', input_file_path=None, output_file_path=None, overwrite=False)
        mock_api_instance = mock_api.return_value
        mock_api_instance.get_human_ortholog.return_value = ([{'mouse_gene': 'Gene1', 'gene_symbol': 'HumanGene1', 'type': 'ortholog_one2one', 'identity': 98.7, 'positivity': 99.2}], None)
        
        with self.assertLogs(level='INFO') as log:
            cli.main()
            self.assertIn("Processing single Ensembl identifier: ENSMUSG00000000001", log.output[0])

    @patch('cli.os.path.exists')
    @patch('cli.argparse.ArgumentParser.parse_args')
    def test_main_with_input_output_files(self, mock_args, mock_exists):
        mock_args.return_value = argparse.Namespace(ensembl_id=None, input_file_path='mouse_genes.csv', output_file_path='human_orthologs.csv', overwrite=False)
        mock_exists.side_effect = [True, False]  # First call (input file) exists, second call (output file) does not exist
        
        with patch('builtins.open', mock_open()) as mocked_file:
            with self.assertLogs(level='INFO') as log:
                cli.main()
                self.assertIn("Process completed.", log.output[0])

    @patch('cli.sys.exit')
    @patch('cli.os.path.exists')
    @patch('cli.argparse.ArgumentParser.parse_args')
    def test_main_missing_input_output_paths(self, mock_args, mock_exists, mock_exit):
        mock_args.return_value = argparse.Namespace(ensembl_id=None, input_file_path=None, output_file_path=None, overwrite=False)
        mock_exists.return_value = False  # Simulate missing files
        
        cli.main()
        mock_exit.assert_called_once_with(1)

if __name__ == '__main__':
    unittest.main()