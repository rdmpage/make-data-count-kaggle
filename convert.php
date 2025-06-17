<?php

// Based on code for BIOC but trying to keep things simple

//----------------------------------------------------------------------------------------
// Extract details from references
function ref($node, &$passage)
{
	global $xpath;
	
	/*
	
	foreach($xpath->query('(element-citation|mixed-citation|nlm-citation)', $node) as $n)
	{
		$passage->infons->unstructured = $n->textContent;
	}	
	
	foreach($xpath->query('(element-citation|mixed-citation|nlm-citation)/person-group/name', $node) as $n)
	{
		$parts = array();
	
		$ncc = $xpath->query ('given-names', $n);
		foreach($ncc as $nc)
		{
			$given = $nc->firstChild->nodeValue;
			$given = preg_replace('/([A-Z])([A-Z])/u', '$1 $2', $given);
			$given = preg_replace('/([A-Z])([A-Z])/u', '$1 $2', $given);
			$given = preg_replace('/([A-Z])([A-Z])/u', '$1 $2', $given);
			$given = trim($given);
			
			$parts[] = $given;
		}
		$ncc = $xpath->query ('surname', $n);
		foreach($ncc as $nc)
		{
			$family = $nc->firstChild->nodeValue;
			
			$parts[] = $family;
		}
		
		$passage->infons->author[] = join(' ', $parts);
	}
	
	// PLoS is flatter
	foreach($xpath->query('mixed-citation/name', $node) as $n)
	{
		$parts = array();
	
		$ncc = $xpath->query ('given-names', $n);
		foreach($ncc as $nc)
		{
			$given = $nc->firstChild->nodeValue;
			$given = preg_replace('/([A-Z])([A-Z])/u', '$1 $2', $given);
			$given = preg_replace('/([A-Z])([A-Z])/u', '$1 $2', $given);
			$given = preg_replace('/([A-Z])([A-Z])/u', '$1 $2', $given);
			$given = trim($given);
			
			$parts[] = $given;
		}
		$ncc = $xpath->query ('surname', $n);
		foreach($ncc as $nc)
		{
			$family = $nc->firstChild->nodeValue;
			
			$parts[] = $family;
		}
		
		$passage->infons->author[] = join(' ', $parts);
	}
	
	
	foreach($xpath->query('(element-citation|mixed-citation|nlm-citation)/article-title', $node) as $n)
	{
		$passage->infons->title = $n->textContent;
	}	

	foreach($xpath->query('(element-citation|mixed-citation|nlm-citation)/source', $node) as $n)
	{
		$passage->infons->source = $n->firstChild->nodeValue;
	}	
		
	foreach($xpath->query('(element-citation|mixed-citation|nlm-citation)/volume', $node) as $n)
	{
		$passage->infons->volume = $n->firstChild->nodeValue;
	}	

	foreach($xpath->query('(element-citation|mixed-citation|nlm-citation)/issue', $node) as $n)
	{
		$passage->infons->issue = $n->firstChild->nodeValue;
	}	

	foreach($xpath->query('(element-citation|mixed-citation|nlm-citation)/fpage', $node) as $n)
	{
		$passage->infons->fpage = $n->firstChild->nodeValue;
	}	
	
	foreach($xpath->query('(element-citation|mixed-citation|nlm-citation)/lpage', $node) as $n)
	{
		$passage->infons->lpage = $n->firstChild->nodeValue;
	}	

	foreach($xpath->query('(element-citation|mixed-citation|nlm-citation)/year', $node) as $n)
	{
		$passage->infons->year = $n->firstChild->nodeValue;
	}		

	foreach($xpath->query('(element-citation|mixed-citation|nlm-citation)/ext-link[@ext-link-type="doi"]/@xlink:href', $node) as $n)
	{
		$passage->infons->doi = $n->firstChild->nodeValue;
	}	

	foreach($xpath->query('(element-citation|mixed-citation|nlm-citation)/pub-id[@pub-id-type="doi"]/@xlink:href', $node) as $n)
	{
		$passage->infons->doi = $n->firstChild->nodeValue;
	}	
	
	foreach($xpath->query('(element-citation|mixed-citation|nlm-citation)/ext-link[@ext-link-type="uri"]/@xlink:href', $node) as $n)
	{
		$passage->infons->url = $n->firstChild->nodeValue;
	}	
	*/
	
}

