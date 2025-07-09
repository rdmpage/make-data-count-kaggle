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

    xml_folder = 'explore'
    json_folder = 'explore'

# Ensure the output directory exists
os.makedirs(json_folder, exist_ok=True)

# Process XML and convert to simple JSON

# Regular expression pattern to detect XML type (customize as needed)
xml_type_pattern = re.compile(r'<\?xml[^>]*\?>|<!DOCTYPE[^>]*>', re.IGNORECASE)

#-----------------------------------------------------------------------------------------     
# Helper function to extract namespaces
def get_namespaces(xml_file):
    try:
        # Extract namespaces declared in the XML file
        with open(xml_file, 'rb') as f:
            for _, elem in etree.iterparse(f, events=('start-ns',)):
                yield elem
    except Exception:
        return
 
#-----------------------------------------------------------------------------------------     
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
    
#----------------------------------------------------------------------------------------- 
def clean_table_cell_value(value):
    if re.match(r'[^A-Z][a-zA-Z0-9-\.]+$', value):
       return value
    else:
        return value    
    
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
                
#        if xml_format == 'unknown':
#            print (filename, " format unknown", header_text)
        
        tree = etree.parse(xml_path)
        root = tree.getroot()     
           
        # Create JSON document
        doc = {
           'id' : filename.replace('.xml', ''),
           'source_type' : 'xml',
           'xml_type' : xml_format,
           'title' : None,
           'doi' : None,
           'sections' : [],
           'references' : [],
           'data_citations' : {}
        }
        
         
        # JATS ---------------------------------------------------------------------------
        if xml_format == "jats":
                      
            # title for article
            title = None
            path = f'.//front/article-meta/title-group/article-title'
            elements = root.findall(path)
            if elements:
                 if elements[0].text:
                     title = elements[0].text.strip()
                     doc['title'] = title
                 
            # doi for article
            doi = None
            path = f'.//front/article-meta/article-id[@pub-id-type="doi"]'
            elements = root.findall(path)
            if elements:
                if elements[0].text:
                    doi = elements[0].text.strip()
                    doc['doi'] = doi
                 
            # PLoS may have some stuff at the front
            path = f'.//front/article-meta/custom-meta-group/custom-meta[@id="data-availability"]/meta-value'
            meta = root.find(path)
            if meta is not None:
                
                paragraph = { 
                    "text" : meta.xpath("normalize-space(string())").strip(),
                    "annotations": []
                }
                
                sec_data = {
                    "title": None,
                    "type" : "data-availability",
                    "paragraphs": [paragraph],
                    "tables": []
                }
           
                doc["sections"].append(sec_data)
                                   
            # Usually we have body/sec/text
            path = f'.//body/sec'
            sections = root.findall(path)
            if sections:
                for sec in sections:
                
                   type = None
                   
                   # section title
                   sec_title = None
                   title_element = sec.find('title')
                   if title_element is not None:
                       if title_element.text:
                           sec_title = title_element.text.strip()
                       
                       #print(sec_title)
                       
                   # text may be further nested, i.e. sec/p/sec/p
                   # paragraph texts (either p, or sec/p)
                   paragraphs = []
                   
                   #print ("body/sec/p");
                   #print (paragraphs);
                       
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
                   
                   #print ("body/sec/sec/p");
                   #print (paragraphs);
                   

                   # tables /body/sec/table
                   tables = []
                                    
                   t_elements = sec.findall(f'.//table')
                   for t in t_elements:
                       table = { "rows" : []}
                   
                       tr_elements = t.findall('thead/tr')
                       for tr in tr_elements:
                           row = [];
                           th_elements = tr.findall('th')
                           for th in th_elements:
                              if th.text:
                                  th_text = th.xpath("normalize-space(string())").strip()
                                  row.append(th_text)
                           table['rows'].append(row)
                    

                       tr_elements = t.findall('tbody/tr')
                       for tr in tr_elements:
                           row = [];
                           td_elements = tr.findall('td')
                           for td in td_elements:
                              if td.text:
                                  td_text = td.xpath("normalize-space(string())").strip()
                                  row.append(td_text)
 
                           table['rows'].append(row)
                        
                       tables.append(table)
                   
                   # Create section object
                   sec_data = {
                       "title": sec_title,
                       "type" : type,
                       "paragraphs": paragraphs,
                       "tables": tables
                   }
                   
                   doc["sections"].append(sec_data)
                   
            # Some JATS files such as 10.1002_chem.202000235 have no sections, so it is
            # body/p         
            path = f'.//body/p'
            p_elements = root.findall(path)
            if p_elements:
            
                type = None
            
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

            t_elements = root.findall(f'.//body/table-wrap/table')
            for t in t_elements:
                table = { "rows" : []}
                 
                tr_elements = t.findall('thead/tr')
                for tr in tr_elements:
                    row = [];
                    th_elements = tr.findall('th')
                    for th in th_elements:
                        if th.text:
                            th_text = th.xpath("normalize-space(string())").strip()
                            row.append(th_text)
                    table['rows'].append(row)

                tr_elements = t.findall('tbody/tr')
                for tr in tr_elements:
                    row = [];
                    td_elements = tr.findall('td')
                    for td in td_elements:
                        if td.text:
                            td_text = td.xpath("normalize-space(string())").strip()
                            row.append(td_text)

                        table['rows'].append(row)
                       
                    tables.append(table)
                   
                # Create section object
                sec_data = {
                       "title": sec_title,
                       "type" : type,
                       "paragraphs": paragraphs,
                       "tables": tables
                   }

                doc["sections"].append(sec_data)
                
            # We may have sections, etc. in the back -------------------------------------
            path = f'.//back/sec'
            sections = root.findall(path)
            if sections:
                for sec in sections:
                  
                   type = None
                   
                   # section title
                   sec_title = None
                   title_element = sec.find('title')
                   if title_element is not None:
                       if title_element.text:
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
                       "type" : type,
                       "paragraphs": paragraphs
                   }
               
                   doc["sections"].append(sec_data)  
                                               
                   # eLife may have nested sec with data
                   sec_data = sec.find(f'sec[@sec-type="datasets"]');
                   if sec_data is not None:
                       sec_title = None
                       title_element = sec_data.find('title')
                       if title_element is not None:
                           if title_element.text:
                               sec_title = title_element.text.strip()
                   
                       p_elements = sec.findall('sec[@sec-type="datasets"]/p');
                       if p_elements:                   
                           paragraphs = []
                           for p in p_elements:
                               if p.text:     
                                   paragraph_data = { "text" : get_text_with_spaces(p) }
                                   paragraphs.append(paragraph_data)
                       
                           sec_data = {
                              "title": None,
                              "type" : "datasets",
                              "paragraphs": paragraphs
                           }
                           doc["sections"].append(sec_data)
                   
                  
            # 10.3390_rs12121957
            #if os.getenv('KAGGLE_KERNEL_RUN_TYPE') is None: 
            if True:
                # This particular XPath originally broke Kaggle
                # but this was because I did not check for the existence of .text
                # fields before using them :O Discovered this when loading XML
                # from outside the competition training set
                path = f'.//back/ack'
                sections = tree.xpath(path)
                if sections:
                    for sec in sections:
                
                       type = None
                       
                       # section title
                       sec_title = None
                       title_element = sec.find('title')
                       if title_element is not None:
                           if title_element.text:
                               sec_title = title_element.text.strip()
                       
                       # paragraph texts
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
                               
                       
                       # Create section object
                       sec_data = {
                           "title": sec_title,
                           "type" : type,
                           "paragraphs": paragraphs
                       }
                   
                       #print (sec_data)
                   
                       doc["sections"].append(sec_data)                   

            path = f'.//back/notes'
            sections = tree.xpath(path)
            if sections:
                for sec in sections:
            
                   type = None
                   
                   # section title
                   sec_title = None
                   title_element = sec.find('title')
                   if title_element is not None:
                       if title_element.text:
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
                       "type" : type,
                       "paragraphs": paragraphs
                   }
               
                   #print (sec_data)
               
                   doc["sections"].append(sec_data)                   

            # 10.7717_peerj.10452 
            # need to think how we indicate that these are back pages and
            # hence likely to be primary 
            path = f'.//back/sec/fn-group'
            sections = root.findall(path)
            if sections:
                for sec in sections:

                   type = None
            
                   # section title
                   sec_title = None
                   title_element = sec.find('title')
                   if title_element is not None:
                       if title_element.text:
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
                       "type": type,
                       "paragraphs": paragraphs
                   }
               
                   #print (sec_data)
               
                   doc["sections"].append(sec_data)  
                   
            # appendices
            path = f'.//back/app-group/app'
            sections = tree.xpath(path)
            if sections:
                for sec in sections:
            
                   type = None
                   
                   # section title
                   sec_title = None
                   title_element = sec.find('title')
                   if title_element is not None:
                       if title_element.text:
                           if title_element.text:
                               sec_title = title_element.text.strip()
                   
                   # paragraph texts
                   paragraphs = []
                   
