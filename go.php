<?php

// read XML, get blocks of text


//----------------------------------------------------------------------------------------
function clean_doi($doi)
{
	$doi = preg_replace('/[;|,|\.|\)]$/', '', $doi);
	$doi = preg_replace('/[;|,|\.|\)]$/', '', $doi);
	$doi = preg_replace('/^doi:/i', 'https://doi.org/', $doi);

	$doi = preg_replace('/^10\./i', 'https://doi.org/10.', $doi);
	
	$doi = preg_replace('/http:\/\/dx\./', 'https://', $doi);

	$doi = preg_replace('/\s+/i', '', $doi);

	return $doi;
}

//----------------------------------------------------------------------------------------
// complete hack, parse DOI looking for patterns of known repos
function is_data_doi($doi)
{
	$is_data = false;
	
	if (preg_match('/10.6073\/pasta/', $doi))
	{
		$is_data = true;
	}

	// GBIF
	if (preg_match('/10.15468\/dl/', $doi))
	{
		$is_data = true;
	}
	
	return $is_data;
}

//----------------------------------------------------------------------------------------
function add_dataset($datasets, $article_id, $data_id, $type = 'Primary')
{
	if (!isset($datasets[$article_id]))
	{
		$datasets[$article_id] = array();
	}
	if (!isset($datasets[$article_id][$data_id]))
	{
		$datasets[$article_id][$data_id] = array();
	}
	$datasets[$article_id][$data_id] = $type;
	
	return $datasets;
}

//----------------------------------------------------------------------------------------
function identifier_patterns($datasets, $article_id, $text)
{
	// Genbank	
	// https://registry.identifiers.org/registry/insdc
	preg_match_all('/\b(?<acc>[A-Z]\d{5}|[A-Z]{2}\d{6}|[A-Z]{4,6}\d{8,10}|[A-J][A-Z]{2}\d{5})(\.\d+)?\b/', $text, $m);
	
	foreach ($m['acc'] as $acc)
	{
		$datasets = add_dataset($datasets, $article_id, $acc, 'Secondary');
	}
	
	// CHEMBL	
	preg_match_all('/(CHEMBL\d+)/', $text, $m);	
	foreach ($m[1] as $id)
	{
		$datasets = add_dataset($datasets, $article_id, $id, 'Secondary');
	}
	
	// GISAID	
	preg_match_all('/(EPI\d+)/', $text, $m);	
	foreach ($m[1] as $id)
	{
		$datasets = add_dataset($datasets, $article_id, $id, 'Secondary');
	}
	

	// InterPro	
	preg_match_all('/(IPR\d{6})/', $text, $m);	
	foreach ($m[1] as $id)
	{
		$datasets = add_dataset($datasets, $article_id, $id, 'Secondary');
	}
	
	// PFam PF\d{5}
	preg_match_all('/(PF\d{5})/', $text, $m);	
	foreach ($m[1] as $id)
	{
		$datasets = add_dataset($datasets, $article_id, $id, 'Secondary');
	}
	
	return $datasets;
}	


//----------------------------------------------------------------------------------------

// testing 
if (1)
{
	
	$basedir = 'test/xml';
	
	$files = scandir($basedir);
	
	//$files = array('10.1002_ece3.5395.xml');
	
	$files = array('10.1002_nafm.10870.xml'); // no XML file
	$files = array('10.1002_esp.5090.xml'); // fails to parse
	$files = array('10.1002_ece3.5395.xml');
	//$files = array('10.1002_chem.201903120.xml');
}

