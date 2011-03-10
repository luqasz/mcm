<?php
require('routeros_api.class.php');
class ukasz_api extends routeros_api {

  public function write_array(array $array) {
    $count = count($array);
    $is_last = 1 == $count;
    $i = 1;
    foreach($array as $name => $value) {
      $this->write('='.$name.'='.$value, $is_last);
      $i++;
     if ($i==$count) {
       $is_last = true;
     } 
    }
  }
 
}

$API = new ukasz_api();
$API->debug = true;
$hostname='10.194.3.249';
#$hostname='172.30.30.60';
$user='admin';
$pass='dupa';

if ($API->connect($hostname, $user, $pass)) {
$data_from_file = file('configfile', FILE_SKIP_EMPTY_LINES);
$tobeset = array();
sort($data_from_file);
foreach ($data_from_file as $key => $line) {
$rows = preg_split("/[\s]+/", $line);
$where = trim(array_shift($rows), "/");
array_pop($rows);
foreach ($rows as $to_build) {
	list ($keyy, $value) = explode("=", $to_build);
	$tmp[$keyy] = $value;
}
$tobeset[$where][] = $tmp;
unset($tmp);
}
$clear_attrs = array(); 
foreach ($tobeset as $tobesetid => $tobesetarray) {

  $API->write('/' . $tobesetid . '/print');
  $has = $API->read(true);
  foreach($tobesetarray as $id => $data) {
    $elem = isset($has[$id]) ? $has[$id] : array();
    $diff = array_diff($data,  $elem);
    foreach($clear_attrs as $attr) {
      if (array_key_exists($attr, $elem) && $elem[$attr] != '') {
        $diff[$attr] = '';
      }
    }
    if ($diff) {
      if (empty($elem)) {
        $API->write('/' . $tobesetid . '/add', false);
        $API->write_array($data);
        $API->read();
      } else { 
        $API->write('/' . $tobesetid . '/set', false);
		if (array_key_exists('.id', $elem)) {
        		$API->write('=.id=' . $elem['.id'], false);
		}
        $API->write_array($diff);
        $API->read();
      }
    }
        if (array_key_exists('.id', $elem)) {
                $save[] = $elem['.id'];
        }
  }
  foreach($has as $id => $value) {
        if (isset($value['.id'])) {
                $collect_ids[] = $value['.id'];
                }
        }
	if (!empty($collect_ids) && !empty($save)) {
    		$remove = array_diff($collect_ids, $save);
		}
        if (!empty($remove)) {
                $API->write('/' . $tobesetid . '/remove', false);
                $tmp = array_shift($remove);
                $command = '=.id=' . $tmp; 
                foreach($remove as $id => $value) {
                        $command .= ',' . $value;
                }
        $API->write($command);
        $API->read();
        }         
}   
$API->disconnect();   
};
?>
