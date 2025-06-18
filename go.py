import os
import re
import json
from lxml import etree
import csv

# Define input and output directories
xml_folder = 'training-xml-extra'
xml_folder = 'train/xml'
#xml_folder = 'test/xml'
json_folder = 'json'

# Define input and output directories
#xml_folder = '/kaggle/input/make-data-count-finding-data-references/test/XML'
#xml_folder = '/kaggle/input/make-data-count-finding-data-references/train/XML'

#json_folder = '/kaggle/temp/'

# Ensure the output directory exists
os.makedirs(json_folder, exist_ok=True)

# Regular expression pattern to detect XML type (customize as needed)
xml_type_pattern = re.compile(r'<\?xml[^>]*\?>|<!DOCTYPE[^>]*>', re.IGNORECASE)

# Helper function to extract namespaces
def get_namespaces(xml_file):
    try:
        # Extract namespaces declared in the XML file
        with open(xml_file, 'rb') as f:
            for _, elem in etree.iterparse(f, events=('start-ns',)):
                yield elem
    except Exception:
        return

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
        
        tree = etree.parse(xml_path)
        root = tree.getroot()     
           
        # Create JSON document
        json_data = {
           'id' : filename.replace('.xml', ''),
           'source_xml_type' : xml_format,
           'title' : None,
           'doi' : None,
           'sections' : [],
           'references' : [],
           'data_citations' : {}
        }
        
         
        # JATS ---------------------------------------------------------------------------
        if xml_format == "jats":
                      
            # title
            title = None
            path = f'.//front/article-meta/title-group/article-title'
            elements = root.findall(path)
            if elements:
                 if elements[0].text:
                     title = elements[0].text.strip()
                     json_data['title'] = title
                 
            # doi
            doi = None
            path = f'.//front/article-meta/article-id[@pub-id-type="doi"]'
            elements = root.findall(path)
            if elements:
                 doi = elements[0].text.strip()
                 json_data['doi'] = doi
                  
            # Note that some JATS files such as 10.1002_chem.202000235 have no sections!
            # Will need to handle body/p
                 
            # Usually text 
            path = f'.//body/sec'
            sections = root.findall(path)
            if sections:
                for sec in sections:
                
                   # section title
                   sec_title = None
                   title_element = sec.find('title')
                   if title_element is not None:
                       sec_title = title_element.text.strip()
                       
                       #print(sec_title)
                       
                   # paragraph texts (either p, or sec/p)
                   paragraphs = []
                       
                   p_elements = sec.findall('p')                   
                   for p in p_elements:
                       if p.text:
                           paragraph_data = { "text" : p.xpath("normalize-space(string())").strip() }
                           paragraphs.append(paragraph_data)
    
                   p_elements = sec.findall('sec/p')
                   for p in p_elements:
                       if p.text:
                           paragraph_data = { "text" : p.xpath("normalize-space(string())").strip() }
                           paragraphs.append(paragraph_data)
                   
                   # print (paragraphs);
                   # print ("\n")

                   # tables
                   tables = []
                   
                   t_elements = sec.findall(f'.//table')
                   for t in t_elements:
                       table = []
                       
                       tr_elements = t.findall('thead/tr')
                       for tr in tr_elements:
                           row = [];
                           th_elements = tr.findall('th')
                           for th in th_elements:
                              if th.text:
                                  th_text = th.xpath("normalize-space(string())").strip()
                                  row.append(th_text)
                           table.append(row)
                       
 
                       tr_elements = t.findall('tbody/tr')
                       for tr in tr_elements:
                           row = [];
                           td_elements = tr.findall('td')
                           for td in td_elements:
                              if td.text:
                                  td_text = td.xpath("normalize-space(string())").strip()
                                  row.append(td_text)
 
                           table.append(row)
                           
                       tables.append(table)
                    
                   
                   # Create section object
                   sec_data = {
                       "title": sec_title,
                       "paragraphs": paragraphs,
                       "tables": tables
                   }
                   
                   json_data["sections"].append(sec_data)
          
            path = f'.//back/sec'
            sections = root.findall(path)
            if sections:
                for sec in sections:
                
                   # section title
                   sec_title = None
                   title_element = sec.find('title')
                   if title_element is not None:
                       sec_title = title_element.text.strip()
                       
                   # paragraph texts (either p, or sec/p)
                   paragraphs = []
                       
                   p_elements = sec.findall('p')                   
                   for p in p_elements:
                       if p.text:
                           paragraph_data = { "text" : p.xpath("normalize-space(string())").strip() }
                           paragraphs.append(paragraph_data)
                       
                   # Create section object
                   sec_data = {
                       "title": sec_title,
                       "paragraphs": paragraphs
                   }
                   
                   json_data["sections"].append(sec_data)                   

            
            path = f'.//back/ref-list/ref'
            ref_elements = root.findall(path)
            if ref_elements:
                for ref_element in ref_elements:
                    citation = ref_element.xpath("normalize-space(string())").strip()
                    
                    ref_data = {
                           "citation": citation
                       }
                       
                    link_elements = ref_element.findall(f'.//pub-id[@pub-id-type="doi"]')
                    if link_elements:
                        for link in link_elements:
                           ref_data['doi'] = link.text
    
                    link_elements = ref_element.findall(f'.//ext-link[@ext-link-type="doi"]')
                    if link_elements:
                        for link in link_elements:
                           ref_data['doi'] = link.text.replace('https://doi.org/', '')
                        
                    json_data["references"].append(ref_data)                 

        # TEI --------------------------------------------------------------------------
        if xml_format == "tei":
    
            ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
            
            # title
            path = f'.//tei:filedesc/tei:titlestmt/tei:title'
            elements = root.findall(path, namespaces=ns)
            if elements:
                 if elements[0].text:
                     title = elements[0].text.strip()
                     json_data['title'] = title
                 
            # text
            path = f'.//tei:text/tei:div'
            sections = root.findall(path, namespaces=ns)
            if sections:
                for sec in sections:
                                  
                   # paragraph text
                   paragraphs = []
                       
                   p_elements = sec.findall('tei:p', namespaces=ns)                   
                   for p in p_elements:
                        paragraph_data = { "text" : p.xpath("normalize-space(string())").strip() }
                        paragraphs.append(paragraph_data)
                       
                   # print (paragraphs);              
                   # print ("\n")
                   
                   # Create section object
                   sec_data = {
                       "paragraphs": paragraphs
                   }
                   
                   json_data["sections"].append(sec_data)
                 
            # references
            path = f'.//tei:listbibl/tei:biblstruct'
            ref_elements = root.findall(path, namespaces=ns)
            if ref_elements:
                for ref_element in ref_elements:
                    citation = ref_element.xpath("normalize-space(string())").strip()
                    
                    ref_data = {
                           "citation": citation
                       }
                       
                    link_elements = ref_element.findall(f'.//tei:idno[@type="DOI"]', namespaces=ns)
                    if link_elements:
                        for link in link_elements:
                           ref_data['doi'] = link.text
     
                    json_data["references"].append(ref_data)

        # BioC --------------------------------------------------------------------------
        if xml_format == "bioc":
    
            # title
            path = f'.//document/passage/text'
            elements = root.findall(path)
            if elements and elements[0].text:
                title = elements[0].text.strip()
                json_data['title'] = title
    
    
            # doi
            path = f'.//document/passage/infon[@key="article-id_doi"]'
            elements = root.findall(path)
            if elements and elements[0].text:
                doi = elements[0].text.strip()
                json_data['doi'] = doi
    
            # sections
            sec_data = None
            previous_sec_title = "Unknown"
            paragraphs = []
            
            path = f'.//document/passage'
            sections = root.findall(path)
            if sections:
                for sec in sections:
                   
                   # section title
                   sec_title = None
                   title_element = sec.find(f'infon[@key="section_type"]')
                   if title_element is not None:
                       sec_title = title_element.text.strip()
                       #print(sec_title)
                       
                   if sec_data:
                       if  sec_title and sec_title != previous_sec_title:
                           json_data["sections"].append(sec_data)
                           
                           sec_data = {
                               "title": sec_title,
                               "paragraphs" : []
                           }
                           
                           previous_sec_title = sec_title;
                   else:
                       sec_data = {
                           "title": sec_title,
                           "paragraphs" : []
                       }
                       previous_sec_title = sec_title;
                    
                   p_elements = sec.findall('text')                   
                   for p in p_elements:
                        paragraph_data = { "text" : p.xpath("normalize-space(string())").strip() }
                        sec_data['paragraphs'].append(paragraph_data)
     
            if sec_data:
                if sec_data['title'] == 'REF':
                    json_data["references"].append(sec_data)
                else:
                    json_data["sections"].append(sec_data)
      
             
        # Wiley --------------------------------------------------------------------------
        if xml_format == "wiley":
     
            ns = {'wiley': 'http://www.wiley.com/namespaces/wiley'}
            
            # title
            path = f'.//wiley:contentMeta/wiley:titleGroup/wiley:title'
            #print (path)
            elements = root.findall(path, namespaces=ns)
            if elements and elements[0].text:
                title = elements[0].text.strip()
                json_data['title'] = title
    
            # doi
            path = f'.//wiley:publicationMeta[@level="unit"]/wiley:doi'
            elements = root.findall(path, namespaces=ns)
            if elements and elements[0].text:
                doi = elements[0].text.strip()
                json_data['doi'] = doi
                
            # paragraphs
            path = f'.//wiley:body/wiley:section'
            sections = root.findall(path, namespaces=ns)
            if sections:
                for sec in sections:
                
                   # print ("\n")
            
                   # section title
                   sec_title = None
                   title_element = sec.find(f'wiley:title', namespaces=ns)
                   if title_element is not None:
                       sec_title = title_element.text.strip()
                       #print(sec_title)
                   
                   # paragraph texts (either p, or section/p)
                   paragraphs = []
                   
                   p_elements = sec.findall(f'wiley:p', namespaces=ns)                   
                   for p in p_elements:
                       if p.text:
                           paragraph_data = { "text" : p.xpath("normalize-space(string())").strip() }
                           paragraphs.append(paragraph_data)
    
                   p_elements = sec.findall(f'wiley:section/wiley:p', namespaces=ns)
                   for p in p_elements:
                       if p.text:
                           paragraph_data = { "text" : p.xpath("normalize-space(string())").strip() }
                           paragraphs.append(paragraph_data)
    
                   # print (paragraphs);
                   
                   # Create section object
                   sec_data = {
                       "title": sec_title,
                       "paragraphs": paragraphs
                   }
               
                   json_data["sections"].append(sec_data)
             
            #references
            path = f'.//wiley:bibliography/wiley:bib/wiley:citation'
            ref_elements = root.findall(path, namespaces=ns)
            if ref_elements:
                for ref_element in ref_elements:
                    citation = ref_element.xpath("normalize-space(string())").strip()
                
                    ref_data = {
                        "citation": citation
                    }
                    
                    link_elements = ref_element.findall(f'wiley:url', namespaces=ns)
                    if link_elements:
                        for link in link_elements:
                           ref_data['url'] = link.text
                    
                    
                    json_data["references"].append(ref_data)
     
                
        print ("done file")

        # Save to JSON with same name but .json extension
        json_filename = filename.replace('.xml', '.json')
        json_path = os.path.join(json_folder, json_filename)

        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, indent=2, ensure_ascii=False)

