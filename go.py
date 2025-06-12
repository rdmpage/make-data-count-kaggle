# Replace this with your actual CSV text
csv_text = """
row_id,article_id,dataset_id,type
0,10.1002_chem.201903120,https://doi.org/10.1002/chem.201903120,Primary
1,10.1002_cssc.202201821,https://doi.org/10.5281/zenodo.7074790,Primary
2,10.1002_cssc.202201821,https://doi.org/10.5281/zenodo.7074790,Primary
3,10.1002_ece3.3985,https://doi.org/10.1002/ece3.3985,Primary
4,10.1002_ece3.4466,https://doi.org/10.5061/dryad.r6nq870,Primary
5,10.1002_ece3.5260,https://doi.org/10.5061/dryad.2f62927,Primary
6,10.1002_ece3.5395,https://doi.org/10.5441/001/1.v1cs4nn0,Primary
7,10.1002_ece3.5395,https://doi.org/10.5441/001/1.c42j3js7,Primary
8,10.1002_ece3.5395,https://doi.org/10.5441/001/1.4192t2j4,Primary
9,10.1002_ece3.5395,https://doi.org/10.5441/001/1.ck04mn78,Primary
10,10.1002_ece3.5395,https://doi.org/10.5441/001/1.71r7pp6q,Primary
11,10.1002_ece3.6144,https://doi.org/10.5061/dryad.zw3r22854,Primary
12,10.1002_ece3.6303,https://doi.org/10.5061/dryad.37pvmcvgb,Primary
13,10.1002_ece3.9627,https://doi.org/10.5061/dryad.b8gtht7h3,Primary
14,10.1002_mp.14424,https://doi.org/10.7937/tcia.2020.6c7y‐gq39,Primary
"""

# Define the output file name
output_file = "submission.csv"

# Write the CSV text to a file
with open(output_file, "w", encoding="utf-8") as f:
    f.write(csv_text.strip())

print(f"CSV file saved as: {output_file}")
