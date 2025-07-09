<?php

//----------------------------------------------------------------------------------------
// http://stackoverflow.com/a/5996888/9684
function translate_quoted($string) {
  $search  = array("\\t", "\\n", "\\r");
  $replace = array( "\t",  "\n",  "\r");
  return str_replace($search, $replace, $string);
}

//----------------------------------------------------------------------------------------
function read_data($filename)
{
	$data = array();
	
	$headings = array();
	
	$row_count = 0;
	
	$file = @fopen($filename, "r") or die("couldn't open $filename");
			
	$file_handle = fopen($filename, "r");
	while (!feof($file_handle)) 
	{
		$row = fgetcsv(
			$file_handle, 
			0, 
			translate_quoted(','),
			translate_quoted('"') 
			);
			
		$go = is_array($row);
		
		if ($go)
		{
			if ($row_count == 0)
			{
				$headings = $row;		
			}
			else
			{
				$obj = new stdclass;
			
				foreach ($row as $k => $v)
				{
					if ($v != '')
					{
						$obj->{$headings[$k]} = $v;
					}
				}
			
				//print_r($obj);	
				
				if ($obj->dataset_id != "Missing")
				{
					if (!isset($data[$obj->article_id]))
					{
						$data[$obj->article_id] = array();
					}
					$data[$obj->article_id][$obj->dataset_id] = $obj->type;
					
					if (!isset($obj->type))
					{
						print_r($obj);
						exit();
					}
				}
			}
		}	
		$row_count++;
	}	
	
	return $data;
}

//----------------------------------------------------------------------------------------
function get_xml_filename($id)
{
	$filename = dirname(__FILE__) . '/train/XML/' . $id . '.xml';
	return $filename;
}

//----------------------------------------------------------------------------------------
function get_text_filename($id)
{
	$filename = dirname(__FILE__) . '/text/' . $id . '.txt';
	return $filename;
}

//----------------------------------------------------------------------------------------
function xml_type($id)
{
	$filename = get_xml_filename($id);
	
	$xml = file_get_contents($filename);
	
	$format = 'unknown';
	
	$header = substr($xml, 0, 1024);

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
	}
	
	return $format;
}

//----------------------------------------------------------------------------------------

// What are we comapring?
// gold standard
if (0)
{
	// competition supplied
	$gold_filename = 'train_labels.csv';
	$model_filename = 'submission.csv';
}
else
{
	// my own labels
	$gold_filename = '/Users/rpage/Development/make-data-count-training-data/new_training_labels.csv';
	$model_filename = 'submission.csv';
}

if (0)
{
	// test manual annotation of PDFs
	$gold_filename = 'alt-train/output.csv';
	$model_filename = 'train_labels.csv';
}

if (0)
{
	// Comapring official training data to mine
	$gold_filename = '/Users/rpage/Development/make-data-count-training-data/new_training_labels.csv';
	$gold_filename = 'train_labels.csv';
	$model_filename = 'newbaseline.csv';
}

if (0)
{
	// Comparing two different runs
	$gold_filename = 'submission-doack.csv';
	$model_filename = 'submission.csv';
}

echo "Reading GOLD standard\n";
$gold = read_data($gold_filename);

echo "Reading predictions\n";
$model = read_data($model_filename);

ksort($gold);
ksort($model);

if (0)
{
	// detailed analysis of matches

	//print_r($model);
	//print_r($gold);
	
	// compare
	
	$comp = array();
	
	foreach ($gold as $id => $citations)
	{
		if (!isset($comp[$id]))
		{
			$comp[$id] = new stdclass;
		}
		
		$comp[$id]->truth = $citations;
		
		if (isset($model[$id]))
		{
			$comp[$id]->predicted = $model[$id];
			
			$g_ids = array_keys($comp[$id]->truth);
			$m_ids = array_keys($comp[$id]->predicted);
			
			$comp[$id]->correct = array_intersect($g_ids, $m_ids);
			$comp[$id]->madeup  = array_diff($m_ids, $g_ids);
			$comp[$id]->missed = array_diff($g_ids, $m_ids);
	
		}
	
	}
	
	
	
	
	ksort($comp);
	print_r($comp);
}

//print_r($model);