#                   p_elements = sec.findall('p')                   
#                   for p in p_elements:
#                       if p.text:
#                           #paragraph_data = { "text" : p.xpath("normalize-space(string())").strip() }
#                           paragraph_data = { "text" : get_text_with_spaces(p) }
#                           paragraphs.append(paragraph_data)
#                   

                   # tables 
                   tables = []
                                    
                   t_elements = sec.findall(f'.//table')
                   for t in t_elements:
                       table = { "rows" : []}
                   
                       tr_elements = t.findall('thead/tr')
                       for tr in tr_elements:
                           row = [];
                           th_elements = tr.findall('th')
                           for th in th_elements:
                              if th.text:
                                  th_text = th.xpath("normalize-space(string())").strip()
                                  row.append(th_text)
                           table['rows'].append(row)
                    

                       tr_elements = t.findall('tbody/tr')
                       for tr in tr_elements:
                           row = [];
                           td_elements = tr.findall('td')
                           for td in td_elements:
                              if td.text:
                                  td_text = td.xpath("normalize-space(string())").strip()
                                  row.append(td_text)
 
                           table['rows'].append(row)
                        
                       tables.append(table)
                   
                   

                   # Create section object
                   sec_data = {
                       "title": sec_title,
                       "type" : type,
                       "paragraphs": paragraphs,
                       "tables": tables
                   }
               
                   #print (sec_data)
               
                   doc["sections"].append(sec_data)                   


            #-----------------------------------------------------------------------------
            # figures
            path = f'.//fig'
            sections = root.findall(path)
            if sections:
                for sec in sections:
                
                   type = "caption"
                   
                   # section title
                   sec_title = None
                   title_element = sec.find('label')
                   if title_element is not None:
                       if title_element.text:
                           sec_title = title_element.text.strip()
                       
                   paragraphs = []
                                          
                   p_elements = sec.findall('caption/p')                   
                   for p in p_elements:
                       if p.text:
                           paragraph_data = { "text" : get_text_with_spaces(p) }
                           paragraphs.append(paragraph_data)

                   # Create section object
                   sec_data = {
                       "title": sec_title,
                       "type" : type,
                       "paragraphs": paragraphs
                   }
                   
                   doc["sections"].append(sec_data)
 
            #-----------------------------------------------------------------------------
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
                        
                    doc["references"].append(ref_data) 
                    
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
                       table = { "rows" : []}
                       
                       tr_elements = t.findall('thead/tr')
                       for tr in tr_elements:
                           row = [];
                           th_elements = tr.findall('th')
                           for th in th_elements:
                              if th.text:
                                  th_text = th.xpath("normalize-space(string())").strip()
                                  row.append(th_text)
                           table['rows'].append(row)
                       
 
                       tr_elements = t.findall('tbody/tr')
                       for tr in tr_elements:
                           row = [];
                           td_elements = tr.findall('td')
                           for td in td_elements:
                              if td.text:
                                  td_text = td.xpath("normalize-space(string())").strip()
                                  row.append(td_text)
 
                           table['rows'].append(row)
                           
                       tables.append(table)
                   #print (tables) 
                   
                   sec_data = {
                       "title": "floats",
                       "type" : None,
                       "paragraphs": [],
                       "tables": tables
                   }
                   doc["sections"].append(sec_data)   
   
               

        # TEI --------------------------------------------------------------------------
        if xml_format == "tei":
    
            ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
            
            # title
            path = f'.//tei:filedesc/tei:titlestmt/tei:title'
            elements = root.findall(path, namespaces=ns)
            if elements:
                 if elements[0].text:
                     title = elements[0].text.strip()
                     doc['title'] = title
                 
            # text
            path = f'.//tei:text/tei:div'
            sections = root.findall(path, namespaces=ns)
            if sections:
                for sec in sections:
                                  
                   type = None
                   
                   # often in TEI files the section title is the the first child of the
                   # div element, i.e. <div>title<p>
                   first_text = sec.xpath('text()[1]');
                   if first_text:
                       title = first_text[0]
                   
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
                       "title" : title,
                       "type" : type,
                       "paragraphs": paragraphs
                   }
                   
                   doc["sections"].append(sec_data)
                 
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
     
                    doc["references"].append(ref_data)

        # BioC --------------------------------------------------------------------------
        if xml_format == "bioc":
    
            # title
            path = f'.//document/passage/text'
            elements = root.findall(path)
            if elements and elements[0].text:
                title = elements[0].text.strip()
                doc['title'] = title
    
    
            # doi
            path = f'.//document/passage/infon[@key="article-id_doi"]'
            elements = root.findall(path)
            if elements and elements[0].text:
                doi = elements[0].text.strip()
                doc['doi'] = doi
    
            # sections
            sec_data = None
            previous_sec_title = "Unknown"
            paragraphs = []
            
            path = f'.//document/passage'
            sections = root.findall(path)
            if sections:
                for sec in sections:
                   
                   type = None
                   
                   # section title
                   sec_title = None
                   title_element = sec.find(f'infon[@key="section_type"]')
                   if title_element is not None:
                       if title_element.text:
                           sec_title = title_element.text.strip()
                           sec_title = sec_title.rstrip('\n')
                       
                   if sec_data:
                       if  sec_title and sec_title != previous_sec_title:
                           doc["sections"].append(sec_data)
                           
                           sec_data = {
                               "title": sec_title,
                               "type" : type,
                               "paragraphs" : []
                           }
                           
                           previous_sec_title = sec_title;
                   else:
                       sec_data = {
                           "title": sec_title,
                           "type" : type,
                           "paragraphs" : []
                       }
                       previous_sec_title = sec_title;
                    
                   p_elements = sec.findall('text')                   
                   for p in p_elements:
                        #paragraph_data = { "text" : p.xpath("normalize-space(string())").strip() }
                        paragraph_data = { "text" : get_text_with_spaces(p) }
                        sec_data['paragraphs'].append(paragraph_data)
     
            if sec_data:
                doc["sections"].append(sec_data)
      
             
        # Wiley --------------------------------------------------------------------------
        if xml_format == "wiley":
     
            ns = {'wiley': 'http://www.wiley.com/namespaces/wiley'}
            
            # title
            path = f'.//wiley:contentMeta/wiley:titleGroup/wiley:title'
            #print (path)
            elements = root.findall(path, namespaces=ns)
            if elements and elements[0].text:
                title = elements[0].text.strip()
                doc['title'] = title
    
            # doi
            path = f'.//wiley:publicationMeta[@level="unit"]/wiley:doi'
            elements = root.findall(path, namespaces=ns)
            if elements and elements[0].text:
                doi = elements[0].text.strip()
                doc['doi'] = doi
                
            # paragraphs
            path = f'.//wiley:body/wiley:section'
            sections = root.findall(path, namespaces=ns)
            if sections:
                for sec in sections:
                
                   type = None
            
                   # section title
                   sec_title = None
                   title_element = sec.find(f'wiley:title', namespaces=ns)
                   if title_element is not None:
                       if title_element.text:
                           sec_title = title_element.text.strip()
                       
                   # Wiley may include type of section as an attribute
                   if sec.get('type'):
                       type = sec.get('type')                       
                                          
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
                       "type" : type,
                       "paragraphs": paragraphs
                   }
               
                   doc["sections"].append(sec_data)
                   
            #figures
            path = f'.//wiley:figure'
            sections = root.findall(path, namespaces=ns)
            if sections:
                for sec in sections:
                
                   type = "caption"
            
                   # section title
                   sec_title = "Figure"
                                          
                   # treat caption as paragraph
                   paragraphs = []
                   
                   p_elements = sec.findall(f'wiley:caption', namespaces=ns)                   
                   for p in p_elements:
                       if p.text:
                           paragraph_data = { "text" : get_text_with_spaces(p) }
                           paragraphs.append(paragraph_data)
                   # Create section object
                   sec_data = {
                       "title": sec_title,
                       "type" : type,
                       "paragraphs": paragraphs
                   }
               
                   doc["sections"].append(sec_data)            
             
            #references
            path = f'.//wiley:bibliography/wiley:bib/wiley:citation'
            ref_elements = root.findall(path, namespaces=ns)
            if ref_elements:
                for ref_element in ref_elements:
                    #citation = ref_element.xpath("normalize-space(string())").strip()
                    citation = get_text_with_spaces(ref_element)
                
                    ref_data = {
                        "citation": citation
                    }
                    
                    link_elements = ref_element.findall(f'wiley:url', namespaces=ns)
                    if link_elements:
                        for link in link_elements:
                           ref_data['url'] = link.text
                    
                    
                    doc["references"].append(ref_data)
                     
        print ("done file")

        # Save to JSON with same name but .json extension
        json_filename = filename.replace('.xml', '.json')
        json_path = os.path.join(json_folder, json_filename)

        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(doc, json_file, indent=2, ensure_ascii=False)

