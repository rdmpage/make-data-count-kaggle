<?php

// Create a subset of XML input



//----------------------------------------------------------------------------------------
function xml_type($xml)
{
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

$basedir = dirname(__FILE__) . '/train/XML';

$want ='bioc';
$want ='tei';
$want ='wiley';
$want ='jats';
$dir =  dirname(__FILE__) . '/' . $want;

if (!file_exists($dir))
{
    $oldumask = umask(0); 
    mkdir($dir, 0777);
    umask($oldumask);
}

$files = scandir($basedir);

foreach ($files as $filename)
{
	if (preg_match('/xml$/', $filename))
	{
		$xml_filename = $basedir . '/' . $filename;
		$xml = file_get_contents($xml_filename);
		
		$format = xml_type($xml);
		
		if ($format == $want)
		{
			
			copy($xml_filename, $dir . '/' . $filename);
		}
	
	}


}

?>
