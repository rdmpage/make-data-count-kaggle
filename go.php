<?php

// read XML, get blocks of text

require_once('shared.php');

//----------------------------------------------------------------------------------------
// complete hack, parse DOI looking for patterns of known repos
function is_data_doi($doi)
{
	$is_data = false;
	
	if (preg_match('/10.6073\/pasta/i', $doi))
	{
		$is_data = true;
	}
	
	// Dryad
	if (preg_match('/10.5061\/dryad/i', $doi))
	{
		$is_data = true;
	}
	
	// F1000research data note, e.g. https://f1000research.com/articles/6-877/v1#DS2
	if (preg_match('/10.5256\/f1000research.\d+.d\d+/i', $doi))
	{
		$is_data = true;
	}

	// GBIF
	if (preg_match('/10.15468\/dl/i', $doi))
	{
		$is_data = true;
	}
	
	// PANGEA
	if (preg_match('/10.1594\/PANGAEA/i', $doi))
	{
		$is_data = true;
	}

	// USGS e.g. doi:10.5066/P9S5PVON
	if (preg_match('/10.5066\/[a-z]/i', $doi))
	{
		$is_data = true;
	}
	
	// Zenodo	
	if (preg_match('/10.5281\/zenodo/i', $doi))
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
	$identifiers = extract_identifier_patterns($text);
	
	// print_r($identifiers);
			
	foreach ($identifiers as $namespace => $ids)
	{
		foreach ($ids as $id)
		{
			$datasets = add_dataset($datasets, $article_id, $id, 'Secondary');
		}
	}

	
	return $datasets;
}	


//----------------------------------------------------------------------------------------