print("Finished processing XML files")

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
def find_datasets(element, text):

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
        'insdcgca'    : r'(GCA_[0-9]{9}(\.[0-9]+)?)', # insdc.gca
        'interpro'    : r'IPR\d{6}',                     
        'nm'          : r'(N[CM]_?\d{6}(\.[0-9]+)?)', # added ? after _ because eLife sometimes misses the underscore. https://www.ncbi.nlm.nih.gov/books/NBK21091/table/ch18.T.refseq_accession_numbers_and_mole/?report=objectonly
        'pdb'         : r'\b((PDB(\s*ID)?:?\s*)?[0-9][A-Za-z][A-Za-z0-9]{2})\b', # PDB, likely lots of false hits unless we include prefix        
        'pfam'        : r'(PF\d{5}(.\d{1,2})?)', # PFAM seems to have versions, e.g. PF01493.23)   
        'prjna'       : r'PRJ[DEN][A-Z]\d+', # https://registry.identifiers.org/registry/bioproject
        'pxd'         : r'PXD\d{6}', # https://www.proteomexchange.org    
        'sra'         : r'[SED]R[APRSXZ]\d+', # https://registry.identifiers.org/registry/insdc.sra
        'up'          : r'UP\d{9}', # https://www.uniprot.org/proteomes/UP000006548

        'uniprot'     : r'\b([A-N,R-Z][0-9]([A-Z][A-Z, 0-9][A-Z, 0-9][0-9]){1,2})|([O,P,Q][0-9][A-Z, 0-9][A-Z, 0-9][A-Z, 0-9][0-9])(\.\d+)?\b', # https://registry.identifiers.org/registry/uniprot
    
        # https://registry.identifiers.org/registry/insdc
        #'insdc'     : r'\b([A-Z]\d{5}|[A-Z]{2}\d{6}|[A-Z]{4,6}\d{8,10}|[A-J][A-Z]{2}\d{5})(\.\d+)?\b',
        'genbank'    : r'\b(A[B-HJ-MPUX-Y]|B[AC-DS-TVX]|C[HMPR-UY]|D[DF-GP-QS]|E[FM-NP-QUZ]|F[JM-RX]|G[F-GLQU]|H[E-GMP-Q]|J[FH-ILN-RT-X]|K[A-FI-NP-RT-VX-Z]|L[AC-EH-KM-NRT]|M[F-HK-LNT-UWZ]|O[DK-NP-RU-VX-Z]|P[P-Q])\d{6}(\.\d+)?\b',
    }   
    
    for source, pattern in patterns.items():
        for match in re.finditer(pattern, text):
            #print (source, " ", match.group())
            # sanity check
            if value_is_ok(match.group()):
                element['annotations'].append(make_annotation(match, text, source))
 
