import os
import re
import json
from lxml import etree
import csv
import sys

# Define input and output directories
if os.getenv('KAGGLE_KERNEL_RUN_TYPE'):
    xml_folder = '/kaggle/input/make-data-count-finding-data-references/test/XML'
    #xml_folder = '/kaggle/input/make-data-count-finding-data-references/train/XML'
    json_folder = '/kaggle/temp/'
else:
    xml_folder = 'train/XML'
    json_folder = 'json'

    #xml_folder = 'testxml'
    #json_folder = 'testjson'

# v16 is False, False, False
DO_TABLES   = True
DO_BACK     = False # failed
DO_BACK1    = True
DO_BACK2A   = False
DO_BACK2B   = True
DO_BACK3    = True #works
DO_ENTITIES = True
DO_SANITISE = True

DO_PATTERNS_1 = True # basic patterns
DO_PATTERNS_2 = True
DO_PATTERNS_3 = True
DO_PATTERNS_4 = True
DO_PATTERNS_5 = True
DO_BIOSAMPLE  = True

# [genbank, interpro, pfam, prjna]

# FTFT failed
# FFFT 0.90
# FFTT 0.170
# TFTT 0.235
# TF(FFF)TT P3 0.284 (worse than P1)
# TF(FFT)TT P3 0.284 (add BACK3 no change to score 0.284)
# TF(FFT)TT P3 0.300 (delete GenBank {4} pattern, 0.300)
# TF(TFT)TT P3 0.308 (add BACK1, 0.308)
# TF(TFT)TT P3 0.308 (treat GBIF DOIs as secondary, 0.308 - no change in score - bug in code)
# TF(TFFT)TT P3 0.305 v 37
# TF(TFTT)TT P3 0.299 v 38 DO_BACK2B
# TF(TTTT)TT P3 DO_BACK2A and DO_BACK2B failed (DO_BACK2A is problem)

# TF(TFT)TT P5 Biosample primary 0.359
# TF(TFT)TT P5 Biosample secondary 0.310


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
        
