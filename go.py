import os
import re
import json
from lxml import etree

# Define input and output directories
xml_folder = 'training-xml-extra'
#xml_folder = 'train/xml'
#xml_folder = 'test/xml'
json_folder = 'json'

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
           'bioc' : r'BioC.dtd',
           'jats' : r'(NLM|TaxonX)//DTD',
           'tei' : r'www.tei-c.org/ns',
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
           'title' : None,
           'doi' : None,
           'sections' : [],
           'references' : []
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
                 #print(title)
                
            # doi
            doi = None
            path = f'.//front/article-meta/article-id[@pub-id-type="doi"]'
            elements = root.findall(path)
            if elements:
                 doi = elements[0].text.strip()
                 #print(doi)
                 
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
                 #print(title)
                 
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
                       print(sec_title)
                       
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
        
            print("Doing Wiley")
    
            ns = {'wiley': 'http://www.wiley.com/namespaces/wiley'}
            
            # title
            path = f'.//wiley:contentMeta/wiley:titleGroup/wiley:title'
            #print (path)
            elements = root.findall(path, namespaces=ns)
            if elements and elements[0].text:
                title = elements[0].text.strip()
                #print (title)
    
            # doi
            path = f'.//wiley:publicationMeta[@level="unit"]/wiley:doi'
            elements = root.findall(path, namespaces=ns)
            if elements and elements[0].text:
                doi = elements[0].text.strip()
                
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
                       print(sec_title)
                   
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
     
             
            if title:
                json_data['title'] = title
            
            if doi:
                json_data['doi'] = doi
            
        print ("done file")

        # Save to JSON with same name but .json extension
        json_filename = filename.replace('.xml', '.json')
        json_path = os.path.join(json_folder, json_filename)

        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, indent=2, ensure_ascii=False)

print("Finished processing XML files.")

# process them here...