// training 
if (1)
{
	$basedir = 'train/xml';
	
	$files = array('10.7717_peerj.10452.xml'); // doesn't include Figshare for some reason?
	$files = array('10.7717_peerj.12422.xml'); // GBIF, I get 10, training has 5
	//$files = array('10.7717_peerj.13193.xml'); // pasta, training says 1 pri, 2 sec, I say all sec
	
	//$files = array('10.7554_elife.74937.xml'); // includes funder DOIs, v. bad
	//$files = array('10.7554_elife.73695.xml'); // wierdness with lots of extra DOIs, XML doesn't seem to respect body
	
	//$files = array('10.5937_bnhmb1811227u.xml'); // TEI Grobid
	
	//$files = array('10.3897_neobiota.82.87455.xml'); // TEI
	
	//$files = array('10.3390_v11060565.xml'); // GenBank (not extracted yet)
	
	//$files = array('10.3390_rs4102923.xml'); // TEI grobid
	
	//$files = array('10.1186_s12870-020-02692-x.xml'); // MCD don't show genbank accessions
	 
	//$files = array('10.1002_ece3.4466.xml');
	//$files = array('10.1002_esp.5090.xml');
	  
	$files = array('10.1002_esp.5090.xml'); // Wiley
	
	//$files = array('10.1002_ejic.201900904.xml'); // wiley, no data
	//$files = array('10.1002_mp.14424.xml'); // grant no.s look like Genbank
	
	$files = array('10.1007_s00382-022-06361-7.xml'); // 
	$files = array('10.1007_s00442-022-05201-z.xml');
	$files = array('10.1016_j.ast.2022.107401.xml'); // tei, XML has mangled the cranfield URLs
	$files = array('10.1016_j.dib.2022.108797.xml');
	//$files = array('10.1016_j.fuel.2022.125768.xml'); // file not found
	
	//$files = array('10.1021_acsomega.3c06074.xml'); // didn't get all CHEMBL records
	
	//$files = array('10.1038_s41396-020-00885-8.xml');
	
	$files = array('10.7717_peerj.13193.xml');
	
	$files = array('10.3390_v11060565.xml');
	
	//$files = scandir($basedir);
}

$failed_to_parse = array();

$datasets = array();

