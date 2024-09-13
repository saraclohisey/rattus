# Rat-Human ortholog command line interface 

This repository contains a command line interface designed to map rat genes to their human orthologs.

The program is written in python and uses the Ensembl API.

## Prerequisites

Before running the script, install the dependencies:

```
pip install -r requirements.txt
```

## Installation

Clone this repository to your local machine.

## Use

1. Open a terminal and navigate to the directory where the script is located. 
2. Run the script using the following command:

   ```shell
   python cli.py <input csv> <output csv> 
   ```

   Flags:

    input_file_path

    output_file_path

    --overwrite   option to overwrite existing output csv

    --ensembl_id  option to provide a single murine ensembl identifier to the cli 

The input csv must have a single column headed `Rat Gene`. Only Ensembl identifiers are valid (e.g., ENSMUSG00000111497).

## Output

The program returns a csv file with four columns:

   - Murine Ensembl identifiers
   - Human Ensembl identifiers
   - Identitiy (the percentage of identical sites (amino acids or nucleotides) between two sequences in the alignment)
   - Positivity (the percentage of positions in an alignment which are either exact matches or are occupied by biochemically similar nucleotides)
