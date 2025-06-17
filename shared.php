<?php

// shared code

//----------------------------------------------------------------------------------------
function extract_identifier_patterns($text)
{
	$identifiers = array();
	
	$patterns = array(
		'genbank' 	=> '\b(?<genbank>[A-Z]\d{5}|[A-Z]{2}\d{6}|[A-Z]{4,6}\d{8,10}|[A-J][A-Z]{2}\d{5})(\.\d+)?\b',

	
		'arx'		=> '(?<arx>E-GEOD-\d+)', // https://www.ebi.ac.uk/biostudies/arrayexpress
		'biosample'	=> '(?<biosample>SAM[NED](\w)?\d+)', // https://registry.identifiers.org/registry/biosample
		'chembl' 	=> '(?<chembl>CHEMBL\d+)',
		'gisaid' 	=> '(?<gisaid>EPI\d+)',
		'gxaexpt'	=> '(?<gxaexpt>[AEP]-\w{4}-\d+)', // https://registry.identifiers.org/registry/gxa.expt
		'interpro' 	=> '(?<interpro>IPR\d{6})',
		'pfam'		=> '(?<pfam>PF\d{5})',
		'prjna'		=> '(?<prjna>PRJ[DEN][A-Z]\d+)', // https://registry.identifiers.org/registry/bioproject
		'pxd'		=> '(PXD\d{6)', // https://www.proteomexchange.org	
		'sra'		=>  '(?<sra>[SED]R[APRSXZ]\d+)', // https://registry.identifiers.org/registry/insdc.sra
		
		//'rrid'		=> '(?<rrid>RRID:[a-zA-Z]+.+)', // https://registry.identifiers.org/registry/rrid
		
		// RRID is really just a prefix to an existing identifier, so pottentially any thing could have RRID as a prefix
		'rrid'		=> '(?<rrid>RRID:[A-Z][A-Z0-9_]+)',
		
	);
	
	foreach ($patterns as $namespace => $pattern)
	{
		preg_match_all('/' . $pattern . '/', $text, $m);
		
		//print_r($m);
		
		if (isset($m[$namespace]) && count($m[$namespace]) > 0)
		{
			$identifiers[$namespace] = array();
		
			foreach ($m[$namespace] as $id)
			{
				// for now clean off RRID prefix to match training data
				$id = preg_replace('/^RRID:/', '', $id);
				$identifiers[$namespace][] = $id;
			}
	
		}
	}
	
	return $identifiers;

}	

//----------------------------------------------------------------------------------------
function clean_doi($doi)
{
	$doi = preg_replace('/[;|,|\.|\)]$/', '', $doi);
	$doi = preg_replace('/[;|,|\.|\)]$/', '', $doi);
	$doi = preg_replace('/^doi:/i', 'https://doi.org/', $doi);

	$doi = preg_replace('/^10\./i', 'https://doi.org/10.', $doi);
	
	$doi = preg_replace('/http:\/\/dx\./', 'https://', $doi);

	// why does this even happen?
	// 10.7717_peerj.12422
	$doi = preg_replace('/\(\d+$/', '', $doi);
	
	// 10.7554_elife.29944,https://doi.org/10.5061/dryad.8153gAvailable
	// https://doi.org/10.13039/501100001809National
	$doi = preg_replace('/(Available|Danmarks|European|Gordon|National|Norges)$/', '', $doi);

	$doi = preg_replace('/\s+/i', '', $doi);
	
	$doi = strtolower($doi);

	return $doi;
}


//----------------------------------------------------------------------------------------

if (0)
{
	$text = 'genbank AB000126 and othgers';

	extract_identifier_patterns($text);
}

?>


