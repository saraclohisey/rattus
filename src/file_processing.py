import csv
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from api import EnsemblAPI

def validate_input_file(input_file_path):
    """
    Validates the input CSV file to ensure it contains the required 'Pig Gene' column,
    is not empty, and follows the correct format.

    Parameters:
    - input_file_path (str): The file path for the input CSV file.

    Raises:
    - ValueError: If the file is empty, does not contain the required column, or is improperly formatted.
    """
    try:
        with open(input_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader, None)  
            if not headers:
                raise ValueError("The input CSV file is empty.")
            if 'Pig Gene' not in headers:
                raise ValueError("The input CSV file must contain a column named 'Pig Gene'.")
    except csv.Error as e:
        raise ValueError(f"CSV format error: {e}")

def process_csv(input_file_path, output_file_path, api):
    """
    Processes a CSV file containing Pig Genes to find their human orthologs and writes the results to another CSV file.
    
    Parameters:
    - input_file_path (str): The file path for the input CSV file containing Pig Gene symbols.
    - output_file_path (str): The file path for the output CSV file where results will be saved.
    - api (EnsemblAPI): An instance of the EnsemblAPI class used to query the Ensembl database.

    Returns:
    - tuple: A tuple containing two integers:
        1. The count of Pig Genes for which no human orthologs were found.
        2. The count of Pig Genes for which errors occurred during processing.

    The input CSV file must contain a column named 'Pig Gene'. The output CSV file will contain columns for
    'Pig Gene', 'Human Ortholog Gene Symbol', 'Type', 'Identity (%)', and 'Positivity (%)'.

    The function uss a ThreadPoolExecutor to process gene queries in parallel, improving performance for
    large datasets. 
    """
    validate_input_file(input_file_path)
    
    not_found_count = 0
    error_count = 0

    with open(input_file_path, mode='r', newline='', encoding='utf-8') as csvfile, \
         open(output_file_path, mode='w', newline='', encoding='utf-8') as outfile:
        gene_reader = csv.DictReader(csvfile)
        
        if 'Pig Gene' not in gene_reader.fieldnames:
            logging.error("The input CSV file must contain a column named 'Pig Gene'.")
            sys.exit(1)
        
        fieldnames = ['Pig Gene', 'Human Ortholog Gene Symbol', 'Type', 'Identity (%)', 'Positivity (%)']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        pig_genes = [row['Pig Gene'] for row in gene_reader]

        def process_gene(pig_gene):
            human_orthologs, error = api.get_human_ortholog(pig_gene)
            results = []
            for ortholog in human_orthologs:
                results.append({
                    'Pig Gene': ortholog['pig_gene'], 
                    'Human Ortholog Gene Symbol': ortholog['gene_symbol'], 
                    'Type': ortholog['type'], 
                    'Identity (%)': ortholog['identity'], 
                    'Positivity (%)': ortholog['positivity']
                })
                if ortholog['gene_symbol'] == 'not found' or ortholog['gene_symbol'].startswith('error'):
                    nonlocal not_found_count
                    nonlocal error_count
                    not_found_count += 1
                    if error:
                        error_count += 1
            return results

        # Use ThreadPoolExecutor to process genes in parallel
        with ThreadPoolExecutor(max_workers=10) as executor, tqdm(total=len(pig_genes)) as progress:
            future_to_gene = {executor.submit(process_gene, gene): gene for gene in pig_genes}
            for future in as_completed(future_to_gene):
                gene = future_to_gene[future]
                try:
                    results = future.result()
                    for result in results:
                        writer.writerow(result)
                    progress.update(1)
                except Exception as exc:
                    logging.error(f'Gene {gene} generated an exception: {exc}')
                    progress.update(1)

    return not_found_count, error_count
