<?php

#jesli nie zawiera id i jest tylko jedno to jest to tylko do odczytu badz pojedyncze menu
#poprawic clear attrs. zeby lykal cala reszta (porownujac co jest minus to co sie ustawia) oprocz default
# czy cos moze byc disabled czy enabled (glupota mikrotikowa


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
$hostname='10.194.3.241';
$user='admin';
$pass='dupa';


 if ($API->connect($hostname, $user, $pass)) {
  $array = array( 
  0 => array(
    'action' => 'remote',
    'topics' => 'info,!wireless,!debug,!route,!ospf'), 
  1 => array(
    'action' => 'remote',
    'topics' => 'warning'), 
  2 => array(
    'action' => 'remote',
    'topics' => 'error'), 
  3 => array(
    'action' => 'echo',
    'topics' => 'critical')
);
$clear_attrs = array('prefix'); 

  $API->write('/system/logging/print');
  $has = $API->read(true);
  foreach($array as $id => $data) {
    $elem = isset($has[$id]) ? $has[$id] : array();
    $diff = array_diff($data,  $elem);
    foreach($clear_attrs as $attr) {
      if (array_key_exists($attr, $elem) && $elem[$attr] != '') {
        $diff[$attr] = '';
      }
    }
    if ($diff) {
      if (empty($elem)) {
        $API->write('/system/logging/add', false);
        $API->write_array($data);
        $API->read();
      } else { 
        $API->write('/system/logging/set', false);
        $API->write('=.id=' . $elem['.id'], false);
        $API->write_array($diff);
        $API->read();
      }
    }
	if (isset($elem['.id'])) {
		$save[] = $elem['.id'];
	}
  }
  foreach($has as $id => $value) {
	$collect_ids[] = $value['.id'];
	}
    $remove = array_diff($collect_ids, $save);
	if (!empty($remove)) {
		$API->write('/system/logging/remove', false);
    		$tmp = array_shift($remove);
    		$command = '=.id=' . $tmp; 
    		foreach($remove as $id => $value) {
     			$command .= ',' . $value;
    		}
	$API->write($command);
	$API->read();
	}	
$API->disconnect();	    
};
?>