#-----------------------------------------------------------------------------------------

# process JSON finding data mentions, store text coordinates, etc.

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
            
        #---------------------------------------------------------------------------------
        # classify sections (to help with citation typing)
        for i, section in enumerate(doc['sections']):
           if section['type']:
              #print ("Type=", section['type'])
              
              # Wiley (and we may have added these labels to other formats)
              # ['acknowledgments', 'discussion', 'conclusions', 'methods', 
              # 'materialsAndMethods', 'results', 'conflictOfInterest', 'openResearch']
              
              # JATS 'datasets'
             
              match section['type']:
                  case 'acknowledgments':
                      section['type'] = 'Acknowledgements'

                  case 'caption':
                      section['type'] = 'Caption'   
                      
                  case 'conclusions':
                      section['type'] = 'Conclusion'   
                      
                  case 'conflictOfInterest':
                      section['type'] = 'ConflictOfInterest' # I made this one up
                      
                  case 'discussion':
                      section['type'] = 'Discussion'
                      
                  case 'materialsAndMethods':
                      section['type'] = 'Methods'
                      
                  case 'methods':
                      section['type'] = 'Methods'
                                            
                  case 'results':
                      section['type'] = 'Results'
                                            
                  case 'openResearch':
                      section['type'] = 'DatasetDescription'
                      
                  # eLife
                  case 'datasets':
                      section['type'] = 'DatasetDescription'
 
                  # PLoS
                  case 'data-availability':
                      section['type'] = 'DatasetDescription'
                      
                  case _:
                      section['type'] = 'Unknown'               
           
           else:
              if section['title']:
                 title = section['title']
                 
                 # match to Wiley typology (which we use because we will already have some articles from Wiley)
                  
                 # match to The Discourse Elements Ontology (DEO)
                 # https://sparontologies.github.io/deo/current/deo.html
                 
                 # acknowledgements  acknowledgements  author contribution  background  
                 # bibliographic reference  biography  caption  conclusion  conclusion  
                 # contribution  data  dataset description  dedication  discourse 
                 # element  discussion  discussion  epilogue  evaluation  external 
                 # resource description  future work  introduction  introduction  
                 # legend  materials  methods  methods  model  motivation  postscript  
                 # problem statement  prologue  reference  related work  results  
                 # results  scenario  supplementary information description 

                 if re.search(r'^Acknowledge?ment', title, re.IGNORECASE):
                     section['type'] = 'Acknowledgements' 

                 if re.search(r'^Concl(usion)', title, re.IGNORECASE):
                     section['type'] = 'Conclusion' 

                 if re.search(r'^Discuss(ion)', title, re.IGNORECASE):
                     section['type'] = 'Discussion' 
                     
                 if re.search(r'^Data\s+(accessibility|archiving|availability|resources)', title, re.IGNORECASE):
                     section['type'] = 'DatasetDescription' 

                 if re.search(r'^Databases', title, re.IGNORECASE):
                     section['type'] = 'DatasetDescription' 
 
                 # Idiosyncratic labels for data------------------------------------------

                 # 10.7717_peerj.10452
                 if re.search(r'^DNA Deposition', title, re.IGNORECASE):
                     section['type'] = 'DatasetDescription' 

                 # 10.1186_s12866-020-01863-y
                 if re.search(r'^Availability of data and materials', title, re.IGNORECASE):
                     section['type'] = 'DatasetDescription' 

                 # 10.1186_s40793-015-0095-9
                 if re.search(r'^Genome sequencing information', title, re.IGNORECASE):
                     section['type'] = 'DatasetDescription' 
                     
                 # other sections---------------------------------------------------------
                 if re.search(r'^Appendix', title, re.IGNORECASE):
                     section['type'] = 'Appendix'  # I made this up       
                 
                 if re.search(r'^Introduction', title, re.IGNORECASE):
                     section['type'] = 'introduction'                  
                 
                 if re.search(r'^Materials?\s+and\s+Methods', title, re.IGNORECASE):
                     section['type'] = 'Methods' 

                 if re.search(r'^Method', title, re.IGNORECASE):
                     section['type'] = 'Methods' 

                 if re.search(r'^Results', title, re.IGNORECASE):
                     section['type'] = 'Results' 

                 if re.search(r'^Supplement', title, re.IGNORECASE):
                     section['type'] = 'SupplementaryInformationDescription'

                 if re.search(r'^SUPPL', title, re.IGNORECASE):
                     section['type'] = 'SupplementaryInformationDescription'
                     
              else:
                 section['type'] = 'Unknown'
                                  
        
        #---------------------------------------------------------------------------------
        # extract identifiers     
        for i, section in enumerate(doc['sections']):
            for j, paragraph in enumerate(section['paragraphs']):
                if paragraph['text']:
                    paragraph['annotations'] = []
                  
                    # do stuff
                    text = paragraph['text']
                    
                    # print(text)
                    
                    # dois                    
                    pattern = r'((DOI[:|,]\s*|doi:\s*|https?://(dx\.)?doi.org/)?' \
                        r'(10\.[0-9]{4,}(?:\.[0-9]+)*(?:/|%2F)(?:(?!["&\'])\S)+))'
                    
                    for match in re.finditer(pattern, text):
                        paragraph['annotations'].append(make_annotation(match, text, 'doi'))
                        
                    #print(paragraph)
                        
                    # other things
                    find_datasets(paragraph, text)
                    