// testing 
if (0)
{
	
	$basedir = 'test/xml';
	
	$files = scandir($basedir);
	
	//$files = array('10.1002_ece3.5395.xml');
	
	$files = array('10.1002_nafm.10870.xml'); // no XML file
	$files = array('10.1002_esp.5090.xml'); // fails to parse
	$files = array('10.1002_ece3.5395.xml');
	//$files = array('10.1002_chem.201903120.xml');
	
	$files = array('10.1002_esp.5058.xml');
	
	//$files = scandir($basedir);
}
else
{
	// training 
	$basedir = 'train/xml';
	
	$files = array('10.7717_peerj.10452.xml'); // doesn't include Figshare for some reason?
	//$files = array('10.7717_peerj.12422.xml'); // GBIF, I get 10, training has 5
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
	  
	//$files = array('10.1002_esp.5090.xml'); // Wiley
	
	//$files = array('10.1002_ejic.201900904.xml'); // wiley, no data
	//$files = array('10.1002_mp.14424.xml'); // grant no.s look like Genbank
	
	//$files = array('10.1007_s00382-022-06361-7.xml'); // 
	//$files = array('10.1007_s00442-022-05201-z.xml');
	//$files = array('10.1016_j.ast.2022.107401.xml'); // tei, XML has mangled the cranfield URLs
	//$files = array('10.1016_j.dib.2022.108797.xml');
	//$files = array('10.1016_j.fuel.2022.125768.xml'); // file not found
	
	//$files = array('10.1021_acsomega.3c06074.xml'); // didn't get all CHEMBL records
	
	//$files = array('10.1038_s41396-020-00885-8.xml');
	
	//$files = array('10.7717_peerj.13193.xml');
	
	//$files = array('10.3390_v11060565.xml');
	
	//$files = array('10.1080_19475683.2023.2226196.xml');
	
	//$files = array('10.3897_zookeys.500.9360.xml');
	
	$files = array('10.7717_peerj.12422.xml');
	
	$files = array('10.1002_chem.201903120.xml');
	
	$files = array('10.1002_ece3.5058.xml');
	
	$files = array('10.1371_journal.pone.0159387.xml');
	
	$files = array('10.7554_elife.29944.xml');
	
	$files = array('10.3390_microorganisms8121872.xml');
	
	$files = array('10.3390_rs4102923.xml'); // TEI pangea
	$files = array('10.1371_journal.pcbi.1011828.xml'); // E-PROT-104 etc in table, not picked up
	
	$files = array('10.1371_journal.pone.0159387.xml'); // ids in table
	
	$files = array('10.12688_f1000research.11698.1.xml');
	
	$files = array('10.1136_jitc-2021-003114.xml'); // use of RRID which training labels ignore
	
	$files = array('10.1098_rsos.160417.xml'); // train has made up some dryad links
	$files = array('10.1111_mec.16743.xml'); // not found, can download if have access
	
	$files = array('10.3133_cir1497.xml');
	
	$files = array(
	'10.1002_2017jc013030.xml',
'10.1002_ecs2.1280.xml',
'10.1002_ecs2.4619.xml',
'10.1002_esp.5058.xml',
'10.1002_esp.5090.xml',
'10.1002_mp.14424.xml',
'10.1002_nafm.10870.xml',
'10.1007_s00259-022-06053-8.xml',
'10.1007_s00382-022-06361-7.xml',
'10.1007_s12559-020-09751-3.xml',
'10.1016_j.ast.2022.107401.xml',
'10.1016_j.cpc.2024.109087.xml',
'10.1016_j.dib.2023.109949.xml',
'10.1016_j.ecolind.2021.107934.xml',
'10.1016_j.fuel.2022.125768.xml',
'10.1016_j.jlp.2022.104761.xml',
'10.1016_j.jobe.2023.107105.xml',
'10.1016_j.jsames.2022.103824.xml',
'10.1016_j.molcel.2018.11.006.xml',
'10.1016_j.scitotenv.2024.171850.xml',
'10.1016_j.websem.2024.100815.xml',
'10.1017_rdc.2022.19.xml',
'10.1017_s0007123423000601.xml',
'10.1021_acs.jcim.9b01185.xml',
'10.1021_acsomega.3c06074.xml',
'10.1021_jacs.2c06519.xml',
'10.1029_2018gl078007.xml',
'10.1029_2019jg005297.xml',
'10.1029_2019pa003774.xml',
'10.1029_2020jf005675.xml',
'10.1029_2021ea001703.xml',
'10.1029_2021gl096173.xml',
'10.1029_2021pa004379.xml',
'10.1029_2022gl100473.xml',
'10.1029_2023ea002840.xml',
'10.1038_hdy.2013.74.xml',
'10.1038_hdy.2014.75.xml',
'10.1038_hdy.2015.99.xml',
'10.1038_s41437-020-0318-8.xml',
'10.1038_s41467-018-04041-x.xml',
'10.1038_s41467-018-07681-1.xml',
'10.1038_s41558-022-01301-z.xml',
'10.1038_s41597-019-0101-y.xml',
'10.1038_s41597-022-01555-4.xml',
'10.1038_s41597-022-01555-4.xml',
'10.1038_s41597-022-01555-4.xml',
'10.1038_s41597-022-01555-4.xml',
'10.1038_s41597-023-02280-2-EMPIAR.xml',
'10.1038_s41598-020-59839-x.xml',
'10.1038_s41598-021-85671-y.xml',
'10.1038_s41598-024-56373-y.xml',
'10.1038_s41893-020-0559-9.xml',
'10.1038_sdata.2017.167.xml',
'10.1039_d1ee03696c.xml',
'10.1039_d2cc00847e.xml',
'10.1073_pnas.1323607111.xml',
'10.1073_pnas.1705601114.xml',
'10.1073_pnas.1711872115.xml',
'10.1073_pnas.1915395117.xml',
'10.1080_19475683.2023.2226196.xml',
'10.1080_21645515.2023.2189598.xml',
'10.1093_beheco_arw167.xml',
'10.1093_evolut_qpad206.xml',
'10.1093_nar_gkp1049.xml',
'10.1098_rsbl.2015.0113.xml',
'10.1098_rsos.160417.xml',
'10.1098_rspb.2015.2726.xml',
'10.1098_rspb.2015.2764.xml',
'10.1101_096297.xml',
'10.1101_2022.02.10.480011.xml',
'10.1103_physrevresearch.4.023008.xml',
'10.1107_s2059798322005691.xml',
'10.1109_access.2024.3385658.xml',
'10.1111_1365-2435.13087.xml',
'10.1111_1365-2656.12501.xml',
'10.1111_1365-2656.12594.xml',
'10.1111_1365-2664.13128.xml',
'10.1111_1365-2664.13168.xml',
'10.1111_1365-2664.13446.xml',
'10.1111_1365-2745.13449.xml',
'10.1111_2041-210x.12453.xml',
'10.1111_acel.13089.xml',
'10.1111_cas.12935.xml',
'10.1111_evo.13972.xml',
'10.1111_ggr.12517.xml',
'10.1111_mec.16743.xml',
'10.1111_mec.16977.xml',
'10.1111_njb.02077.xml',
'10.1128_JVI.01717-21.xml',
'10.1130_ges01387.1.xml',
'10.1145_3461702.3462538.xml',
'10.1186_s13071-018-2842-4.xml',
'10.1242_jeb.211466.xml',
'10.1364_oe.25.001985.xml',
'10.1371_journal.pcbi.1011828.xml',
'10.1371_journal.pone.0070749.xml',
'10.1371_journal.pone.0139215.xml',
'10.1371_journal.pone.0188323.xml',
'10.1371_journal.pone.0198382.xml',
'10.1371_journal.pone.0253228.xml',
'10.1371_journal.pone.0262974.xml',
'10.1371_journal.pone.0284951.xml',
'10.14358_pers.22-00039r2.xml',
'10.14379_iodp.proc.390393.208.2024.xml',
'10.1534_genetics.120.303190.xml',
'10.1617_s11527-023-02260-3.xml',
'10.17581_bp.2020.09104.xml',
'10.18438_eblip29674.xml',
'10.21105_joss.04237.xml',
'10.21203_rs.3.rs-2814013_v1.xml',
'10.21203_rs.3.rs-3338732_v1.xml',
'10.3133_cir1497.xml',
'10.3133_fs20233046.xml',
'10.3133_ofr20201035.xml',
'10.3133_ofr20231026.xml',
'10.3133_ofr20231027.xml',
'10.3389_fcell.2020.618552.xml',
'10.3389_fcimb.2024.1292467.xml',
'10.3389_feart.2023.1205211.xml',
'10.3389_fevo.2023.1112519.xml',
'10.3389_fmicb.2024.1456637.xml',
'10.3390_d13010019.xml',
'10.3390_rs12121957.xml',
'10.3390_rs4102923.xml',
'10.3390_s19030479.xml',
'10.3390_s23177333.xml',
'10.3897_jhr.96.111550.xml',
'10.3897_zookeys.500.9360.xml',
'10.5194_acp-2021-570.xml',
'10.5194_acp-22-2769-2022.xml',
'10.5194_acp-22-5701-2022.xml',
'10.5194_amt-15-3969-2022.xml',
'10.5194_essd-12-1287-2020.xml',
'10.5194_essd-2019-206.xml',
'10.5194_essd-2023-187.xml',
'10.5194_essd-2023-198.xml',
'10.5194_essd-8-663-2016.xml',
'10.5194_gmd-12-4221-2019.xml',
'10.5194_se-13-1541-2022.xml',
'10.5194_tc-17-3617-2023.xml',
'10.5937_bnhmb1811227u.xml',
'10.7554_elife.29944.xml',
'10.7554_elife.63455.xml',
'10.7717_peerj.11352.xml',
);

	$files = array('10.3897_jhr.96.111550.xml'); // added
	$files = array('10.3390_s23177333.xml'); // badly cited, naked DOI in text, reference is direct Zenodo URL
	$files = array('10.3390_d13010019.xml'); // training is TEI not JATS!
	//$files = scandir($basedir);
}

