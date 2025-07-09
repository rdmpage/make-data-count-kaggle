import os
import re
import json
from pdftext.extraction import paginated_plain_text_output, plain_text_output,dictionary_output
import csv
import sys

#-----------------------------------------------------------------------------------------     
def parse_text_blocks(text):
    # Split text into blocks separated by two or more blank lines
    blocks = re.split(r'(?:\r?\n\s*){2,}', text.strip())

    # Join lines in each block with a space
#   return [' '.join(line.strip() for line in block.strip().splitlines() if line.strip())
#           for block in blocks if block.strip()]

    # Join lines, no space as that might break URLs (need to be more clever about this)
    return ['•'.join(line.strip() for line in block.strip().splitlines() if line.strip())
            for block in blocks if block.strip()]

#-----------------------------------------------------------------------------------------
# Given the result of a regex match, the source text, and the type of entity being
# matched, store any hits as simple annotations. we store start and end coordinates,
# and prefix and suffix strings.
def make_annotation(match, text, type):
    annotation = {}

    annotation['exact'] = match.group()
    
    # start and end positions in the string
    start = match.start()
    end =  match.end()
    
    # get prefix and suffix
    left = max(0, start - 64)
    right = min(len(text), end + 64)
    
    annotation['prefix'] = text[left:start]
    annotation['suffix'] = text[end:right]
    
    annotation['start'] = start
    annotation['end ']=  end
    
    annotation['type'] = type
    
    return annotation
    
#-----------------------------------------------------------------------------------------
# crude sanity check to ensure our identifiers are reasonable and don't, for example,
# contain strings that would break CSV output
def value_is_ok(value):
    ok = True
    
    if re.search(r'[\s|,|"|#]', value):
       #print("bad chars")
       ok = False

    if value == "":
       #print("empty")
       ok = False    
       
    if len(value) > 64:
        #print("too long")
        ok = False
    
    return ok
    

#-----------------------------------------------------------------------------------------
def find_datasets(element, text):

    patterns = {
        'arxe'        : r'E-GEOD-\d+', # https://www.ebi.ac.uk/biostudies/arrayexpress
        'arxm'        : r'E-MTAB-\d+', # https://www.ebi.ac.uk/biostudies/arrayexpress
        'arxp'        : r'E-PROT-\d+', # https://www.ebi.ac.uk/biostudies/arrayexpress
        'biosample'   : r'SAM[NED]\w?\d+', # https://registry.identifiers.org/registry/biosample
        'cellosaurus' : r'(CVCL_[0-9A-Z][0-9A-Z]\d{2})',
        'chembl'      : r'CHEMBL\d+',
        'dbsnp'       : r'(rs\d{4,})', # modified from https://registry.identifiers.org/registry/dbsnp
        'empiar'      : r'EMPIAR-\d{5,}',
        'encode'      : r'ENCSR[A-Z0-9]+', # ENCODE 
        'ensembl'     : r'ENS[A-Z]{4}\d{11}',   # ENSBTAG00000011038
        'gisaidisl'   : r'(EPI(_ISL_)?\d+)', # not in identifiers.org            
        'geo'         : r'GSM\s*\d{5,}', # modified https://registry.identifiers.org/registry/geo        
        'gse'         : r'((GEO:\s*)?GSE\d{5,})',
        'hpa'         : r'((CAB|HPA)\d{6})', # http://www.proteinatlas.org/search/CAB004592
        'insdcgca'    : r'(GCA_[0-9]{9}(\.[0-9]+)?)', # insdc.gca
        'interpro'    : r'IPR\d{6}',   
        'massive'     : r'MSV\d{9}',             
        'nm'          : r'(N[CM]_?\d{6}(\.[0-9]+)?)', # added ? after _ because eLife sometimes misses the underscore. https://www.ncbi.nlm.nih.gov/books/NBK21091/table/ch18.T.refseq_accession_numbers_and_mole/?report=objectonly
        'pdb'         : r'\b((PDB(\s*ID)?:?\s*)?[0-9][A-Za-z][A-Za-z0-9]{2})\b', # PDB, likely lots of false hits unless we include prefix
        'pfam'        : r'(PF\d{5}(.\d{1,2})?)', # PFAM seems to have versions, e.g. PF01493.23)   
        'prjna'       : r'PRJ[DEN][A-Z]\d+', # https://registry.identifiers.org/registry/bioproject
        'pxd'         : r'PXD\d{6}', # https://www.proteomexchange.org    
        'sra'         : r'[SED]R[APRSXZ]\d+', # https://registry.identifiers.org/registry/insdc.sra
        'up'          : r'UP\d{9}', # https://www.uniprot.org/proteomes/UP000006548
        
        # https://registry.identifiers.org/registry/insdc
        #'insdc'     : r'\b([A-Z]\d{5}|[A-Z]{2}\d{6}|[A-Z]{4,6}\d{8,10}|[A-J][A-Z]{2}\d{5})(\.\d+)?\b',
        'genbank'    : r'\b(A[B-HJ-MPUX-Y]|B[AC-DS-TVX]|C[HMPR-UY]|D[DF-GP-QS]|E[FM-NP-QUZ]|F[JM-RX]|G[F-GLQU]|H[E-GMP-Q]|J[FH-ILN-RT-X]|K[A-FI-NP-RT-VX-Z]|L[AC-EH-KM-NRT]|M[F-HK-LNT-UWZ]|O[DK-NP-RU-VX-Z]|P[P-Q])\d{6}(\.\d+)?\b',
        
        'pass'        : r'PASS\d+', # https://registry.identifiers.org/registry/peptideatlas.dataset 
    }   
    
    for source, pattern in patterns.items():
        for match in re.finditer(pattern, text):
            #print (source, " ", match.group())
            # sanity check
            if value_is_ok(match.group()):
                element['annotations'].append(make_annotation(match, text, source))