#                   if section['type']:
#                       match section['type']:
#                          case 'Methods':
#                              find_datasets(paragraph, text)                       
#                          case 'Results':
#                              find_datasets(paragraph, text)                       
                    
            #-----------------------------------------------------------------------------
            # extract identifiers in tables
            
            if section.get('tables'):
               for i, table in enumerate(section['tables']):
                   table['annotations'] = []
                   for j, row in enumerate(table['rows']):
                       #print(row)
                       for cell in row:
                           text = cell
                           text = clean_table_cell_value(text)
                           if text: 
                               find_datasets(table, text) 
        
          
        #---------------------------------------------------------------------------------
        # citations in references    
        # Extract only DOIs.
        for i, reference in enumerate(doc['references']):
            if reference['citation']:
                text = reference['citation']
                
                reference['annotations'] = []
               
                pattern = r'((DOI[:|,]\s*|doi:\s*|https?://(dx\.)?doi.org/)?' \
                    r'(10\.[0-9]{4,}(?:\.[0-9]+)*(?:/|%2F)(?:(?!["&\'])\S)+))'
               
                for match in re.finditer(pattern, text):
                    reference['annotations'].append(make_annotation(match, text, 'doi'))                    

        #---------------------------------------------------------------------------------
        # OK, at this point we have articles in simplified form, have attempted to
        # classify sections (e.g., methods, results, etc.), and have extracted 
        # dataset identifiers.
        #
        # Now we go through the identifiers, perhaps clean them (e.g., DOIs) and
        # classify the mode of citation


        #---------------------------------------------------------------------------------
        # Genbank experiment
