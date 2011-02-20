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

  public function __toArray() {
    return array();
  }
 
}

$API = new ukasz_api();
$API->debug = false;
$hostname='192.168.200.100';
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
$clear_attrs = array('prefix'); //lista atrybutów które chcemy wyczyscic podczas seta

  $API->write('/system/logging/print');
  $has = $API->read(true);
  if (count($has) > count($array)) {
    //remove all 
    $API->write('/system/logging/remove', false);
    $tmp = array_shift($has);
    $command = '=.id=' . $tmp['.id']; 
    foreach($has as $id => $data) {
     $command .= ',' . $data['.id'];
    }
 
    $API->write($command);
    $API->read();
    $has = array();
  }
  foreach($array as $id => $data) {
    // $elem = znajdz element w tablicy has, który ma atrybut action = $data['action'] a jesli go nie ma zwróc array()

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
        $API->write_array($data);
        $API->read();
      }
    }
    // do tablicy wniebowziete wrzuc sobie elem['.id'] (jesli elem istnieje, tj np zawiera .id
  }
  // przejedz po wszystkich $has, i dla tych $has, których .id nie znajduje sie w tablicy wniebowziete dodaj te elementy do tablicy czysciec
  // przejedz po tablicy czysciec i zrob to co w liniach 53:58
  $API->disconnect();	    
};

?>