if (1)
{
        $patterns = array(
            'arxe'      => 'E-GEOD-\d+', // https://www.ebi.ac.uk/biostudies/arrayexpress
            'arxm'      => 'E-MTAB-\d+', // https://www.ebi.ac.uk/biostudies/arrayexpress
            'arxp'      => 'E-PROT-\d+', // https://www.ebi.ac.uk/biostudies/arrayexpress
            'biosample' => 'SAM[NED]\w?\d+', // https://registry.identifiers.org/registry/biosample
            
            'cellosaurus' => '(CVCL_[0-9A-Z][0-9A-Z]\d{2})',
            
            'chembl'    => 'CHEMBL\d+',
            
            'dbsnp'     => 'rs\d{4,}', // modified from https://registry.identifiers.org/registry/dbsnp
            
            //'dra'       => 'DRA\d{6}', // https://www.ddbj.nig.ac.jp/dra/index-e.html
            
            'empiar'    => 'EMPIAR-\d{5,}',
            
            'encode'    => 'ENCSR[A-Z0-9]+', // ENCODE 
            
            'ensembl'   => 'ENS[A-Z]{4}\d{11}',   // ENSBTAG00000011038
            
            'insdcgca'  => '(GCA_[0-9]{9}(\.[0-9]+)?)', // insdc.gca
            
            // https://www.ncbi.nlm.nih.gov/genbank/acc_prefix/
            //'genbank'   => '\b([A-Z]\d{5}|[A-Z]{2}\d{6})\b',
            'genbank'   => '\b([A-Z]{2}\d{6})\b', // just 2 letters + 6 digits
            
            'gisaidisl' => '(EPI(_ISL_)?\d+)', // not in identifiers.org
            
            'geo'       => 'GSM\d{5,}', // modified https://registry.identifiers.org/registry/geo
            
            //'massive'   => 'MSV\d{9}', // https://massive.ucsd.edu/
            
            // https://www.ncbi.nlm.nih.gov/books/NBK21091/table/ch18.T.refseq_accession_numbers_and_mole/?report=objectonly
            'nm'        => '(N[CM]_\d{6}(\.[0-9]+)?)', 
            
            'gse'       => '((GEO:\s*)?GSE\d{5,})',
            
            'hpa'       => '((CAB|HPA)\d{6})', // http://www.proteinatlas.org/search/CAB004592
            'interpro'  => 'IPR\d{6}',
            
            'pdb'     => '\b((PDB:\s*)?[0-9][A-Za-z][A-Za-z0-9]{2})\b', // PDB, likely lots of false hits unless we include prefix
            
            'pfam'      => '(PF\d{5}(.\d{1,2})?)', // PFAM seems to have versions, e.g. PF01493.23)
            'prjna'     => 'PRJ[CDEN][A-Z]\d+', // https://registry.identifiers.org/registry/bioproject
            'pxd'       => 'PXD\d{6}', // https://www.proteomexchange.org    
            'sra'       => '[SED]R[APRSXZ]\d+', // https://registry.identifiers.org/registry/insdc.sra
            
            'up'        => 'UP\d{9}', // https://www.uniprot.org/proteomes/UP000006548,
            
            'doi'		=> 'https',
        );     




	$mode = 0; // just include dataset id
	//$mode = 1; // dataset id and mode of citation
	
	$g = array();
	$m = array();
	
	foreach ($gold as $article => $data)
	{
		foreach ($data as $id => $type)
		{
			$row = [$article, $id];
			
			if ($mode == 1)
			{
				$row[] = $type;
			}
			
			$g[] = join("|", $row);
		}
	}
	
	foreach ($model as $article => $data)
	{
		foreach ($data as $id => $type)
		{
			$row = [$article, $id];
			
			if ($mode == 1)
			{
				$row[] = $type;
			}
			
			
			$m[] = join("|", $row);
		}
	}
	
	
	
	// print_r($g);
	//print_r($m);
	
	$tpset = array_intersect($g, $m);
	$fpset = array_diff($m, $g);
	$fnset = array_diff($g, $m);
	
	$dois = array();
	
	$unknown = array();
	
	$result = array();
	
	$bad_types = array();
	
	$input = array($tpset, $fpset, $fnset);
	
	foreach ($input as $index => $input_data)
	{
		foreach ($input_data  as $row)
		{
			$parts = explode("|", $row);
			
			$article_id = $parts[0];
			$dataset_id = $parts[1];
			
			$type = null;
			if (count($parts) == 3)
			{
				$type = $parts[2];
			}
			
			//print_r($parts);
			$data_type = 'unknown';
			$matched = false;
			
			foreach ($patterns as $db => $pattern)
			{

				if (0) // separate out DOIs by prefix
				{
					if (preg_match('/https:\/\/doi.org\/(10\.\d+)\//', $dataset_id, $m))
					{
						$data_type = $m[1];
						$matched = true;
					}
				}
				
				if (!$matched)
				{
				
					if (preg_match('/' . str_replace('/', '\/', $pattern) . '/', $dataset_id))
					{
						$data_type = $db;
						$matched = true;
						
						// echo "Found $dataset_id $db $pattern\n";
					}
				}
				
				if ($matched == true) break;
				
				/*
				if (preg_match('/https:\/\/doi.org\/(10.5281)\//', $dataset_id, $m))
				{
					$data_type = $m[1];
					echo $dataset_id . "\n";
					$matched = true;
				}
				*/
				
				if ($matched == true) break;
				
			
			}
			
			if (!$matched)
			{
				$unknown[] = $dataset_id;
			}
			
			/*
			if ($data_type = 'unknown')
			{
				echo "What is $dataset_id?\n";
				exit();
			}
			*/
			
			
			if (!isset($result[$data_type]))
			{
				$result[$data_type] = [0, 0, 0]	;	
			}
			
			$result[$data_type][$index]++;
			
			if ($index == 1)
			{
				$bad_types[$dataset_id] = $type;
			}
			
			
			
		}
	}
	
	//print_r($result);
	
	//exit();
	
	//print_r($unknown);
	
	// print_r($bad_types);
	
	foreach ($result as $data_type => $scores)
	{
		echo str_pad($data_type, 16, ' ', STR_PAD_LEFT);
		
		echo '| ';
		
		if ($scores[0] == 0 && ($scores[1] == 0 || $scores[2] == 0))
		{
			$f1 = 0;
		}
		else
		{
			$precision = $scores[0] / ($scores[0] + $scores[1]);
			$recall = $scores[0] / ($scores[0] + $scores[2]);
			
			if ($precision == $recall && $precision == 0)
			{
				$f1 = 0;
			}
			else
			{
				$f1 = 2 * ($precision * $recall) / ($precision + $recall);
			}
		}
		
		echo round($f1,2) . "\n";
		
	
	}
	
}

