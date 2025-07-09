# make-data-count-kaggle
Kaggle competition for Make Data Count

## PHP

## Python

```
python3 -m venv .venv 
source .venv/bin/activate
```

## Examples

### Citation in references without URL or DOI

10.1002/anie.202005531 is provided as BioC(!) but one can get original XML from Wiley. Note that it cites primary data:

> Deposition Numbers 1993042 (for 1a), and 1993043 (for 7m) contain the supplementary crystallographic data for this paper. These data are provided free of charge by the joint Cambridge Crystallographic Data Centre and Fachinformationszentrum Karlsruhe Access Structures service www.ccdc.cam.ac.uk/structures

No individual URLs, the data can be viewed at https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid=1993042&DatabaseToSearch=Published (10.5517/ccdc.csd.cc24wxpn) and https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid=1993043&DatabaseToSearch=Published (10.5517/ccdc.csd.cc24wxqp)

But not that XML does have a search link to the CCDC that uses the paper DOI.

### Things that training data says are data but which aren’t

#### EPI

10.1128_JVI.01717-21
- EPI_ISL_291131 is a virus strain

#### 10.3390_s19030479

Training says https://doi.org/10.4231/r7rx991c but this isn’t in text, however papers cites https://purr.purdue.edu/publications/1947/1 which has that DOI(!)

#### 10.1186_s13071-018-2842-4

Training says https://doi.org/10.17638/datacat.liverpool.ac.uk/417 but in text is URL http://datacat.liverpool.ac.uk/id/eprint/434.

#### 10.1002_cssc.202201821

We have PDF and XML but this paper is not in the training dataset `train_labels.csv`.

#### 10.1021_acs.jcim.9b01185

BioRxiv preprint, no data DOI

#### 10.1029_2021gl096173

Dryad as stash not DOI https://datadryad.org/stash/share/ exYZnfhUnvOFfjOvnMV4os7WO4ErfrGhwxFBAR-jUZA

#### 10.1029_2022gl100473

Zenodo as records not DOIs

#### 10.1038_s41467-019-10357-z

> The X-ray crystallographic coordinates for structures reported in this study have been deposited at the Cambridge Crystallographic Data Center (CCDC), under deposition numbers 1878657-1878660.

#### 10.1038_s41467-019-10357-z

preprint

#### 10.1080_21645515.2023.2189598

PDF is supplementary figures, not actual paper (FFS).

#### 10.1111_1365-2656.12594

PDF is actually for 10.1111/ecog.04716 whcih has data in Dryad. the actual paper https://doi.org/10.1111/1365-2656.12594 has data with the DOI given in the training data.

#### 10.1128_JVI.01717-21

Is `EPI_ISL_376123` in `EPI_ISL_376123_A/Jiangsu/1/2018(H7N4)` an identifier?


   

