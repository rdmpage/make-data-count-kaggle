import os
import json
import csv
import re
import sys
import pymupdf
#import pymupdf4llm


# Define input and output directories
if os.getenv('KAGGLE_KERNEL_RUN_TYPE'):
    pdf_folder = '/kaggle/input/make-data-count-finding-data-references/test/PDF'
    text_folder = '/kaggle/temp/'
else:
    pdf_folder = 'train/pdf'
    text_folder = 'text'

    #pdf_folder = 'test/pdf'
    #text_folder = 'text'
    
DO_SANITISE     = True
DO_TEXT         = True
DO_PATTERNS_2   = True
DO_PATTERNS_3   = True
DO_PATTERNS_4   = True
DO_PATTERNS_5   = True
DO_EXTRACT_DOIS = True
DO_BIOSAMPLE    = True

# TTP5F works
# TTP4T works 0.338
# TTP5T works 0.330
# TTP5T B works 0.330

# not doing GenBank raises the score a lot!

# Ensure the output directory exists
os.makedirs(text_folder, exist_ok=True)
#os.makedirs(json_folder, exist_ok=True)

def value_is_ok(value):
    ok = True
    
    if re.search(r'[\s|,|"|#]', value):
       ok = False
       
    if value == "":
       ok = False
       
    if len(value) > 64:
        ok = False
    
    return ok
    
def extract_dois(text, json_data):
    """
    Extracts DOIs from the given text, formats them, and appends them to the json_data structures.
    
    Parameters:
        text (str): The text to search for DOIs.
        json_data (dict): A dictionary expected to have a key 'data_citations' where DOIs will also be added.
    """
    pattern = r'((DOI[:|,]\s*|doi:\s*|https?://(dx\.)?doi.org/)?' \
              r'10\.[0-9]{4,}(?:\.[0-9]+)*(?:/|%2F)(?:(?!["&\'])\S)+)'

    matches = re.findall(pattern, text, re.IGNORECASE)

    dois = [match[0] for match in matches]

    for doi in dois:
        doi = clean_doi(doi)
        
        if value_is_ok(doi):
            if is_data_doi(doi):
                json_data.setdefault('data_citations', {}).setdefault('doi', [])
                if doi not in json_data['data_citations']['doi']:
                    json_data['data_citations']['doi'].append(doi)    

def clean_doi(doi):
    doi = re.sub(r'https://datadryad.org/resource/doi:', '', doi)

    doi = re.sub(r'[;|,|\.|\)|>|\]]+$', '', doi)
    doi = re.sub(r'^DOI[:|,]\s*', '', doi, flags=re.IGNORECASE)
    doi = re.sub(r'^https?://(dx\.)?doi.org/', '', doi)
    doi = re.sub(r'^https?://doi.pangaea\.de/', '', doi)
    doi = re.sub(r'#.*$/', '', doi)
    doi = re.sub(r'\.+$', '', doi)
    #doi = re.sub(r'[\u2010\u2011\u2012\u2013\u2014\u2015]', '-', doi)
     
    doi = re.sub(r"[^A-Za-z0-9\-._~:/?#\[\]@!$&'()*+,;=%]", "", doi)
    
    doi = doi.lower()
    doi = 'https://doi.org/' + doi
    
    return doi
    

