# Kaggle

Known XML issues

## 10.1016_j.ast.2022.107401

The cranfield DOI is split up: `https://doi .org/10 .17862/cranfield .rd .19146182 .v1`

## 10.1016_j.ecolind.2021.107934 

https://doi.org/10.6073/pasta/be42bb841e696b7bca**-**d9957aed33db5e has a hyphen in the middle, which breaks matching the actual DOI

https://doi.org/10.6096/ctoh_seaice_2019_12 is in JSON but not extracted! (bad lacement of check for acknowledgements before looking at DOis)

## 10.3133_ofr20201035

Don’t think ther eis any way to tell that these are primary 9if, indeed, they are…)

## 10.3133_cir1497

Some DOIs seem to be missing from XML, e.g. https://doi.org/10.5066/p9z04lnk, this is a big PDF and maybe GROBID just failed… 

## 10.1186_s12881-019-0773-3

Gene interaction BDNF_rs7103411%2DBDNF_rs1491851%2DSLC6A3_rs40184 https://bmcmedgenet.biomedcentral.com/articles/10.1186/s12881-019-0773-3#:~:text=BDNF_rs7103411%2DBDNF_rs1491851%2DSLC6A3_rs40184 get’s treated as two SNPs, which is incorrect.

## 10.1039_d0sc01197e

DOIs in references can match Uniprot

## 10.1038_s41597-019-0101-y

Lots of records such as SAMN10880019 are in an “online only” table which is not in the PDF but is in the XML(!)

## 10.1029_2023wr035126

Some DOIs are for software, e.g. https://doi.org/10.5066/p9cc9jex and https://doi.org/10.5281/zenodo.7859686