print("Finished processing XML files")
print("\n")

print("Processing JSON")

import re

def value_is_ok(value):
    ok = True
    
    #print (value)
    
    if re.search(r'[\s|,|"|#]', value):
       ok = False
       
    if len(value) > 64:
        ok = False
    
    return ok

def is_data_doi(doi):
    # Check known DOI patterns for data repositories
    patterns = [
        r'10\.6073/pasta',
        r'10\.5061/dryad',
        r'10\.5256/f1000research\.\d+\.d\d+',
        r'10\.15468/dl',
        r'10\.1594/PANGAEA',
        r'10\.5066/[a-zA-Z]',
        r'10\.5281/zenodo',
        r'10\.16904/envidat',
        r'10\.6075/[a-zA-Z0-9]',
    ]
    
    for pattern in patterns:
        if re.search(pattern, doi, re.IGNORECASE):
            return True
            
    return False


def clean_doi(doi):
    doi = re.sub(r'[;|,|\.|\)|>]+$', '', doi)
    doi = re.sub(r'^DOI[:|,]\s*', '', doi, flags=re.IGNORECASE)
    doi = re.sub(r'^https?://(dx\.)?doi.org/', '', doi)
    doi = re.sub(r'#.*$/', '', doi)
    doi = re.sub(r'[\u2010\u2011\u2012\u2013\u2014\u2015]', '-', doi)
    doi = doi.lower()
    doi = 'https://doi.org/' + doi
    
    return doi
    