#        for i, section in enumerate(doc['sections']):
#            for j, paragraph in enumerate(section['paragraphs']):
#                if paragraph.get('annotations'):
#                    for k, annotation in enumerate(paragraph['annotations']):
#                        if annotation['type'] == 'genbank':
#                           print (annotation['exact'])
#

        #---------------------------------------------------------------------------------
        # get data citations in text
        for i, section in enumerate(doc['sections']):
            for j, paragraph in enumerate(section['paragraphs']):
                if paragraph.get('annotations'):
                    for k, annotation in enumerate(paragraph['annotations']):
                    
                        dataset_id = annotation['exact']
                        
                        # clean any namespace prefix
                        dataset_id = remove_namespace(dataset_id)
                                               
                        if annotation['type'] == 'doi':
                        
                            # only add DOI if it is in the DatasetDescription section 
                            # or acknowledgements(?)
                            if annotation['type'] == 'doi':
                                doi = dataset_id
                                doi = clean_doi(doi)
                                doi = format_doi(doi)
                                if section['type'] in ['DatasetDescription', 'Acknowledgements']:
                                    doc['data_citations'][doi] = 'Primary'
 
                        # Special handling for datasets that are likely to be
                        # primary (published by this article) 
                                   
                        elif annotation['type'] in ['biosample', 'genbank', 'gisaidisl', 'prjna', 'pxd', 'sra']:
                            if section['type'] in ['DatasetDescription', 'Acknowledgements']:
                                doc['data_citations'][dataset_id] = 'Primary'
                            else:
                                doc['data_citations'][dataset_id] = 'Secondary'                                
                        else:
                            doc['data_citations'][dataset_id] = 'Secondary'

