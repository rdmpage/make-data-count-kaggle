<?php


$dirs = ['test', 'train'];
//$dirs = ['test'];


$types = ['pdf', 'xml'];

foreach ($dirs as $dir)
{
	echo "$dir\n";
	
	$pdf = [];
	$xml = [];

	foreach ($types as $type)
	{
		$files = scandir($dir . '/' . $type);
		
		foreach ($files as $filename)
		{
			if (preg_match('/\.xml$/', $filename))
			{
				$xml[] = basename($filename, '.xml');
			}
		}
		
		foreach ($files as $filename)
		{
			if (preg_match('/\.pdf$/', $filename))
			{
				$pdf[] = basename($filename, '.pdf');
			}
		}
	}
	
	//print_r($pdf);
	//print_r($xml);
	
	$pdf_only = array_diff($pdf, $xml);
	
	echo "PDF only\n";
	print_r($pdf_only);
	
	$xml_only = array_diff($xml, $pdf);
	
	echo "XML only\n";
	print_r($xml_only);
	
	// XML types
	
	$formats = array();
	
	foreach ($xml as $id)
	{
		$filename = $dir . '/' . $type . '/' . $id . '.xml';
		
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
		
		if (!isset($formats[$format]))
		{
			$formats[$format] = array();
		}
		$formats[$format][] = $id;
		
	}
	
	print_r($formats);
	
	
	echo "---------\n";

}

?>
