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

$shortopts 	= "p:u:a:vhl:t:c:";

//check for keys in array
function array_keys_exist($keys,$array) {
    if (count (array_intersect($keys,array_keys($array))) == count($keys)) {
        return true;
    }
}

//must specify user password and address
$mandatoryoptions = array('p','u','a');
$options = getopt($shortopts);
if (array_key_exists('h', $options)) {
	echo "You must specify -u username, -p password and -a address\n";
	echo "\t-a address. can be fqdn\n";
	echo "\t-c configuration file for address. defaults to specified address.conf\n";
	echo "\t-d delay between connection attempts in seconds (defaults to 2)\n";
	echo "\t-h this help\n";
	echo "\t-p password\n";
	echo "\t-t connection attempt timeout and data read timeout (defaults to 2)\n";
	echo "\t-u username\n";
	echo "\t-v show debug information. be verbose what is going on\n";
	} else {
		if (array_keys_exist($mandatoryoptions,$options)) {
			$API->debug = array_key_exists('v', $options); 
			$configfile = array_key_exists('c', $options) ? $options['c'] : $options['a'] . '.conf'; 
			$API->delay = array_key_exists('d', $options) ? $options['d'] : 2; 
			$API->timeout = array_key_exists('t', $options) ? $options['t'] : 2; 
			
				if ($API->connect($options['a'], $options['u'], $options['p'])) {
					$data_from_file = file($configfile, FILE_SKIP_EMPTY_LINES | FILE_IGNORE_NEW_LINES);
					$data_from_file = (preg_grep('/^#.*/', $data_from_file, PREG_GREP_INVERT));
					$tobeset = array();

					foreach ($data_from_file as $line) {
						$rows = preg_split("/[\s]+/", $line);
						$where = trim(array_shift($rows), "/");
							foreach ($rows as $to_build) {
								list ($key, $value) = explode("=", $to_build);
								$tmp[$key] = $value;
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
				}
			} else {
			echo "You must specify -u username, -p password, -a address\n";
		}
};
?>