foreach ($files as $filename)
{
	if (preg_match('/\.xml$/', $filename))
	{
		$format = 'jats';
		
		$text = '';
		
		$article_id = basename($filename, '.xml');
		
		$xml = file_get_contents($basedir . '/'. $filename);
		
		$header = substr($xml, 0, 1024);
		
		if (preg_match('/www.wiley.com\/namespaces/', $header))
		{
			$format = 'wiley';
			
			// clean up
			$xml = preg_replace('/<component[^>]+>/', '<component>', $xml);
		}

		if (preg_match('/www.tei-c.org\/ns/', $header))
		{
			$format = 'tei';
		}
		
		echo "format=$format\n";
		
		$dom = new DOMDocument;
		$dom->loadXML($xml, LIBXML_NOCDATA);
		$xpath = new DOMXPath($dom);
		
		
		if ($format == 'tei')
		{
			$xpath->registerNamespace('tei', 'http://www.tei-c.org/ns/1.0');
		}
		
		$ok = false;

		// main text of article
		
		// JATS
		if ($format == 'jats')
		{
			$body_nodes = $xpath->query ('//body');
			foreach($body_nodes as $body)
			{			
				$ok = true;
				
				$nodeCollection = $xpath->query ('//p', $body);		
				foreach($nodeCollection as $node)
				{
					//echo $node->textContent . "\n";
					
					$paragraph_text = $node->textContent;
					
					echo "\n$paragraph_text\n";
					
					$text .= $paragraph_text;
					
					preg_match_all('/((DOI:\s*|doi:\s*|https?:\/\/(dx\.)?doi.org\/)10\.[0-9]{4,}(?:\.[0-9]+)*(?:\/|%2F)(?:(?![\"&\'])\S)+)/', $paragraph_text, $m);
					
					foreach ($m[1] as $doi)
					{
						$doi = clean_doi($doi);				
						$datasets = add_dataset($datasets, $article_id, $doi, 'Primary');
					}
					
					$datasets = identifier_patterns($datasets, $article_id, $paragraph_text);
					
				}
			}
			
			// JATS but no text
			if ($text == "")
			{
				$ok = false;
			}
			
			// references 
			$nodeCollection = $xpath->query ('//back/ref-list/ref');
			foreach($nodeCollection as $node)
			{
				$ok = true;
				
				$citation_nodes = $xpath->query ('(element-citation|mixed-citation|nlm-citation)', $node);
				foreach($citation_nodes as $citation_node)
				{
					$nc = $xpath->query ('pub-id[@pub-id-type="doi"]', $citation_node);
					foreach($nc as $n)
					{
						$doi = strtolower($n->firstChild->nodeValue);
						$doi = clean_doi($doi);
						
						if (is_data_doi($doi))
						{
							$datasets = add_dataset($datasets, $article_id, $doi, 'Secondary');					
						}
					}		
				}
			}
			
		}
		
		if ($format == 'tei')
		{
			
			// TEI references (typicaly from Grobid)
			$body_nodes = $xpath->query ('//tei:listbibl');
			foreach($body_nodes as $body)		
			{						
				$ok = true;
	/* 
	<idno type="DOI">10.15468/dl.ize4xxiNaturalist.org(2018b):Ranagraeca.GBIF.org</idno>
	<ptr target="https://doi.org/10.15468/dl"></ptr>
	*/		
				$nodeCollection = $xpath->query ('//tei:biblstruct//tei:idno[@type="DOI"]');		
				foreach($nodeCollection as $node)
				{
					$doi = $node->textContent;
					$doi = preg_replace('/iNaturalist.org.*$/i', '', $doi);
					$doi = clean_doi($doi);	
								
					if (is_data_doi($doi))
					{
						$datasets = add_dataset($datasets, $article_id, $doi, 'Secondary');					
					}
				}
			}		
		}
		
		if ($format == 'wiley')
		{
			// Wiley
			$xpath->registerNamespace('wiley', 'http://www.wiley.com/namespaces/wiley');
			
			$components = $xpath->query ('//component');
			foreach($components as $component)
			{			
				$ok = true;
				
				$sections = $xpath->query ('//body/section', $component);		
				foreach($sections as $section)
				{
					// title
					$title = '';
					foreach ($xpath->query('title', $section) as $p)
					{					
						$title = $p->textContent;
						
						echo "title=$title\n";
					}
					
					// text
					foreach ($xpath->query('p', $section) as $p)
					{					
						echo $p->textContent . "\n";
						
						$paragraph_text = $p->textContent;
						
						$text .= $paragraph_text;
						
						// DOIs
						preg_match_all('/((DOI:\s*|doi:\s*|https?:\/\/(dx\.)?doi.org\/)10\.[0-9]{4,}(?:\.[0-9]+)*(?:\/|%2F)(?:(?![\"&\'])\S)+)/', $paragraph_text, $m);
						foreach ($m[1] as $doi)
						{
							$doi = clean_doi($doi);				
							$datasets = add_dataset($datasets, $article_id, $doi, 'Primary');
						}
						
						$datasets = identifier_patterns($datasets, $article_id, $paragraph_text);
						
					}
					
				}
	
			}	
		}
		
		
		// broken XML (or parser?)
		if (!$ok)
		{
			$failed_to_parse[] = $article_id;
		}
			
		
	}
}

print_r($datasets);

$num_read = count($files);
$num_failed = count($failed_to_parse);

echo $num_read . " XML files read\n";

if ($num_failed > 0)
{
	echo "*** Failed to parse " . $num_failed . " files ***\n";
	
	echo join("\n", $failed_to_parse) . "\n";
}

echo "\nOutput\n\n";

echo "row_id,article_id,dataset_id,type\n";

$counter = 0;

foreach ($datasets as $article_id => $dois)
{
	foreach ($dois as $doi => $type)
	{
		$row = array($counter++, $article_id, $doi, $type);
		echo join(",", $row) . "\n";
	}
}


?>