//----------------------------------------------------------------------------------------
// Recursively traverse DOM and process tags, add passages and annotations as we go
function dive($dom, $node, $passage = null)
{	
	global $count;
	global $depth;
	
	global $doc;
	
	//echo $doc->title_depth . "\n";
	
	$tag_name = $node->nodeName;
	
	// Tags for references can include <title> which gets conflated with section titles.
	if ($node->parentNode->nodeName == 'mixed-citation')
	{
		$tag_name = '';
	}
	
	// echo "tag_name = $tag_name\n";
		
	switch ($tag_name)
	{		
		case 'sec':
			$doc->title_depth++;
			break;
					
		//case 'label': // labels can't be passages as they break Pensoft
		//case 'abstract':
		case 'article-title':
		case 'title':
		case 'p':
		case 'tp:taxon-treatment':
		case 'ref':
			if (!$passage)
			{		
				$passage = new stdclass;			
				$passage->text = '';
				//$passage->offset = $count;
				//$passage->infons = new stdclass;
				//$passage->annotations = array();
			}
			
			switch ($node->nodeName)
			{		
			
				/*
				case 'abstract':
				  	$passage->section_type = "abstract";
					break;	
				*/			
				
				// case 'article-title':
				case 'title':
				  	$passage->section_type = "title" . "_" . $doc->title_depth;
					break;				
					
				case 'ref':		
					$passage->section_type = "ref";
					//$passage->infons->type = "ref";
					ref($node, $passage);
					break;
					
				case 'p':
				//case 'tp:taxon-treatment':
				//case 'label':
				default:
					$passage->section_type = "text";
					break;
			}
					
			$doc->passages[] = $passage;			
			$doc->stack[] = $passage;			
			$doc->current = $passage;
			
			/*
			$depth++;	
			echo str_pad('', (2 * $depth), ' ');			
			echo "push " . $node->nodeName . ' [' . count($doc->stack) . "]\n";
			*/
			
			break;
			
		/*
		// annotations
		
		// taxonomic names
		case 'tp:taxon-name':	
			// echo '[' . $count . '] ' . $node->nodeValue . "\n";
			
			// These need special treatment as Pensoft can include additional tags
			// such as object-id which make processing tricky
			
				//<tp:taxon-name><object-id content-type="arpha">3F003351-4A01-5C0A-BDF5-35CC77D4FC5A</object-id>
				 // <tp:taxon-name-part taxon-name-part-type="genus" reg="Lappula">Lappula</tp:taxon-name-part>
				//  <tp:taxon-name-part taxon-name-part-type="species" reg="effusa">effusa</tp:taxon-name-part>
				//  <object-id content-type="ipni" xlink:type="simple">urn:lsid:ipni.org:names77343947-1</object-id>
				//</tp:taxon-name>
			
			if (1)
			{				
				$taxon_name_parts = array();
				$start = 0;
				
				$children = $node->childNodes;
				foreach ($children as $child)
				{
					switch ($child->nodeName)
					{
						// skip over these
						case 'object-id':
							$count += mb_strlen($child->nodeValue, mb_detect_encoding($child->nodeValue));
							$count += 1; // add one for space
							break;
							
						case 'tp:taxon-name-part':
							//echo ">|" . $child->nodeValue . "|\n";
							
							if (trim($child->nodeValue) != '')
							{
								if ($start == 0)
								{
									$start = $count;								
								}
								$taxon_name_parts[] = $child->nodeValue;
							}
							break;
							
						default:
							break;
					}
				}
				
				//echo "start=$start\n";
				//print_r($a);
				
				if (count($taxon_name_parts) > 0)
				{
					
					$taxon_name = join(' ', $taxon_name_parts);
					
					$annotation = new stdclass;
					$annotation->text = $taxon_name;
					$annotation->infons = new stdclass;
					$annotation->infons->type = 'Species';
					$annotation->locations = array();
					
					$location = new stdclass;
					$location->offset = $start;
					$location->length = mb_strlen($taxon_name, mb_detect_encoding($taxon_name));
					$annotation->locations[] = $location;
									
					if ($doc->current)
					{
						$doc->current->annotations[] = $annotation;
					}
				}	
			}
			else
			{	
				// this works for most tp:taxon-name but not those with UUIDs and other 
				// identifiers				
				$annotation = new stdclass;
				$annotation->text = $node->nodeValue;
				$annotation->infons = new stdclass;
				$annotation->infons->type = 'Species';
				$annotation->locations = array();
				
				$location = new stdclass;
				$location->offset = $count;
				$location->length = mb_strlen($node->nodeValue, mb_detect_encoding($node->nodeValue));
				$annotation->locations[] = $location;
								
				if ($doc->current)
				{
					$doc->current->annotations[] = $annotation;
				}	
			}					
			break;
			
		// named-content
		case 'named-content':		
			// echo '[' . $count . '] ' . $node->nodeValue . "\n";
						
			$attributes = array();
			if ($node->hasAttributes()) 
			{ 
				$attrs = $node->attributes; 
	
				foreach ($attrs as $i => $attr)
				{
					$attributes[$attr->name] = $attr->value; 
				}
			}
			
			$type = 'Unknown';
			
			// print_r($attributes);
			//exit();
			
			$go = true;

			if (isset($attributes['content-type']))
			{
				switch ($attributes['content-type'])
				{
					// if we have both dwc:verbatimCoordinates and geo-json
					// we get two annotations with an identical span, and that breaks
					// our ability to render them in HTML
					case 'dwc:verbatimCoordinates':
						$type = 'Geo';
						$go = true;
						break;					
				
					case 'geo-json':
						$type = 'Geo';
						$go = false;
						break;
						
					case 'dwc:institutional_code':
					case 'institution':
						$type = 'Organisation';
						break;
						
					case 'kingdom':
					case 'order':
					case 'family':
						$type = 'Species';
						break;
						
					default:
						break;
				}
		    }	
		    		
		    if ($go)
		    {
				$annotation = new stdclass;
				$annotation->text = $node->nodeValue;
				$annotation->infons = new stdclass;
				$annotation->infons->type = $type;
				$annotation->locations = array();
		
				$location = new stdclass;
				$location->offset = $count;
				$location->length = mb_strlen($node->nodeValue, mb_detect_encoding($node->nodeValue));
				$annotation->locations[] = $location;
					
				if ($doc->current)
				{
					$doc->current->annotations[] = $annotation;
				}
			}			
						
			break;
			
		// external links
		case 'ext-link':		
			//echo '[' . $count . '] |' . $node->nodeValue . "|\n";			
			
			$attributes = array();
			if ($node->hasAttributes()) 
			{ 
				$attrs = $node->attributes; 
	
				foreach ($attrs as $i => $attr)
				{
					$attributes[$attr->name] = $attr->value; 
				}
			}
			
			$type = 'Unknown';
			
			//print_r($attributes);
			//exit();

			if (isset($attributes['ext-link-type']))
			{
				switch ($attributes['ext-link-type'])
				{
					case 'gen':
						$type = 'Gene';
						break;

					default:
						break;
				}
		    }	
		    		
			$annotation = new stdclass;
			$annotation->text = $node->nodeValue;
			$annotation->infons = new stdclass;
			$annotation->infons->type = $type;
			$annotation->locations = array();
		
			$location = new stdclass;
			$location->offset = $count;
			$location->length = mb_strlen($node->nodeValue, mb_detect_encoding($node->nodeValue));
			$annotation->locations[] = $location;
					
			if ($doc->current)
			{
				$doc->current->annotations[] = $annotation;
			}
			break;	
		*/
						
		case '#text':
			//echo '#text=|' . $node->nodeValue . "|\n";
			if ($doc->current)
			{
				$doc->current->text .= $node->nodeValue . ' ';
				//$count += mb_strlen($node->nodeValue, mb_detect_encoding($node->nodeValue));
				//$count += 1;
			}
			break;
						
		default:
			break;
	}
	
	// Visit any children of this node
	if ($node->hasChildNodes())
	{
		foreach ($node->childNodes as $children) {
			dive($dom, $children);
		}
	}
	
	// leaving
	
	$depth--;
	//echo str_pad('', (2 * $depth), ' ');
	
	switch ($tag_name)
	{
		case 'sec':
			$doc->title_depth--;
			break;
	
		//case 'label': // labels can't be passages as they break Pensoft
		//case 'abstract':
		case 'article-title':
		case 'title':
		case 'p':
		case 'tp:taxon-treatment':
		case 'ref':
		
			// clean text(?)
			if (1)
			{
				$doc->current->text = preg_replace('/\s+$/', '', $doc->current->text);	
				$doc->current->text = preg_replace('/\(\s+/', '(', $doc->current->text);
				$doc->current->text = preg_replace('/\s+([\)|,|;])/', '$1', $doc->current->text);
			}
		
			array_pop($doc->stack);
						
			/*
			$depth--;	
			echo str_pad('', (2 * $depth), ' ');			
			echo "pop " . $node->nodeName . ' [' . count($doc->stack) . "]\n";
			*/
			
			$stack_count = count($doc->stack);
			if ($stack_count > 0)
			{
				$doc->current = $doc->stack[$stack_count - 1];
			}
			else
			{
				$doc->current = null;
			}
			
			break;
						
		default:
			break;
	
	
	}
	
	
}


