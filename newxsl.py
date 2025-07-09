import os
import re
import json
import csv
import sys
from lxml import etree
import xmltodict
import pprint

# Define input and output directories
if os.getenv('KAGGLE_KERNEL_RUN_TYPE'):
    xml_folder = '/kaggle/input/make-data-count-finding-data-references/test/XML'
    xml_folder = '/kaggle/input/make-data-count-finding-data-references/train/XML'
    json_folder = '/kaggle/temp/'
    
    xsl_folder = '/kaggle/input/article-xslt'

else:
    xml_folder = 'train/XML'
    #xml_folder = 'test/XML'
    #json_folder = 'xsljson'

    xml_folder = 'xslxml'
    json_folder = 'xsljson'
    
    xsl_folder = 'article-xslt'
    
    

# Ensure the output directory exists
os.makedirs(json_folder, exist_ok=True)

# Process XML and convert to simple JSON

# Regular expression pattern to detect XML type (customize as needed)
xml_type_pattern = re.compile(r'<\?xml[^>]*\?>|<!DOCTYPE[^>]*>', re.IGNORECASE)


#----------------------------------------------------------------------------------------- 
# Process each XML file
for filename in os.listdir(xml_folder):
    if filename.endswith('.xml'):
    
        print (filename)
        
        xml_path = os.path.join(xml_folder, filename)

        # Read the first 1024 bytes
        with open(xml_path, 'rb') as f:
            header_bytes = f.read(1024)
        header_text = header_bytes.decode('utf-8', errors='ignore')

        # Determine the XML type
        xml_types = {
           'bioc'  : r'BioC.dtd',
           'jats'  : r'(NLM|TaxonX)//DTD',
           'tei'   : r'www.tei-c.org/ns',
           'wiley' : r'www.wiley.com/namespaces'
        }
        
        xml_format = 'unknown'
        for format, pattern in xml_types.items():
            if re.search(pattern, header_text, flags=re.IGNORECASE):
                xml_format = format
                
        # choose appropriate XSL
        xsl_filename = ''
        
        match xml_format:
            case 'bioc':
                xsl_filename = 'bioc-html.xsl'
 
            case 'jats':
                xsl_filename = 'jats-html.xsl'
               
            case 'tei':
                xsl_filename = 'tei-html.xsl'

            case 'wiley':
                xsl_filename = 'wiley-html.xsl'
                
            case _:
                xsl_filename = ''
            
        if xsl_filename != '':
            # transform
            xsl_path = os.path.join(xsl_folder, xsl_filename )
    
            dom = etree.parse(xml_path)
            xslt = etree.parse(xsl_path)
            transform = etree.XSLT(xslt)
            result_tree = transform(dom)
            
            # Convert the result to string
            result_str = str(result_tree)
    
            # Parse XML string to dict
            result_dict = xmltodict.parse(result_str)
            
            #print(result_dict)
    
            # Step 4: Convert dict to JSON
            json_output = json.dumps(result_dict, indent=2)
    
            # Print the JSON
            #print(json_output)        
    
            # Save to JSON with same name but .json extension
            json_filename = filename.replace('.xml', '.json')
            json_path = os.path.join(json_folder, json_filename)
    
            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(result_dict, json_file, indent=2, ensure_ascii=False)

print("Finished processing XML files")


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
    
    doi = re.sub(r'\)and$', '', doi) # remove terminal punctuation
    
    doi = re.sub(r'[A|a]ccessed.*$', '', doi) # remove accessed date
        
    return doi

#----------------------------------------------------------------------------------------- 
# clean identifier, for now blank 
def clean_identifier(id):
    return id

#-----------------------------------------------------------------------------------------
# Given the result of a regex match, the source text, and the type of entity being
# matched, store any hits as simple annotations. we store start and end coordinates,
# and prefix and suffix strings.
def make_annotation(match, text, annotation_type, section_type):
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
    
    annotation['type'] = annotation_type
    
    annotation['section_type'] = section_type
    
    return annotation

#-----------------------------------------------------------------------------------------
# strip any namespace prefix from a string
def remove_namespace(value):
    value = re.sub(r'^[A-Z]+:\s*', '', value)
    return value
    