$failed_to_parse = array();

$datasets = array();

foreach ($files as $filename)
{
	if (preg_match('/\.xml$/', $filename))
	{
		if (!file_exists($basedir . '/'. $filename))
		{
			echo "*** $filename does not exist! ***\n";
			//exit();
			continue;
		}
			
		$text = '';
		
		$article_id = basename($filename, '.xml');
				
		$xml = file_get_contents($basedir . '/'. $filename);
		
		$header = substr($xml, 0, 1024);
		
		$format = 'unknown';
		
		// BioC annotations
		if (preg_match('/"BioC.dtd"/', $header))
		{
			$format = 'bioc';
		}
		
		// NLM JATS
		if (preg_match('/NLM\/\/DTD/', $header))
		{
			$format = 'jats';
		}
		
		// TaxonX
		if (preg_match('/TaxonX\/\/DTD/', $header))
		{
			$format = 'taxonx';
			$format = 'jats';
		}
		
		// TEI
		if (preg_match('/www.tei-c.org\/ns/', $header))
		{
			$format = 'tei';
		}
		
		// Wiley
		if (preg_match('/www.wiley.com\/namespaces/', $header))
		{
			$format = 'wiley';
			
			// clean up
			$xml = preg_replace('/<component[^>]+>/', '<component>', $xml);			
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
		$article_doi = '';
		
		// JATS
		if ($format == 'jats')
		{
			foreach($xpath->query('//front/article-meta/article-id[@pub-id-type="doi"]') as $node)
			{
				$article_doi = $node->firstChild->nodeValue;
			}				
		
			$body_nodes = $xpath->query ('//body');
			foreach($body_nodes as $body)
			{			
				$ok = true;
				
				$nodeCollection = $xpath->query ('//p', $body);		
				foreach($nodeCollection as $node)
				{
					//echo $node->textContent . "\n";
					
					$paragraph_text = $node->textContent;
					
					//echo "\n$paragraph_text\n";
					
					$text .= $paragraph_text;
					
					preg_match_all('/((DOI:\s*|doi:\s*|https?:\/\/(dx\.)?doi.org\/)10\.[0-9]{4,}(?:\.[0-9]+)*(?:\/|%2F)(?:(?![\"&\'])\S)+)/', $paragraph_text, $m);
					
					foreach ($m[1] as $doi)
					{
						$doi = clean_doi($doi);				
						$datasets = add_dataset($datasets, $article_id, $doi, 'Primary');
					}
					
					$datasets = identifier_patterns($datasets, $article_id, $paragraph_text);
					
					// F1000
					// <ext-link ext-link-type="uri" xlink:href="http://dx.doi.org/10.5256/f1000research.11698.d163784">10.5256/f1000research.11698.d163784</ext-link>
					$links = $xpath->query ('ext-link[@ext-link-type="uri"]/@xlink:href', $node);		
					foreach($links as $link)
					{
						if (preg_match('/((https?:\/\/(dx\.)?doi.org\/)10\.[0-9]{4,}(?:\.[0-9]+)*(?:\/|%2F)(?:(?![\"&\'])\S)+)/', $link->firstChild->nodeValue, $m))
						{
							$doi = clean_doi($m[1]);				
							$datasets = add_dataset($datasets, $article_id, $doi, 'Primary');
						}
					}

					
				}
				
				// table				
				$nodeCollection = $xpath->query ('//table/tbody/tr/td', $body);		
				foreach($nodeCollection as $node)
				{
					//echo $node->textContent . "\n";
					
					$table_cell = $node->textContent;
					
					//echo "\n$paragraph_text\n";
					
					$text .= $table_cell;
					
					$datasets = identifier_patterns($datasets, $article_id, $table_cell);					
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
					// structured citation
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
					
					// Pensoft GBIF citation
					$nc = $xpath->query ('ext-link[@ext-link-type="doi"]/@xlink:href', $citation_node);		
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
			
			foreach($xpath->query('//publicationMeta[@level="unit"]/doi') as $node)
			{
				$article_doi = $node->firstChild->nodeValue;
			}				
			
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
					foreach ($xpath->query('(section|.)/p', $section) as $p)
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
		
		echo "article_doi=$article_doi\n";
		
		// remove any self citations (why do we get these?)
		if (isset($datasets[$article_id]['https://doi.org/' . $article_doi]))
		{
			unset($datasets[$article_id]['https://doi.org/' . $article_doi]);
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

$output = '';

$output .= "row_id,article_id,dataset_id,type\n";

$counter = 0;

foreach ($datasets as $article_id => $dois)
{
	foreach ($dois as $doi => $type)
	{
		$row = array($counter++, $article_id, $doi, $type);
		$output .= join(",", $row) . "\n";
	}
}

echo $output . "\n";

file_put_contents('output.csv', $output);



?>