def is_data_doi(doi):
    # Check known DOI patterns for data repositories
    patterns = [
        r'10.1594/idea',
        r'10.1594/pangea',
        r'10.25386', # https://gsajournals.figshare.com/
        r'10.25387', # https://gsajournals.figshare.com/
        r'10.3334/cdiac', # CDIAC
        r'10.5061/dryad',
        r'10.5066/[a-zA-Z]',
        r'10.5066/[a-zA-Z0-9]',
        r'10.5067',
        r'10.5256/f1000research.\d+.d\d+',
        r'10.5281/zenodo',
        r'10.5291/', # USDA          
        r'10.5441/001/', # MoveBank
        r'10.6070/[A-Z0-9]+', #  BMC          
        r'10.6073/pasta',
        r'10.6075/[a-zA-Z0-9]',        
        r'10.6084/m\d\.figshare.[0-9\.v]+',
        r'10.7937/',
        r'10.13020/', # Minnesota 
        r'10.15131/shef.data.', # Sheffield 
        r'10.15454/',
        r'10.15468/dl', # GBIF
        r'10.15482/usda', # USDA   
        r'10.15485', # https://data.ess-dive.lbl.gov/view/doi:10.15485/1843541
        r'10.16904/envidat',
        r'10.17044', # figshare.scilifelab.se
        r'10.17600/\d+',
        r'10.17632/', # Mendeley
        r'10.17863/', # Cambridge
        r'10.17882/\d+',
        r'10.17910/', # Harvard
        r'10.18150/', # MX-RDR
        r'10.21942/', # UVA
        r'10.25377/sussex', # Sussex 
        r'10.3886/icpsr', # Uniform Crime Reporting Program Data
        r'10.7291', # Dryad
        r'10.24381', # climate data store
        r'10.6096', # baobab
        r'10.26197', # ALA
        r'10.22033', # wdc-climate
        #r'10.5194', # essd publish data papers, not data
        r'10.17862', #cranfield
    ]
    
    for pattern in patterns:
        if re.search(pattern, doi, re.IGNORECASE):
            return True
            
    return False

rows = []