//----------------------------------------------------------------------------------------

$filename = 'train/xml/10.7717_peerj.12422.xml';
//$filename = 'train/xml/10.1007_s00442-022-05201-z.xml';

$filename = 'train/xml/10.3897_bdj.7.e47369.xml';
//$filename = 'train/xml/10.3897_zookeys.500.9360.xml';

/*
if ($argc < 2)
{
	echo "Usage: jats2bioc.php <filename>\n";
	exit(1);
}
else
{
	$filename = $argv[1];
}
*/

$basename = preg_replace('/\.xml$/', '', $filename);

$output_filename = $basename . '.json';

$xml = file_get_contents($filename);

// load XML and XPATH
$dom= new DOMDocument;
$dom->preserveWhiteSpace = true; // need this for tp:name to work
$dom->preserveWhiteSpace = false;
$dom->loadXML($xml, LIBXML_NOCDATA); // So we get text wrapped in <![CDATA[ ... ]]>
$xpath = new DOMXPath($dom);

// store output 
$depth = 0;

$doc = new stdclass;
$doc->stack = array();
$doc->current = null;
$doc->title_depth = 0;
$doc->passages = array();

// identifiers

// pmcid
foreach($xpath->query('//front/article-meta/article-id[@pub-id-type="pmc"]') as $node)
{
    $doc->pmcid = $node->firstChild->nodeValue;
}