#-----------------------------------------------------------------------------------------
# crude sanity check to ensure our identifiers are reasonable and don't, for example,
# contain strings that would break CSV output
def value_is_ok(value):
    ok = True
    
    # clean any namespace prefix before we check
    value = remove_namespace(value)
    
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
# Find DOIs and add as annotations
def find_dois(id, text, section_type):
    pattern = r'((DOI[:|,]\s*|doi:\s*|https?://(dx\.)?doi.org/)?' \
	    r'(10\.[0-9]{4,}(?:\.[0-9]+)*(?:/|%2F)(?:(?!["&\'])\S)+))'

    for match in re.finditer(pattern, text):
        # print(match)
        
        annot = make_annotation(match, text, 'doi', section_type)
        
        # store a cleaned version of the DOI
        annot['value'] = clean_doi(annot['exact'])
        annot['value'] =  format_doi(annot['value'])
        
        if id not in annotations:
           annotations[id] = []
        annotations[id].append(annot)
        
#-----------------------------------------------------------------------------------------
# Find data identifiers
def find_datasets(id, text, section_type):

    patterns = {
        'arxe'        : r'E-GEOD-\d+', # https://www.ebi.ac.uk/biostudies/arrayexpress
        'arxm'        : r'E-MTAB-\d+', # https://www.ebi.ac.uk/biostudies/arrayexpress
        'arxp'        : r'E-PROT-\d+', # https://www.ebi.ac.uk/biostudies/arrayexpress
        'biosample'   : r'SAM[NED]\w?\d+', # https://registry.identifiers.org/registry/biosample
        'cellosaurus' : r'(CVCL_[0-9A-Z][0-9A-Z]\d{2})',
        'chembl'      : r'CHEMBL\d+',
        'dbsnp'       : r'rs\d{4,}', # modified from https://registry.identifiers.org/registry/dbsnp
        'empiar'      : r'EMPIAR-\d{5,}',
        'encode'      : r'ENCSR[A-Z0-9]+', # ENCODE 
        'ensembl'     : r'ENS[A-Z]{4}\d{11}',   # ENSBTAG00000011038
        'gisaidisl'   : r'(EPI(_ISL_)?\d+)', # not in identifiers.org            
        'geo'         : r'GSM\d{5,}', # modified https://registry.identifiers.org/registry/geo        
        'gse'         : r'((GEO:\s*)?GSE\d{5,})',
        'hpa'         : r'((CAB|HPA)\d{6})', # http://www.proteinatlas.org/search/CAB004592
        
        # https://registry.identifiers.org/registry/insdc
        #'insdc'     : r'\b([A-Z]\d{5}|[A-Z]{2}\d{6}|[A-Z]{4,6}\d{8,10}|[A-J][A-Z]{2}\d{5})(\.\d+)?\b',
        'genbank'    : r'\b(A[B-HJ-MPUX-Y]|B[AC-DS-TVX]|C[HMPR-UY]|D[DF-GP-QS]|E[FM-NP-QUZ]|F[JM-RX]|G[F-GLQU]|H[E-GMP-Q]|J[FH-ILN-RT-X]|K[A-FI-NP-RT-VX-Z]|L[AC-EH-KM-NRT]|M[F-HK-LNT-UWZ]|O[DK-NP-RU-VX-Z]|P[P-Q])\d{6}(\.\d+)?\b',
        
        'insdcgca'    : r'(GCA_[0-9]{9}(\.[0-9]+)?)', # insdc.gca
        'interpro'    : r'IPR\d{6}',                     
        'nm'          : r'(N[CM]_?\d{6}(\.[0-9]+)?)', # added ? after _ because eLife sometimes misses the underscore. https://www.ncbi.nlm.nih.gov/books/NBK21091/table/ch18.T.refseq_accession_numbers_and_mole/?report=objectonly
        #'pdb'         : r'\b((PDB(\s*ID)?:?\s*)?[0-9][A-Za-z][A-Za-z0-9]{2})\b', # PDB, likely lots of false hits unless we include prefix        
        'pfam'        : r'(PF\d{5}(.\d{1,2})?)', # PFAM seems to have versions, e.g. PF01493.23)   
        'prjna'       : r'PRJ[DEN][A-Z]\d+', # https://registry.identifiers.org/registry/bioproject
        'pxd'         : r'PXD\d{6}', # https://www.proteomexchange.org    
        'sra'         : r'[SED]R[APRSXZ]\d+', # https://registry.identifiers.org/registry/insdc.sra
        'up'          : r'UP\d{9}', # https://www.uniprot.org/proteomes/UP000006548

        'uniprot'     : r'\b([A-N,R-Z][0-9]([A-Z][A-Z, 0-9][A-Z, 0-9][0-9]){1,2})|([O,P,Q][0-9][A-Z, 0-9][A-Z, 0-9][A-Z, 0-9][0-9])(\.\d+)?\b', # https://registry.identifiers.org/registry/uniprot
    }   
    
    for source, pattern in patterns.items():
        for match in re.finditer(pattern, text):
            #print (source, " ", match.group())
            # sanity check
            if value_is_ok(match.group()):
                annot = make_annotation(match, text, source, section_type)
                
                # store a cleaned version of the identifier
                annot['value'] = clean_identifier(annot['exact'])
                
                if id not in annotations:
                    annotations[id] = []
                annotations[id].append(annot)
        
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
# Recursively traverse document tree, keeping track of section type
# This is where we extract identifiers/DOIs
def traverse_document(node, current_type=None):
    if isinstance(node, dict):
        # Update section type if this is a section with a 'type' attribute
        if 'type' in node:
            current_type = node['type']

        # Print text with the current section type
        if '#text' in node:
            id = 'Unknown'
            if '@id' in node:
               id = node['@id']
        
            print(f"[{current_type}] [id: {id}] {node['#text']}")
            
            # look for identifiers
            find_dois(id, node['#text'], current_type)
            find_datasets(id, node['#text'], current_type)
            
        # Traverse 'p'
        if 'p' in node:
            p = node['p']
            if isinstance(p, list):
                for item in p:
                    traverse_document(item, current_type)
            else:
                traverse_document(p, current_type)

        # Traverse nested 'section'
        if 'section' in node:
            sections = node['section']
            if isinstance(sections, list):
                for section in sections:
                    traverse_document(section, current_type)
            else:
                traverse_document(sections, current_type)                

        # Traverse other keys (in case nested text exists there)
        for key, value in node.items():
            if key not in {'#text', 'p', 'section', 'type'}:
                traverse_document(value, current_type)

    elif isinstance(node, list):
        for item in node:
            traverse_document(item, current_type)


