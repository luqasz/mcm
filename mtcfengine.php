<?php
require ('routeros_api.class.php');
class ukasz_api extends routeros_api {
	public function write_array(array $array) {
		$count = count ( $array );
		$is_last = 1 == $count;
		$i = 1;
		foreach ( $array as $name => $value ) {
			$this->write ( '=' . $name . '=' . $value, $is_last );
			$i ++;
			if ($i == $count) {
				$is_last = true;
			}
		}
	}
}

function show_help() {
?>
You must specify -u -p -a
	-a address. can be fqdn
	-c configuration file for address. defaults to specified address.conf
	-d delay between connection attempts in seconds (defaults to 2)
	-h this help
	-p password
	-t connection attempt timeout and data read timeout (defaults to 2)
	-u username
	-v show debug information. be verbose what is going on
<?php
}

function show_connection_error() {
?>
Connection fault
<?php
}

function show_file_error($file) {
echo "Specified file \"$file\" does not exist.\n";
}


class Parser {

	public function __construct($file) {
		$this->_file	= $file;
	}

	public function parseFile() {
     	$data_from_file = file ( $this->_file, FILE_SKIP_EMPTY_LINES | FILE_IGNORE_NEW_LINES );
		$data_from_file = (preg_grep ( '/^#.*/', $data_from_file, PREG_GREP_INVERT ));

		foreach ( $data_from_file as $line ) {
			$rows = preg_split ( "/[\s]+/", $line );
			$where = trim ( array_shift ( $rows ), "/" );
			foreach ( $rows as $to_build ) {
		  		list ( $key, $value ) = explode ( "=", $to_build );
					$tmp [$key] = $value;
				}
				$tobeset [$where] [] = $tmp;
				unset ( $tmp );
		}
		return array($tobeset);
    }
}

class Mtcfengine {

    public function __construct($address, $user, $password) {
		$this->_address  = $address;
		$this->_user     = $user;
		$this->_password = $password;
		$this->api       = new ukasz_api();
    }

	public function connect() {
	return $this->api->connect($this->_address, $this->_user, $this->_password);

	}

    public function configure(array $parsedoptions) {
		foreach ($parsedoptions as $tobesetid => $tobesetarray ) {
			$this->api->write ( '/' . $tobesetid . '/print' );
			$has = $this->api->read ( true );
			foreach ( $tobesetarray as $id => $data ) {
				$elem = isset ( $has [$id] ) ? $has [$id] : array ();
				$diff = array_diff ( $data, $elem );
				$this->save_diff($diff, $elem, $tobesetid, $data);
				if (array_key_exists ( '.id', $elem )) {
					$save [] = $elem ['.id'];
				}
			}
			foreach ( $has as $id => $value ) {
				if (isset ( $value ['.id'] )) {
					$collect_ids [] = $value ['.id'];
				}
			}
			if (! empty ( $collect_ids ) && ! empty ( $save )) {
				$this->remove(array_diff ( $collect_ids, $save ), $tobesetid);
			}
		}
    }

    protected function save_diff($diff, $elem, $tobesetid, array $data) {
    	if (!$diff) {
    		return;
    	}
		if (empty ( $elem )) {
			$this->api->write ( '/' . $tobesetid . '/add', false );
			$this->api->write_array ( $data );
			$this->api->read ();
		} else {
			$this->api->write ( '/' . $tobesetid . '/set', false );
			if (array_key_exists ( '.id', $elem )) {
				$this->api->write ( '=.id=' . $elem ['.id'], false );
			}
			$this->api->write_array ( $diff );
			$this->api->read ();
		}
    }

    protected function remove($remove, $tobesetid) {
    	if (empty($remove)) {
    		return;
    	}
		$this->api->write ( '/' . $tobesetid . '/remove', false );
		$tmp = array_shift ( $remove );
		$command = '=.id=' . $tmp;
		foreach ( $remove as $id => $value ) {
			$command .= ',' . $value;
		}
		$this->api->write ( $command );
		$this->api->read ();
    }

    public function disconnect() {
  		$this->api->disconnect();
    }
}


interface MtcfengineParams {
	public function getUser();
	public function getPassword();
	public function getAddress();
	public function isValid();
	public function isHelp();
	public function emptyParams();
	public function getDebug();
	public function getTimeout();
	public function getDelay();
	public function getConfigFile();
}

class MtcfengineCLIParams implements MtcfengineParams {
	private $required = array('u' => '0', 'p' => '0', 'a' => '0');

	public function __construct() {
		$this->params = getopt("p:u:a:vhl:t:c:");
	}

	public function getUser() {
		return $this->getOption('u');
	}

	public function getPassword() {
		return $this->getOption('p');
	}

	public function getAddress() {
		return $this->getOption('a');
	}

	public function getConfigFile() {
    	return $this->getOption('c', $this->getAddress() . 'conf');
    }

    public function getDebug() {
    	return $this->getOption('v');
	}

    public function isHelp() {
		return $this->getOption('h');
	}

    public function getDelay() {
    	return $this->getIntOption('l', $default = 2);
    }
    public function getTimeout() {
    	return $this->getIntOption('t', $default = 2);;
    }

	public function emptyParams() {
		return empty($this->params);
	}

	public function isValid() {
		return count(array_values(array_intersect_key($this->params, $this->required))) == count($this->required);
	}

	private function getIntOption($key, $default = 0) {
		return is_int($key, $this->params) ? $this->params[$key] : $default;
	}

	private function getOption($key, $default = false) {
		return array_key_exists($key, $this->params) ? $this->params[$key] : $default;
	}
}

$options = new MtcfengineCLIParams();

if (!$options->isValid() || $options->isHelp() || $options->emptyParams()) {
	show_help();
	exit;
}

if (!file_exists($options->getConfigFile())) {
	show_file_error($options->getConfigFile());
	exit;
}

$parser = new Parser($options->getConfigFile());

$configurator = new Mtcfengine($options->getAddress(), $options->getUser(), $options->getPassword());

if (!$configurator->connect()) {
	show_connection_error();
	exit();
}

$configurator->configure($parser->parseFile());
$configurator->disconnect();

?>