#                        # alternative rule where some datasets are always primary
#                        # does worse in training
#                        elif annotation['type'] in ['biosample', 'genbank', 'prjna', 'pxd', 'sra']:
#                            doc['data_citations'][dataset_id] = 'Primary'
#                        else:
#                            if section['type'] in ['DatasetDescription', 'Acknowledgements']:
#                                doc['data_citations'][dataset_id] = 'Primary'
#                            else:
#                                doc['data_citations'][dataset_id] = 'Secondary'                                
 
        #---------------------------------------------------------------------------------
        # get data citations in tables
        for i, section in enumerate(doc['sections']):
            if section.get('tables'):
               for j, table in enumerate(section['tables']):
                   if table.get('annotations'):
                       for k, annotation in enumerate(table['annotations']):                   
                           dataset_id = annotation['exact']
                           
                           # clean any namespace prefix
                           dataset_id = remove_namespace(dataset_id)
                           
                           doc['data_citations'][dataset_id] = 'Secondary'

        #---------------------------------------------------------------------------------
        # get data citations in references
        # We rely on our list of data repository DOIs, or text such as "dataset" 
        # or "data release" to distinguish between data citations and paper citations      

        for i, reference in enumerate(doc['references']):
            if reference.get('annotations'):
                for k, annotation in enumerate(reference['annotations']):
                    
                    if annotation['type'] == 'doi':
                        doi = annotation['exact']
                        doi = clean_doi(doi)
                        
                        is_data_citation = False
                        
                        # Does DOI look like it comes from a data repository?
                        if is_data_doi(doi):
                            is_data_citation = True   
                        
                        # Does citation mention "dataset"?
                        if is_data_doi(doi) and re.search(r'data\s*set\b', annotation['prefix'], re.IGNORECASE):
                            is_data_citation = True
 
                        # Does citation mention "data release"?
                        if is_data_doi(doi) and re.search(r'data release\b', annotation['prefix'], re.IGNORECASE):
                            is_data_citation = True
                                                       
                        # Is it really?
                        if re.search(r'zenodo', doi):
                            if re.search(r'(code|library|pandas|python|\bR\b|release|software|version)', annotation['prefix'], re.IGNORECASE):
                                is_data_citation = False   
 
                            # assume that versions refer to software not data
                            if re.search(r'ion\s+\d+\.\d+', annotation['prefix'], re.IGNORECASE):
                                is_data_citation = False
 
                            if re.search(r'data(set)?', annotation['prefix'], re.IGNORECASE):
                                is_data_citation = True   
                                                                         
                        if is_data_citation:
                            doi = clean_doi(doi)
                            doi = format_doi(doi)
                            # we may already have this DOI if it is declared
                            # in the body of the paper, so don't overwrite it
                            if not doi in doc['data_citations']:
                                if is_primary_doi(doi):
                                    doc['data_citations'][doi] = 'Primary'
                                else:
                                    doc['data_citations'][doi] = 'Secondary'
              

        
        #---------------------------------------------------------------------------------
        # save annotated doc
        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(doc, json_file, indent=2, ensure_ascii=False)
            
            
        #---------------------------------------------------------------------------------
        # Add citations to list of results
        if doc.get('data_citations'):
            for citation, type in doc['data_citations'].items():
               rows.append([doc['id'], citation, type])
            
# exploring details about annotations for debugging
#for filename in os.listdir(json_folder):
#    if filename.endswith('.json'):
#    
#        print (filename)
#        
#        id = filename.replace('.json', '')
#        
#        json_path = os.path.join(json_folder, filename)
#        
#        with open(json_path, 'rb') as f:
#            doc = json.load(f)
#            
#        genbank = []
#
#        for i, section in enumerate(doc['sections']):
#            for j, paragraph in enumerate(section['paragraphs']):
#                if paragraph.get('annotations'):
#                    for k, annotation in enumerate(paragraph['annotations']):
#                        #if annotation['type'] == 'doi':
#                        #    print (annotation['prefix'], " | ", annotation['exact'], " | ", annotation['suffix'])
#                        if annotation['type'] == 'genbank':
#                            genbank.append(annotation['exact'])
#        print (genbank)

#print (rows)

# Output

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