def extract_dois(text, paragraph, json_data):
    """
    Extracts DOIs from the given text, formats them, and appends them to the paragraph and json_data structures.
    
    Parameters:
        text (str): The text to search for DOIs.
        paragraph (dict): A dictionary with a key 'ids' where DOIs will be appended.
        json_data (dict): A dictionary expected to have a key 'data_citations' where DOIs will also be added.
    """
    pattern = r'((DOI[:|,]\s*|doi:\s*|https?://(dx\.)?doi.org/)?' \
              r'10\.[0-9]{4,}(?:\.[0-9]+)*(?:/|%2F)(?:(?!["&\'])\S)+)'

    matches = re.findall(pattern, text, re.IGNORECASE)

    dois = [match[0] for match in matches]

    for doi in dois:
        doi = clean_doi(doi)
        
        if value_is_ok(doi):

            if paragraph:
                paragraph.setdefault('ids', []).append(doi)

            json_data.setdefault('data_citations', {}).setdefault('doi', [])
            if doi not in json_data['data_citations']['doi']:
                json_data['data_citations']['doi'].append(doi)

def extract_identifiers(text, paragraph, json_data):

    # ok 
    # [genbank, interpro, pfam]
    # [genbank, interpro, pfam, prjna] v7 0.138

    # bad 
    # [genbank gisaid, interpro, pfam, prjna, sra]
    # [biosample chembl genbank interpro, pfam, prjna, pxd]
    # [biosample genbank interpro, pfam, prjna, pxd]
    
    patterns = {

        #'arx'       : r'(E-GEOD-\d+)', # https://www.ebi.ac.uk/biostudies/arrayexpress

        #'biosample' : r'SAM[NED]\w?\d+', # https://registry.identifiers.org/registry/biosample
        
        #'chembl'    : r'(CHEMBL\d+)',
        
        #'empiar'    : r'(EMPIAR-\d{5,})',
        
        # This regex seems to blow up
        #'ensembl'   : r'((ENS[FPTG]\d{11}(\.\d+)?)|(FB\w{2}\d{7})|(Y[A-Z]{2}\d{3}[a-zA-Z](\-[A-Z])?)|([A-Z_a-z0-9]+(\.)?(t)?(\d+)?([a-z])?))',
        
        'genbank'   : r'\b([A-Z]\d{5}|[A-Z]{2}\d{6}|[A-Z]{4,6}\d{8,10}|[A-J][A-Z]{2}\d{5})(?!\.\d+)?\b',
        #'gisaid'    : r'(EPI\d+)',
        #'gxaexpt'   : r'([AEP]-\w{4}-\d+)', # https://registry.identifiers.org/registry/gxa.expt
        
        'interpro'  : r'(IPR\d{6})',
        
        'pfam'      : r'(PF\d{5})',
        'prjna'     : r'(PRJ[DEN][A-Z]\d+)', # https://registry.identifiers.org/registry/bioproject
        #'pxd'       : r'(PXD\d{6})', # https://www.proteomexchange.org	

         # RRID is really just a prefix to an existing identifier,
         # so potentially any thing could have RRID as a prefix
        #'rrid'      : r'(RRID:[A-Z][A-Z0-9_]+)',

        #'sra'       : r'([SED]R[APRSXZ]\d+)', # https://registry.identifiers.org/registry/insdc.sra

    }

    for source, pattern in patterns.items():
        matches = re.findall(pattern, text)
        
        for hit in matches:
            if value_is_ok(hit):
        
                paragraph.setdefault('ids', []).append(hit)

                json_data.setdefault('data_citations', {}).setdefault(source, [])
                if hit not in json_data['data_citations'][source]:
                    json_data['data_citations'][source].append(hit)