# Process each PDF file
for filename in sorted(os.listdir(pdf_folder)):
    if filename.endswith('.pdf'):
    
        print (filename)
        print ("\n")
        
        id = filename.replace('.pdf', '')
        
        # Create JSON document
        json_data = {
           'id' : id,
           'data_citations' : {}
        }        
    
        pdf_path = os.path.join(pdf_folder, filename)

        if 0:
            md_text = pymupdf4llm.to_markdown(pdf_path)
        
            text_filename = filename.replace('.pdf', '.md')
            text_path = os.path.join(text_folder, text_filename)

            with open(text_path, 'w', encoding='utf-8') as text_file:
                text_file.write(md_text)


        if 1:
            doc = pymupdf.open(pdf_path) # open a document
            
            for page in doc:
                links = page.get_links()  # Get all links on the page

                # Extract DOIs from links in PDF
                for link in links:
                    uri = link.get("uri", None)  # The URL if it's a URI link
                    if uri:
                    
                        #print(uri)
                    
                        if is_data_doi(uri):
                            doi = clean_doi(uri)
                            
                            print(doi)
                            
                            json_data.setdefault('data_citations', {}).setdefault('doi', [])
                            if doi not in json_data['data_citations']['doi']:
                                json_data['data_citations']['doi'].append(doi)
                      
                            
                     
            if DO_TEXT:     
                text_filename = filename.replace('.pdf', '.txt')
                text_path = os.path.join(text_folder, text_filename)
                
                # get text from PDF, save to disk
                out = open(text_path, "wb") # create a text output
                for page in doc: # iterate the document pages
                    text = page.get_text().encode("utf8") # get plain text (is in UTF-8)                    
                    out.write(text) # write text of page
                    out.write(bytes((12,))) # write page delimiter (form feed 0x0C)
                out.close()
                
                # process
         
                with open(text_path, "r", encoding="utf-8-sig") as f:
                  content = f.read()
        
                  # Split content by form feed character (0x0C)
                  pages = content.split('\f')
                
                  for page in pages:
                
                    patterns = {}
                    
                    if DO_PATTERNS_2:
                        patterns = {
                            'biosample' : r'SAM[NED]\w?\d+', # https://registry.identifiers.org/registry/biosample
                            'genbank'   : r'\b([A-Z]\d{5}|[A-Z]{2}\d{6})\b',
                            'interpro'  : r'IPR\d{6}',
                            'pfam'      : r'PF\d{5}',
                            'prjna'     : r'PRJ[DEN][A-Z]\d+', # https://registry.identifiers.org/registry/bioproject
                        } 

                    if DO_PATTERNS_3:
                        patterns = {
                            'arxe'      : r'E-GEOD-\d+', # https://www.ebi.ac.uk/biostudies/arrayexpress
                            'arxp'      : r'E-PROT-\d+', # https://www.ebi.ac.uk/biostudies/arrayexpress
                            'biosample' : r'SAM[NED]\w?\d+', # https://registry.identifiers.org/registry/biosample
                            'chembl'    : r'CHEMBL\d+',
                            'empiar'    : r'EMPIAR-\d{5,}',
                            'ensembl'   : r'ENS[A-Z]{4}\d{11}',   # ENSBTAG00000011038
                            'genbank'   : r'\b([A-Z]\d{5}|[A-Z]{2}\d{6})\b',
                            'hpa'       : r'((CAB|HPA)\d{6})', # http://www.proteinatlas.org/search/CAB004592
                            'interpro'  : r'IPR\d{6}',
                            'pfam'      : r'PF\d{5}',
                            'prjna'     : r'PRJ[DEN][A-Z]\d+', # https://registry.identifiers.org/registry/bioproject
                            'pxd'       : r'PXD\d{6}', # https://www.proteomexchange.org    
                            'sra'       : r'[SED]R[APRSXZ]\d+', # https://registry.identifiers.org/registry/insdc.sra
                        }      

                    if DO_PATTERNS_4:
                        patterns = {
                            'arxe'      : r'E-GEOD-\d+', # https://www.ebi.ac.uk/biostudies/arrayexpress
                            'arxp'      : r'E-PROT-\d+', # https://www.ebi.ac.uk/biostudies/arrayexpress
                            'biosample' : r'SAM[NED]\w?\d+', # https://registry.identifiers.org/registry/biosample
                            'chembl'    : r'CHEMBL\d+',
                            'empiar'    : r'EMPIAR-\d{5,}',
                            
                            'encode'    : r'ENCSR[A-Z0-9]+', # ENCODE 
                            
                            'ensembl'   : r'ENS[A-Z]{4}\d{11}',   # ENSBTAG00000011038
                            
                            'insdcgca'  : r'(GCA_[0-9]{9}(\.[0-9]+))?', # insdc.gca
                            
                            # https://www.ncbi.nlm.nih.gov/genbank/acc_prefix/
                            #'genbank'   : r'\b([A-Z]\d{5}|[A-Z]{2}\d{6})\b',
                            
                            'gisaidisl' : r'(EPI(_ISL_)?\d+)', # not in identifiers.org
                            
                            'geo'       : r'GSM\d{5,}', # modified https://registry.identifiers.org/registry/geo
                            
                            # https://www.ncbi.nlm.nih.gov/books/NBK21091/table/ch18.T.refseq_accession_numbers_and_mole/?report=objectonly
                            'nm'        : r'(NM_\d{6}(\.[0-9]+))?', 
                            
                            'gse'       : r'((GEO:)?GSE\d{5,})',
                            
                            'hpa'       : r'((CAB|HPA)\d{6})', # http://www.proteinatlas.org/search/CAB004592
                            'interpro'  : r'IPR\d{6}',
                            'pfam'      : r'PF\d{5}',
                            'prjna'     : r'PRJ[DEN][A-Z]\d+', # https://registry.identifiers.org/registry/bioproject
                            'pxd'       : r'PXD\d{6}', # https://www.proteomexchange.org    
                            'sra'       : r'[SED]R[APRSXZ]\d+', # https://registry.identifiers.org/registry/insdc.sra
                            
                            'up'        : r'UP\d{9}', # https://www.uniprot.org/proteomes/UP000006548
                        }      

                    if DO_PATTERNS_5:
                        patterns = {
                            'arxe'      : r'E-GEOD-\d+', # https://www.ebi.ac.uk/biostudies/arrayexpress
                            'arxp'      : r'E-PROT-\d+', # https://www.ebi.ac.uk/biostudies/arrayexpress
                            'biosample' : r'SAM[NED]\w?\d+', # https://registry.identifiers.org/registry/biosample
                            
                            #'cellosaurus' : r'(CVCL_[0-9A-Z][0-9A-Z]\d{2})',
                            
                            'chembl'    : r'CHEMBL\d+',
                            
                            'dbsnp'     : r'rs\d{4,}', # modified from https://registry.identifiers.org/registry/dbsnp
                            
                            #'dra'       : r'DRA\d{6}', # https://www.ddbj.nig.ac.jp/dra/index-e.html
                            
                            'empiar'    : r'EMPIAR-\d{5,}',
                            
                            'encode'    : r'ENCSR[A-Z0-9]+', # ENCODE 
                            
                            'ensembl'   : r'ENS[A-Z]{4}\d{11}',   # ENSBTAG00000011038
                            
                            'insdcgca'  : r'(GCA_[0-9]{9}(\.[0-9]+))?', # insdc.gca
                            
                            # https://www.ncbi.nlm.nih.gov/genbank/acc_prefix/
                            #'genbank'   : r'\b([A-Z]\d{5}|[A-Z]{2}\d{6}(\.[0-9]+)?)\b',
                            'genbank'   : r'\b([A-Z]{2}\d{6}(\.[0-9]+)?)\b', # just 2 letters + 6 digits
                            
                            'gisaidisl' : r'(EPI(_ISL_)?\d+)', # not in identifiers.org
                            
                            'geo'       : r'GSM\d{5,}', # modified https://registry.identifiers.org/registry/geo
                            
                            #'massive'   : r'MSV\d{9}', # https://massive.ucsd.edu/
                            
                            # https://www.ncbi.nlm.nih.gov/books/NBK21091/table/ch18.T.refseq_accession_numbers_and_mole/?report=objectonly
                            'nm'        : r'(N[CM]_\d{6}(\.[0-9]+)?)', 
                            
                            'gse'       : r'((GEO:\s*)?GSE\d{5,})',
                            
                            'hpa'       : r'((CAB|HPA)\d{6})', # http://www.proteinatlas.org/search/CAB004592
                            'interpro'  : r'IPR\d{6}',
                            
                            #'pdb'       : r'\b(PDB:\s*[0-9][A-Za-z0-9]{3})\b', # PDB, likely lots of false hits unless we include prefix
                            
                            'pfam'      : r'(PF\d{5}(.\d{1,2})?)', # PFAM seems to have versions, e.g. PF01493.23)
                            'prjna'     : r'PRJ[DEN][A-Z]\d+', # https://registry.identifiers.org/registry/bioproject
                            'pxd'       : r'PXD\d{6}', # https://www.proteomexchange.org    
                            'sra'       : r'[SED]R[APRSXZ]\d+', # https://registry.identifiers.org/registry/insdc.sra
                            
                            'up'        : r'UP\d{9}', # https://www.uniprot.org/proteomes/UP000006548
                        }      
                       
                    for source, pattern in patterns.items():
                        matches = re.findall(pattern, page)
    
                        for hit in matches:
                            if not isinstance(hit, str):
                                hit = hit[0]
    
                            if value_is_ok(hit):

                                json_data.setdefault('data_citations', {}).setdefault(source, [])
                                if hit not in json_data['data_citations'][source]:
                                    json_data['data_citations'][source].append(hit)
                                    
                    # dois (we will have many of these from links, but some may be plain text)
                    if DO_EXTRACT_DOIS:
                    
                        lines = page.split('\n')
      
                        text = ''      
                        for line in lines:
                            line = re.sub(r'[-|-]\s*$', '', line)
                            text += line
                    
                        extract_dois(page, json_data)
                        
                 
        citations = json_data['data_citations'];
          
        for data_type, values in citations.items():
            for value in values: 
                if DO_SANITISE:
                   value = re.sub(r'[^\x00-\x7F]|[\r\n",]', '', value) 
                match data_type:
                    # Assume DOIs are only added if in body or back, not references
                    # unless they match known data repos
                    case "doi":
                        if re.search(r'10\.15468/dl', value, re.IGNORECASE): 
                            # GBIF downloads are primary
                            rows.append([id, value, 'Primary'])
                        else:
                            # Data DOIs are assumed to be primary
                            rows.append([id, value, 'Primary'])

                    
                    case "biosample":
                        if DO_BIOSAMPLE:
                            # Assume a biosample is novel
                            rows.append([id, value, 'Primary'])
                        else:
                            ows.append([id, value, 'Secondary'])
                
                    case _:
                        rows.append([id, value, 'Secondary'])
           


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