# Get spaced text
def get_text_with_spaces(elem):
    parts = []

    if elem.text:
        parts.append(elem.text)

    for child in elem:
        parts.append(get_text_with_spaces(child))
        if child.tail:
            parts.append(child.tail)

    return ' '.join(part.strip() for part in parts if part and part.strip())
        

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
                           #paragraph_data = { "text" : p.xpath("normalize-space(string())").strip() }
                           paragraph_data = { "text" : get_text_with_spaces(p) }
                           paragraphs.append(paragraph_data)
    
                   p_elements = sec.findall('sec/p')
                   for p in p_elements:
                       if p.text:
                           #paragraph_data = { "text" : p.xpath("normalize-space(string())").strip() }
                           paragraph_data = { "text" : get_text_with_spaces(p) }                           
                           paragraphs.append(paragraph_data)
                   
                   # print (paragraphs);
                   # print ("\n")

                   # tables
                   tables = []
                   if DO_TABLES:
                                        
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
                   
            # No sections ----------------------------------------------------------------
            no_sections = False
            path = f'.//body/p'
            p_elements = root.findall(path)
            if p_elements:
            
                # One big section!
                # section title
                sec_title = 'Body'
           
                paragraphs = []
            
                for p in p_elements: 
                    if p.text:
                        #paragraph_data = { "text" : p.xpath("normalize-space(string())").strip() }
                        paragraph_data = { "text" : get_text_with_spaces(p) }
                        paragraphs.append(paragraph_data)
                    
                   
                # look for tables
                tables = []
                if DO_TABLES:
                                    
                  t_elements = root.findall(f'.//body/table-wrap/table')
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
                
 
          
            # We may have sections, etc. in the back -------------------------------------
            if DO_BACK1:
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
                               #paragraph_data = { "text" : p.xpath("normalize-space(string())").strip() }
                               paragraph_data = { "text" : get_text_with_spaces(p) }
                               paragraphs.append(paragraph_data)
                       
                       # Create section object
                       sec_data = {
                           "title": sec_title,
                           "paragraphs": paragraphs
                       }
                   
                       json_data["sections"].append(sec_data)  
                   
            # 10.3390_rs12121957
            # need to think how we indicate that these are back pages and
            # hence likely to be primary      
            # Note the use of tree.xpath to do the query, we need this for optional
            # queries with multiple paths 
            if DO_BACK2A:           
                path = f'.//back/ack'
                sections = tree.xpath(path)
                if sections:
                    for sec in sections:
                
                       # section title
                       sec_title = None
                       title_element = sec.find('title')
                       if title_element is not None:
                           sec_title = title_element.text.strip()
                       
                       # paragraph texts
                       paragraphs = []
                       
                       p_elements = sec.findall('p')                   
                       for p in p_elements:
                           if p.text:
                               #paragraph_data = { "text" : p.xpath("normalize-space(string())").strip() }
                               paragraph_data = { "text" : get_text_with_spaces(p) }
                               paragraphs.append(paragraph_data)
                       
                       # Create section object
                       sec_data = {
                           "title": sec_title,
                           "paragraphs": paragraphs
                       }
                   
                       #print (sec_data)
                   
                       json_data["sections"].append(sec_data)                   

            if DO_BACK2B:           
                path = f'.//back/notes'
                sections = tree.xpath(path)
                if sections:
                    for sec in sections:
                
                       # section title
                       sec_title = None
                       title_element = sec.find('title')
                       if title_element is not None:
                           sec_title = title_element.text.strip()
                       
                       # paragraph texts
                       paragraphs = []
                       
                       p_elements = sec.findall('p')                   
                       for p in p_elements:
                           if p.text:
                               #paragraph_data = { "text" : p.xpath("normalize-space(string())").strip() }
                               paragraph_data = { "text" : get_text_with_spaces(p) }
                               paragraphs.append(paragraph_data)
                       
                       # Create section object
                       sec_data = {
                           "title": sec_title,
                           "paragraphs": paragraphs
                       }
                   
                       #print (sec_data)
                   
                       json_data["sections"].append(sec_data)                   

            # 10.7717_peerj.10452 
            # need to think how we indicate that these are back pages and
            # hence likely to be primary 
            if DO_BACK3:                 
                path = f'.//back/sec/fn-group'
                sections = root.findall(path)
                if sections:
                    for sec in sections:
                
                       # section title
                       sec_title = None
                       title_element = sec.find('title')
                       if title_element is not None:
                           if title_element.text:
                               sec_title = title_element.text.strip()
                       
                       # paragraph texts
                       paragraphs = []
                       
                       p_elements = sec.findall('fn/p')                   
                       for p in p_elements:
                           if p.text:
                               #paragraph_data = { "text" : p.xpath("normalize-space(string())").strip() }
                               paragraph_data = { "text" : get_text_with_spaces(p) }
                               paragraphs.append(paragraph_data)
                       
                       # Create section object
                       sec_data = {
                           "title": sec_title,
                           "paragraphs": paragraphs
                       }
                   
                       #print (sec_data)
                   
                       json_data["sections"].append(sec_data)                   

            # references, sometimes these include citations of datasets
            path = f'.//back/ref-list/ref'
            ref_elements = root.findall(path)
            if ref_elements:
                for ref_element in ref_elements:
                    #citation = ref_element.xpath("normalize-space(string())").strip()
                    citation = get_text_with_spaces(ref_element)
                    
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
                    
            # will need to handle float-groups e.g. 10.3390_v11060565 
            # as we make have tables there
            path = f'.//floats-group'
            float_elements = root.findall(path)
            if float_elements:
                for float_group in float_elements:
                   # tables
                   tables = []
                   
                   t_elements = float_group.findall(f'.//table')
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
                   #print (tables) 
                   
                   sec_data = {
                       "title": "floats",
                       "paragraphs": [],
                       "tables": tables
                   }
                   json_data["sections"].append(sec_data)   
   
               

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
                        #paragraph_data = { "text" : p.xpath("normalize-space(string())").strip() }
                        paragraph_data = { "text" : get_text_with_spaces(p) }
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
                    #citation = ref_element.xpath("normalize-space(string())").strip()
                    citation = get_text_with_spaces(ref_element)
                    
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
                        #paragraph_data = { "text" : p.xpath("normalize-space(string())").strip() }
                        paragraph_data = { "text" : get_text_with_spaces(p) }
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
                           #paragraph_data = { "text" : p.xpath("normalize-space(string())").strip() }
                           paragraph_data = { "text" : get_text_with_spaces(p) }
                           paragraphs.append(paragraph_data)
    
                   p_elements = sec.findall(f'wiley:section/wiley:p', namespaces=ns)
                   for p in p_elements:
                       if p.text:
                           #paragraph_data = { "text" : p.xpath("normalize-space(string())").strip() }
                           paragraph_data = { "text" : get_text_with_spaces(p) }
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
                    #citation = ref_element.xpath("normalize-space(string())").strip()
                    citation = { "text" : get_text_with_spaces(ref_element) }
                
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

    if value == "":
       ok = False    
       
    if len(value) > 64:
        ok = False
    
    return ok
    