rows = []

for filename in os.listdir(json_folder):
    if filename.endswith('.json'):
    
        print (filename)
        
        id = filename.replace('.json', '')
        
        json_path = os.path.join(json_folder, filename)
        
        with open(json_path, 'rb') as f:
            json_data = json.load(f)

        for i, section in enumerate(json_data['sections']):
            for j, paragraph in enumerate(section['paragraphs']):
                if paragraph['text']:
                    paragraph['ids'] = []
                  
                    # do stuff
                    text = paragraph['text']
                    extract_dois(text, paragraph, json_data)
                    extract_identifiers(text, paragraph, json_data)

                # tables
                if section.get('tables'):
                    for i, table in enumerate(section['tables']):
                        for j, row in enumerate(table):
                            for cell in row:
                                text = cell
                                # something about text from tables caused the scoring to fail :(
                                #extract_identifiers(text, None, json_data)
                            #print ("\n")

        for reference in json_data['references']:
            doi = reference.get('doi')
            if doi:
                doi = clean_doi(doi)
                if value_is_ok(doi):
                    if is_data_doi(doi):
                        json_data.setdefault('data_citations', {}).setdefault('doi', [])
                        if doi not in json_data['data_citations']['doi']:
                            json_data['data_citations']['doi'].append(doi)       
               
        print (json.dumps(json_data['data_citations'], indent=4))
        print("\n")
          
        citations = json_data['data_citations'];
          
        for data_type, values in citations.items():
            for value in values:                
                match data_type:
                    case "doi":
                        rows.append([id, value, 'Primary'])
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


