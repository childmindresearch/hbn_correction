[![DOI](https://zenodo.org/badge/657341621.svg)](https://zenodo.org/doi/10.5281/zenodo.10383685)

# HBN Correction

[![Build](https://github.com/childmindresearch/hbn_correction/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/childmindresearch/hbn_correction/actions/workflows/test.yaml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/childmindresearch/hbn_correction/branch/main/graph/badge.svg?token=22HWWFWPW5)](https://codecov.io/gh/childmindresearch/hbn_correction)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![stability-stable](https://img.shields.io/badge/stability-stable-green.svg)
[![pages](https://img.shields.io/badge/api-docs-blue)](https://childmindresearch.github.io/hbn_correction)

# Installation 
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