#-----------------------------------------------------------------------------------------
# For each JSON document we process the text for identifiers, such as DOIs. 
# These are stored as annotations.

data_citations = {}

for filename in os.listdir(json_folder):
    if filename.endswith('.json'):
    
        annotations = {}
    
        print (filename)
        
        article_id = filename.replace('.json', '')
        
        json_path = os.path.join(json_folder, filename)
        
        with open(json_path, 'rb') as f:
            doc = json.load(f)
            
        # starting point for document traversal
        article = doc['html']['body']['article']
        
        # traverse document
        traverse_document(article)                     
        
        # output list of annotations
        #pprint.pprint (annotations)
        
        data_citations[article_id] = {}
        
        # filter, classify, and output
        for id, annots in annotations.items():
            for annot in annots:
                citation = annot['value']
                
                # do any filering here
                ok = True
                
                if annot['type'] == 'doi':
                   ok = is_data_doi(citation)
                
                if ok:
                    if not citation in data_citations[article_id]:
                         data_citations[article_id][citation] = "Primary"
                
                #rows.append([article_id, citation, 'Primary'])
            
        #print (data_citations)    

#-----------------------------------------------------------------------------------------
        
rows = []  

for article_id, citation in data_citations.items():
    for dataset_id, citation_type in citation.items():
        rows.append([article_id, dataset_id, citation_type])
         
        
#-----------------------------------------------------------------------------------------
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
        
