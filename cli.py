import argparse
import os
import logging
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from api import EnsemblAPI
from file_processing import process_csv

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    parser = argparse.ArgumentParser(description='Find human orthologs for rat genes from a CSV file or a single Ensembl identifier and output the results to another CSV file.')
    parser.add_argument('input_file_path', type=str, help='Path to the input CSV file containing rat gene symbols.', nargs='?')
    parser.add_argument('output_file_path', type=str, help='Path to the output CSV file to save the results.', nargs='?')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite the output file if it exists.')
    parser.add_argument('--ensembl_id', type=str, help='A single Ensembl identifier to process.', default=None)

    args = parser.parse_args()

    api = EnsemblAPI()

    if args.ensembl_id:
        logging.info(f"Processing single Ensembl identifier: {args.ensembl_id}")
        human_orthologs, error = api.get_human_ortholog(args.ensembl_id)
        if not error:
            for ortholog in human_orthologs:
                print(f"Rat Gene: {ortholog['Rat_gene']}, Human Ortholog Gene Symbol: {ortholog['gene_symbol']}, Type: {ortholog['type']}, Identity (%): {ortholog['identity']}, Positivity (%): {ortholog['positivity']}")
        else:
            logging.error("Error processing the Ensembl identifier.")
    else:
        if not args.input_file_path or not args.output_file_path:
            logging.error("Input and output file paths are required when not using --ensembl_id.")
            sys.exit(1)

        if not os.path.exists(args.input_file_path):
            logging.error(f"Input file does not exist: {args.input_file_path}")
            sys.exit(1)

        if os.path.exists(args.output_file_path) and not args.overwrite:
            logging.error(f"Output file already exists: {args.output_file_path}. Use --overwrite to overwrite it.")
            sys.exit(1)

        not_found_count, error_count = process_csv(args.input_file_path, args.output_file_path, api)
        logging.info(f"Process completed. Orthologs not found or errors encountered for {not_found_count} genes. Total errors: {error_count}")

if __name__ == "__main__":
    main()