#----------------------------------------------------------------------------------------- 
# formats a DOI, assumes that DOI is clean and has no http prefix    
def format_doi(doi):
    doi = doi.lower()
    doi = 'https://doi.org/' + doi   
    return doi
       
#----------------------------------------------------------------------------------------- 
# clean a DOI, returns DOI inf format 10.\d+... 
def clean_doi(doi):

    match = re.search(r'(10\.[0-9]{4,}(?:\.[0-9]+)*(?:/|%2F)(?:(?!["&\'])\S)+)', doi)
    if match:
        doi = match.group()

    doi = re.sub(r'[\.,\);]+$', '', doi) # remove terminal punctuation
    
    doi = re.sub(r'[A|a]ccessed.*$', '', doi) # remove accessed date    
    
    if (re.search(r'figshare', doi)):
        print(doi)
        doi = re.sub(r'(figshare.\d+.v\d)\d+', r'\1', doi)
        print(doi)
    
    return doi
    
#----------------------------------------------------------------------------------------- 
# Check known DOI patterns for data repositories
def is_data_doi(doi):

    patterns = [
        r'10.3334/cdiac',                   # www.ncei.noaa.gov
        r'10.3886/icpsr',                   # www.icpsr.umich.edu
        r'10.5061/dryad',                   # datadryad.org
        r'10.5066/[a-zA-Z0-9]',             # www.sciencebase.gov/
        r'10.5067',                         # www.earthdata.nasa.gov/
        r'10.5256/f1000research.\d+.d\d+',  # f1000research.com
        r'10.5281/zenodo',                  # zenodo.org
        r'10.5291/',                        # www.ill.eu
        r'10.5441/001/',                    # datarepository.movebank.org/home
        r'10.6070/[A-Z0-9]+',               # mynotebook.labarchives.com
        r'10.6073/pasta',                   # portal.edirepository.org/nis/home.jsp
        r'10.6075/[a-zA-Z0-9]',             # library.ucsd.edu/
        r'10.6084/m\d\.figshare.[0-9\.v]+', # figshare.com
        r'10.6096',                         # baobab.sedoo.fr
        r'10.7291',                         # datadryad.org
        r'10.7937/',                        # www.cancerimagingarchive.net/
        r'10.13020/',                       # conservancy.umn.edu
        r'10.15131/shef.data.',             # orda.shef.ac.uk/ (FigShare)
        r'10.15454/',                       # entrepot.recherche.data.gouv.fr
        r'10.15468/dl',                     # www.gbif.org
        r'10.15482/usda',                   # agdatacommons.nal.usda.gov/ (FigShare)
        r'10.15485',                        # data.ess-dive.lbl.gov
        r'10.16904/envidat',                # www.envidat.ch/
        r'10.17044',                        # figshare.scilifelab.se
        r'10.17600/\d+',                    # campagnes.flotteoceanographique.fr
        r'10.17632/',                       # data.mendeley.com
        r'10.17863/',                       # www.repository.cam.ac.uk
        r'10.17882/\d+',                    # www.seanoe.org
        r'10.18150/',                       # mxrdr.icm.edu.pl
        r'10.21942/',                       # uvaauas.figshare.com
        r'10.22033',                        # www.wdc-climate.de
        r'10.24381/cds',                    # cds.climate.copernicus.eu
        r'10.25386',                        # gsajournals.figshare.com/
        r'10.25387',                        # gsajournals.figshare.com/
        r'10.26197',                        # ala.org.au
        r'10.1594/pangaea',                 # www.pangaea.de
        r'10.5883/DS',                      # portal.boldsystems.org
    ]
    
    for pattern in patterns:
        if re.search(pattern, doi, re.IGNORECASE):
            return True
            
    return False

#----------------------------------------------------------------------------------------- 
# Hack to say some DOIs are almost certainly primary
def is_primary_doi(doi):

    patterns = [
        r'10.26197',                        # ala.org.au   
        r'10.15468/dl',                     # www.gbif.org
        r'10.5061/dryad',                   # datadryad.org
    ]    

    for pattern in patterns:
        if re.search(pattern, doi, re.IGNORECASE):
            return True
            
    return False

#-----------------------------------------------------------------------------------------     
# Define input and output directories
if os.getenv('KAGGLE_KERNEL_RUN_TYPE'):
    pdf_folder = '/kaggle/input/make-data-count-finding-data-references/test/PDF'
    json_folder = '/kaggle/temp/'
    text_folder = '/kaggle/temp/'