if (0)
{
	echo "Correct matches\n";

	print_r($tpset);
}

if (0)
{
	echo "False positives, you said there is a citation when there isn't\n";
	print_r($fpset);
}

if (1)
{
	echo "False negatives, you missed these ones\n";
	print_r($fnset);
}

if (1)
{
	$tp = count($tpset);
	$fp = count($fpset);
	$fn = count($fnset);
	
	if ($mode == 0)
	{
		echo "\nScoring just identifier matches (e.g., did we get the DOI)\n\n";
	}
	if ($mode == 1)
	{
		echo "\nScoring identifier classification (did we get primary vs. secondary correct?)\n\n";
	}
	
	echo "true positives = $tp, false positives = $fp, false negatives = $fn\n";
	
	$precision = $tp / ($tp + $fp);
	$recall = $tp / ($tp + $fn);
	
	if ($precision == $recall && $precision == 0)
	{
		$f1 = 0;
	}
	else
	{
		$f1 = 2 * ($precision * $recall) / ($precision + $recall);
	}
	
	echo "Precision = $precision\n";
	echo "Recall = $recall\n";
	echo "Score = $f1\n";
}

if (0)
{
	// Analyse the missed cases for XML
	$missed = array();
	
	print_r($fnset);	
	
	foreach ($fnset as $item)
	{
		$parts = explode("|", $item);
		
		$id = $parts[0];
		
		if (!isset($missed[$id]))
		{
			$missed[$id] = array();
		}
		
		$missed[$id][] = $parts[1];
	}

	ksort($missed);
		
	$html = '<html>';
	$html .= '<body>';
	
	$no_xml = array();
	
	$articles_with_missing = array_keys($missed);
	foreach ($articles_with_missing as $id)
	{
		$path = 'train/XML/' . $id . '.xml';
		
		if (!file_exists($path))
		{
			$no_xml[] = $id;
		}
	}
	
	
	
	// check whether have XML for these

	//print_r($missed);
	//print_r($no_xml);
	
	echo "Missed documents=" . count($articles_with_missing) . " of which " . count($no_xml) . " have no XML\n";
	
	foreach ($no_xml as $id)
	{
		unset($missed[$id]);
	}
	
	
	// what data did we miss in XML files?
	$missed_text = '';
	foreach ($missed as $id => $data_ids)
	{
		// get file type	
		$html .= '<h2>' . "\n$id [" . strtoupper(xml_type($id)) . "] . </h2>";
		
		$html .= '<p><a href="' . get_xml_filename($id) . '" target="_new">' . get_xml_filename($id) . '</a></p>';
		
		$text = file_get_contents(get_xml_filename($id));
		
		$html .= '<ul>';
		
		print_r($gold[$id]);
		
		foreach ($gold[$id] as $k => $v)
		{
			if (in_array($k, $data_ids))
			{
			
				$html .= '<li>';
				$html .= "   $k";
				
				$k = str_replace('https://doi.org/', '', $k);
				
				if (strstr($text, $k))
				{
					$html .= "  *** in text ***";
				}
				
				$html .= '</li>';
			}
		}

		$html .= '</ul>';
	}
	
	file_put_contents('missed.html', $html);
	
	
	//print_r($gold);
	
}

if (0)
{
	// Analyse the missed cases for PDF
	$missed = array();
	
	foreach ($fnset as $item)
	{
		$parts = explode("|", $item);
		
		$missed[] = $parts[0];
	}
	
	$missed = array_unique($missed);
	
	print_r($missed);
	
	// what data did we miss in text files?
	$missed_text = '';
	foreach ($missed as $id)
	{
		
		$text = file_get_contents(get_text_filename($id));
		
		foreach ($gold[$id] as $k => $v)
		{
			$missed_text .= "   $k";
			
			$k = str_replace('https://doi.org/', '', $k);
			
			if (strstr($text, $k))
			{
				$missed_text .= "  *** in text ***";
			}
			
			$missed_text .= "\n";
		}
	}
	
	echo $missed_text;
	
	file_put_contents('missed.txt', $missed_text);
	
	
	//print_r($gold);
	
}

?>