def clean_table_cell_value(value):
    if re.match(r'[^A-Z][a-zA-Z0-9-]+$', value):
       return value
    else:
        return value

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


def clean_doi(doi):
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

def extract_identifiers(text, block, json_data):

    # ok 
    # [genbank, interpro, pfam]
    # [genbank, interpro, pfam, prjna] v7 0.138

    # bad 
    # [genbank gisaid, interpro, pfam, prjna, sra]
    # [biosample chembl genbank interpro, pfam, prjna, pxd]
    # [biosample genbank interpro, pfam, prjna, pxd]
    
    patterns = {

        #'arxe'       : r'E-GEOD-\d+', # https://www.ebi.ac.uk/biostudies/arrayexpress
        #'arxp'       : r'E-PROT-\d+', # https://www.ebi.ac.uk/biostudies/arrayexpress

        #'biosample' : r'SAM[NED]\w?\d+', # https://registry.identifiers.org/registry/biosample
        
        #'chembl'    : r'CHEMBL\d+',
        
        #'empiar'    : r'EMPIAR-\d{5,}',
        
        # This regex seems to blow up
        #'ensembl'   : r'((ENS[FPTG]\d{11}(\.\d+)?)|(FB\w{2}\d{7})|(Y[A-Z]{2}\d{3}[a-zA-Z](\-[A-Z])?)|([A-Z_a-z0-9]+(\.)?(t)?(\d+)?([a-z])?))',
        
        #'genbank'   : r'\b([A-Z]\d{5}|[A-Z]{2}\d{6}|[A-Z]{4,6}\d{8,10}|[A-J][A-Z]{2}\d{5})(?!\.\d+)?\b',
        
        'genbank'   : r'\b([A-Z]\d{5}|[A-Z]{2}\d{6})\b',
        
        #'gisaid'    : r'EPI\d+',
        #'gxaexpt'   : r'([AEP]-\w{4}-\d+)', # https://registry.identifiers.org/registry/gxa.expt
        
        'interpro'  : r'IPR\d{6}',
        
        'pfam'      : r'PF\d{5}',
        'prjna'     : r'PRJ[DEN][A-Z]\d+', # https://registry.identifiers.org/registry/bioproject
        #'pxd'       : r'PXD\d{6}', # https://www.proteomexchange.org    

         # RRID is really just a prefix to an existing identifier,
         # so potentially any thing could have RRID as a prefix
        #'rrid'      : r'(RRID:[A-Z][A-Z0-9_]+)',

        #'sra'       : r'[SED]R[APRSXZ]\d+', # https://registry.identifiers.org/registry/insdc.sra

    }

    if DO_PATTERNS_1:
        patterns = {
            'genbank'   : r'\b([A-Z]\d{5}|[A-Z]{2}\d{6})\b',
            'interpro'  : r'IPR\d{6}',
            'pfam'      : r'PF\d{5}',
            'prjna'     : r'PRJ[DEN][A-Z]\d+', # https://registry.identifiers.org/registry/bioproject
        }      

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
            #'genbank'   : r'\b([A-Z]\d{5}|[A-Z]{2}\d{6})\b',
            'genbank'   : r'\b([A-Z]{2}\d{6})\b', # just 2 letters + 6 digits
            
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
        matches = re.findall(pattern, text)
        
        for hit in matches:
            if not isinstance(hit, str):
               hit = hit[0]
            
            if value_is_ok(hit):
        
                if block:
                   block.setdefault('ids', []).append(hit)

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
                    if DO_ENTITIES:
                        extract_identifiers(text, paragraph, json_data)

            # tables
            if section.get('tables'):
                for i, table in enumerate(section['tables']):
                    for j, row in enumerate(table):
                        for cell in row:
                            text = cell
                            text = clean_table_cell_value(text)
                            if text:                                
                                # something about text from tables caused the scoring to fail :(
                                if DO_ENTITIES:
                                    extract_identifiers(text, None, json_data)
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
                if DO_SANITISE:
                   value = re.sub(r'[^\x00-\x7F]|[\r\n",]', '', value) 
                   #if re.search(r'[^\x00-\x7F]|[\r\n",]', value):
                   #    print("BADNESS ", value) 
                   #    sys.exit() 
                match data_type:
                    # Assume DOIs are only added if in body or back, not references
                    # unless they match known data repos
                    case "doi":
                        if re.search(r'10\.15468/dl', value, re.IGNORECASE): 
                            # GBIF downloads are secondary
                            rows.append([id, value, 'Secondary'])
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

