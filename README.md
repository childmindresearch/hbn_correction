[![DOI](https://zenodo.org/badge/657341621.svg)](https://zenodo.org/doi/10.5281/zenodo.10383685)

# HBN Correction

## Installation 
Install this package via:
```sh
pip install git+https://github.com/childmindresearch/hbn_correction.git
```

## Quick start
```sh
from hbn_correction.datacorrection import DataCorrection
corrected_data = DataCorrection().run(hbn_data_path = "./data.csv")
```
[Notebook Example](https://github.com/childmindresearch/hbn_correction/blob/main/examples/run_data_correction.ipynb)