else:
    pdf_folder = 'train/PDF'
    json_folder = 'pdfjson'
    text_folder = 'pdftext'

    pdf_folder = 'explore-pdf'
    json_folder = 'explore-pdf'

# Ensure the output directory exists
os.makedirs(json_folder, exist_ok=True)
os.makedirs(text_folder, exist_ok=True)

#-----------------------------------------------------------------------------------------
# Process each PDF file
for filename in sorted(os.listdir(pdf_folder)):
    if filename.endswith('.pdf'):
    
        print (filename)
        
        id = filename.replace('.pdf', '')
        
        json_filename = filename.replace('.pdf', '.json')
        json_path = os.path.join(json_folder, json_filename)    
        
        #if os.path.exists(json_path):
        if False:
            print (json_filename, " exists") 
        else:   
            pdf_path = os.path.join(pdf_folder, filename)
    
            pages = paginated_plain_text_output(pdf_path, sort=True, hyphens=False) # Optional arguments explained above
            
            if False:
                text_filename = filename.replace('.pdf', '.json')
                text_path = os.path.join(text_folder, text_filename)    
                with open(text_path, 'w', encoding='utf-8') as text_file:
                    json.dump(pages, text_file, indent=2, ensure_ascii=False)
                       
            # Create JSON document
            doc = {
                'id' : filename.replace('.pdf', ''),
                'source_type' : 'pdf',
                'title' : None,
                'doi' : None,
                'pages' : [],
                'data_citations' : {}
            }
    
            for pdf_page in pages:
            
                page = {
                   "blocks" :  [],                  
                }
                
                pdf_blocks = parse_text_blocks(pdf_page)
                for pdf_block in pdf_blocks:
                
                    # clean end of line markers
                    text = pdf_block
                    text = re.sub(r"(https?:[^\s]+)[\.|;]?•([^A-Z\(\[])", r"\1\2", text)
                    text = re.sub(r"•", r" ", text)
                
                    block = {
                       "text" : text,
                       "type" : None,
                       "annotations": []
                    } 
                    
                    page['blocks'].append(block)
 
                doc['pages'].append(page)
    
            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(doc, json_file, indent=2, ensure_ascii=False)

#-----------------------------------------------------------------------------------------     
print("Processing JSON")

rows = []

# For each JSON document we process the text for identifiers, such as DOIs. 
# These are stored as annotations.
for filename in os.listdir(json_folder):
    if filename.endswith('.json'):
    
        print (filename)
        
        id = filename.replace('.json', '')
        
        json_path = os.path.join(json_folder, filename)
        
        with open(json_path, 'rb') as f:
            doc = json.load(f)
            
            # do stuff
            for page in doc['pages']:
                for block in page['blocks']:

                    text = block["text"]
                    
                    # dois                    
                    pattern = r'((DOI[:|,]\s*|doi:\s*|https?://(dx\.)?doi.org/)?' \
                        r'(10\.[0-9]{4,}(?:\.[0-9]+)*(?:/|%2F)(?:(?!["&\'])\S)+))'
                    
                    for match in re.finditer(pattern, text):
                        block['annotations'].append(make_annotation(match, text, 'doi'))
                        
                    # other things
                    find_datasets(block, text)
                    
                        
        #---------------------------------------------------------------------------------
        # get data citations in text
        for i, page in enumerate(doc['pages']):
            for j, block in enumerate(page['blocks']):
                if block.get('annotations'):
                    for k, annotation in enumerate(block['annotations']):
                    
                        dataset_id = annotation['exact']
                                               
                        if annotation['type'] == 'doi':
                        
                             if annotation['type'] == 'doi':
                                doi = dataset_id
                                doi = clean_doi(doi)
                                doi = format_doi(doi)
                                
                                is_data_citation = False
                        
                                # Does DOI look like it comes from a data repository?
                                if is_data_doi(doi):
                                    is_data_citation = True   
                                    
                                if is_data_citation:
                                    doc['data_citations'][doi] = 'Primary'
                                    
                        elif annotation['type'] in ['biosample', 'genbank', 'prjna', 'pxd', 'sra']:
                            doc['data_citations'][dataset_id] = 'Primary'
                        else:
                            doc['data_citations'][dataset_id] = 'Secondary'
                                    
                                
                         
                     
        #---------------------------------------------------------------------------------
        # save annotated doc
        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(doc, json_file, indent=2, ensure_ascii=False)
                    
        #---------------------------------------------------------------------------------
        # Add citations to list of results
        if doc.get('data_citations'):
            for citation, type in doc['data_citations'].items():
               rows.append([doc['id'], citation, type])
                    
# Output CSV file

with open('submission.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter=',')
    
    # Write header
    writer.writerow(['row_id', 'article_id', 'dataset_id', 'type'])
    
    for i, row in enumerate(rows):
        writer.writerow([i] + row)
  
# show first few lines      
with open('submission.csv', newline='', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter=',')
    
    for i, row in enumerate(reader):
        print('\t'.join(row))  # Print row with tab spacing
        if i == 9:  # Stop after 10 rows (including header)
            break       

