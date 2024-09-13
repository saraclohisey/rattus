import requests
import logging
import math
import time
import random
import traceback
from requests.exceptions import RequestException

class EnsemblAPI:
    def __init__(self):
        self.session = requests.Session()
        self.server = "https://rest.ensembl.org"
        self.session.headers.update({'Content-Type': 'application/json'})

    def fetch_data(self, rat_gene, retries=3, delay=2):
        """
        Fetches data from the Ensembl API for a given rat gene with retries and exponential backoff.

        Parameters:
        - rat_gene (str): The rat gene symbol for which to fetch homology information.
        - retries (int): The maximum number of attempts to make (default is 3).
        - delay (int): The initial delay in seconds before the first retry. Subsequent retries will double this delay (default is 2).

        Returns:
        - dict: A dictionary containing the JSON response from the API if the request is successful.
        - None: If all attempts fail, the method returns None to indicate failure.

        Raises:
        - requests.HTTPError: If the response status code indicates an HTTP error (other than a 400 Bad Request, which is logged as a warning).
        - RequestException: For issues like network problems, or timeout errors.
        - Exception: For any unexpected errors encountered during the request process.
        """
        ext = f"/homology/symbol/rattus_norvegicus/{rat_gene}?content-type=application/json"
        for attempt in range(retries):
            try:
                response = self.session.get(self.server + ext)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                self.handle_error(e, attempt, retries, rat_gene, delay)
                if attempt == retries - 1:
                    return None

    def handle_error(self, e, attempt, retries, rat_gene, delay):
        """
        Handles errors encountered during API requests, logging appropriate messages and implementing exponential backoff.

        Parameters:
        - e (Exception): The exception that was caught.
        - attempt (int): The current attempt number (0-indexed).
        - retries (int): The total number of retries allowed.
        - rat_gene (str): The rat gene symbol that was being queried when the error occurred.
        - delay (int): The initial delay in seconds before the first retry. Subsequent retries will double this delay.

        The method uses an exponential backoff strategy for the delay between retries, multiplying the initial delay by
        2 raised to the power of the attempt number. It also applies a random jitter between 0.8 and 1.2 to the calculated
        delay to prevent thundering herd problems.
        """
        if isinstance(e, requests.HTTPError):
            if e.response.status_code == 400:
                logging.warning(f"Bad request for gene {rat_gene}. Attempt {attempt + 1} of {retries}. Error: {e.response.text}")
            else:
                logging.error(f"HTTP error for gene {rat_gene}: {e.response.text}. Status Code: {e.response.status_code}")
        elif isinstance(e, RequestException):
            logging.exception(f"Request exception for gene {rat_gene}: {e}")
        else:
            logging.critical(f"Unexpected error for gene {rat_gene}: {traceback.format_exc()}")

        sleep_time = delay * math.pow(2, attempt) * random.uniform(0.8, 1.2)
        logging.info(f"Retrying in {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)

    def get_human_ortholog(self, rat_gene, retries=3, delay=2):
        """
        Retrieves the human ortholog for a specified rat gene symbol.

        Parameters:
        - rat_gene (str): The rat gene symbol for which to find the human ortholog.
        - retries (int): The maximum number of retry attempts for the API request (default is 3).
        - delay (int): The initial delay in seconds before the first retry, with subsequent retries
            following an exponential backoff strategy (default is 2).

        Returns:
        - tuple: A tuple containing two elements:
            1. A list of dictionaries, each representing a human ortholog found. Each dictionary
           contains keys for 'rat_gene', 'gene_symbol', 'type', 'identity', and 'positivity'.
           In case of failure, the list contains a single dictionary with an error message.
            2. A boolean flag indicating whether an error occurred (True if error, False otherwise).
        """
        data = self.fetch_data(rat_gene, retries, delay)
        if data:
            return self.process_response(data, rat_gene), False
        else:
            return [{'rat_gene': rat_gene, 'gene_symbol': 'error - retries exceeded', 'type': '', 'identity': '', 'positivity': ''}], True
        
    @staticmethod
    def process_response(data, rat_gene):
        """
        Processes the API response to extract human ortholog information for a rat gene.

        Parameters:
        - data (dict): The JSON response data from the Ensembl REST API.
        - rat_gene (str): The rat gene symbol that was queried.

        Returns:
        - list: A list of dictionaries, where each dictionary contains information about a human ortholog. If no
            human orthologs are found, returns a list with a single dictionary indicating that the gene was not found.

        Each dictionary in the returned list has the following keys:
        - 'rat_gene': The queried rat gene symbol.
        - 'gene_symbol': The human gene symbol of the ortholog.
        - 'type': The type of homology.
        - 'identity': is the percentage of identical sites (amino acids or nucleotides) between two sequences in the alignment.
        - 'positivity': is the percentage of positions in an alignment which are either exact matches or are occupied by biochemically similar nucleotides.
        """
        human_orthologs = []
        if data and data['data'][0]['homologies']:
            human_orthologs = [
                {
                    'rat_gene': rat_gene,
                    'gene_symbol': homology['target']['id'],
                    'type': homology['type'],
                    'identity': homology['target']['perc_id'],
                    'positivity': homology['target']['perc_pos']
                } for homology in data['data'][0]['homologies'] if homology['target']['species'] == 'homo_sapiens'
            ]

        if not human_orthologs:
            human_orthologs.append({
                'rat_gene': rat_gene,
                'gene_symbol': 'not found',
                'type': '',
                'identity': '',
                'positivity': ''
            })
        return human_orthologs