// pmid
foreach($xpath->query('//front/article-meta/article-id[@pub-id-type="pmid"]') as $node)
{
    $doc->pmid = (Integer)$node->firstChild->nodeValue;
}

// doi
foreach($xpath->query('//front/article-meta/article-id[@pub-id-type="doi"]') as $node)
{
    $doc->doi = $node->firstChild->nodeValue;
}


// title
foreach($xpath->query('//front/article-meta/title-group/article-title') as $node)
{
	$passage = new stdclass;
	$passage->section_title = $node->textContent;
	$passage->section_type =  'title';
    $passage->text = $node->textContent; 
    
    $doc->passages[] = $passage;
}


// Handle the various parts of an article

/*
foreach ($xpath->query('//front/article-meta/title-group/article-title') as $node) {
    dive($dom, $node, $front_passage);
}
*/



$depth = 0;

foreach ($xpath->query('//front/article-meta') as $node) {
    dive($dom, $node);
}


foreach ($xpath->query('//body') as $node) {
    dive($dom, $node);
}


foreach ($xpath->query('//back') as $node) {
    dive($dom, $node);
}

// clean up
unset($doc->stack);
unset($doc->current);
unset($doc->title_depth);

/*

$bioc->passages = $doc->passages;

//print_r($bioc);

file_put_contents($output_filename, json_encode($bioc, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE));

*/


echo json_encode($doc, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
echo "\n";


?>
