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
			
				print_r($obj);	
				
				if ($obj->dataset_id != "Missing")
				{
					if (!isset($data[$obj->article_id]))
					{
						$data[$obj->article_id] = array();
					}
					$data[$obj->article_id][$obj->dataset_id] = $obj->type;
				}
			}
		}	
		$row_count++;
	}	
	
	return $data;
}

//----------------------------------------------------------------------------------------


// gold standard
$filename = 'train_labels.csv';

$gold = read_data($filename);

//print_r($gold);

$filename = 'output.csv';
$filename = 'submission.csv';

$model = read_data($filename);

//print_r($model);



$mode = 0; // just include dataset id
$mode = 1; // dataset id and mode of citation

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
		
		$g[] = join("-", $row);
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
		
		
		$m[] = join("-", $row);
	}
}

// print_r($g);
// print_r($m);

$tpset = array_intersect($g, $m);
$fpset = array_diff($m, $g);
$fnset = array_diff($g, $m);

echo "Correct matches\n";
print_r($tpset);

echo "False hits, you said there is a citation when there isn't\n";
print_r($fpset);

echo "False negatives, you missed these ones\n";
print_r($fnset);

$tp = count($tpset);
$fp = count($fpset);
$fn = count($fnset);

echo "true positives = $tp, false positives = $fp, false negatives = $fn\n";

$precision = $tp / ($tp + $fp);
$recall = $tp / ($tp + $fn);
$f1 = 2 * ($precision * $recall) / ($precision + $recall);

echo "precision = $precision\n";
echo "Recall = $recall\n";
echo "Score = $f1\n";



?>

