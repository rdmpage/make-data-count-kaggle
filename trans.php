<?php


// tei
if (0)
{
	
	$xml_filename = 'train/XML/10.3133_ofr20231027.xml';
	$xml_filename = 'train/XML/10.3133_fs20233046.xml';
	
	//$xml_filename = 'train/XML/10.17581_bp.2020.09104.xml';
	//$xml_filename = 'train/XML/10.1002_ecs2.4619.xml';
	//$xml_filename = 'train/XML/10.5194_essd-12-1287-2020.xml';
	//$xml_filename = 'train/XML/10.5937_bnhmb1811227u.xml';
	
	//$xml_filename = 'c3ddf729-d783-4d70-b69b-cf16e1c5d219_15142_-_mark_field.pdf.tei.xml';
	$xml_filename = 'sdata201433.pdf.tei.xml';
	
	$xml_filename = 'train/XML/10.1002_ecs2.4619.xml';	
	
	$xml_filename = 'train/XML/10.5194_essd-2023-198.xml';	
	
	$xml_filename = 'train/XML/10.3133_cir1497.xml';	
	
	$xslt_filename = 'tei.xsl';
	$xslt_filename = 'article-xslt/tei-html.xsl';
}


// Wiley
if (0)
{
	$xml_filename = 'explore/done/10.1002_ece3.5058.xml';
	$xml_filename = 'train/XML/10.1002_ejic.201900904.xml';
	$xml_filename = 'train/XML/10.1111_ddi.13153.xml';
	$xml_filename = 'train/XML/10.1111_mec.16743.xml';
	
	//$xml_filename = 'train/XML/10.1002_esp.5090.xml';
	
	
	$xml_filename = 'explore/not-in-training/cas.12935.xml';
	
	$xml_filename = 'train/XML/10.1002_esp.5090.xml';
	
	$xslt_filename = 'wiley.xsl';
	$xslt_filename = 'article-xslt/wiley-html.xsl';
}

// JATS
if (1)
{

	$xml_filename = 'train/XML/10.1111_eva.12151.xml';
	$xml_filename = 'train/XML/10.3897_zookeys.500.9360.xml';
	
	//$xml_filename = 'train/XML/10.1186_s13059-020-1949-z.xml';
	
	//$xml_filename = 'train/XML/10.1186_s12885-018-4229-5.xml';
	//$xml_filename = 'train/XML/10.7717_peerj.12422.xml';
	$xml_filename = 'train/XML/10.7717_peerj.10452.xml';
	$xml_filename = 'train/XML/10.1186_s13059-019-1924-8.xml';
	
	$xml_filename = 'train/XML/10.12688_f1000research.13622.1.xml';
	$xml_filename = 'train/XML/10.12688_f1000research.11698.1.xml';
	
	$xml_filename = 'train/XML/10.1371_journal.pone.0146274.xml';
	
	$xslt_filename = 'article-xslt/jats-html.xsl';


}

// BioC
if (0)
{
	$xml_filename = 'train/XML/10.1111_cas.12935.xml';
	$xslt_filename = 'article-xslt/bioc-html.xsl';

}

if (0)
{
	$xml_filename = 'test.xml';
	$xslt_filename = 'test.xsl';

}



// convert
$xml = file_get_contents($xml_filename);

$xslt = new xsltProcessor;

$xslDoc = new DOMDocument(); 
$xslDoc->load($xslt_filename, LIBXML_NOCDATA); 
$xslt->importStylesheet($xslDoc); 

$xmlDoc = new DOMDocument(); 
$xmlDoc->loadXML($xml); 

$output = $xslt->transformToXML($xmlDoc); 

echo $output;

file_put_contents('output.xml', $output);



?>
