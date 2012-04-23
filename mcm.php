<?php
class routeros_api {
	private $error_no;				// Variable for storing connection error number, if any
	private $error_str;				// Variable for storing connection error text, if any
	public $connected = false;		// Connection state
	private $socket;				// Variable for storing socket resource
	private $attempts = 3;
	public function __construct(MtcfengineCLIParams $params, monitorHandler $monitor) {
	$this->params = $params;
	$this->monitor = $monitor;
	}
	/**************************************************
	 *
	 *************************************************/
	function encode_length($length) {
		if ($length < 0x80) {
			$length = chr($length);
		}
		else
		if ($length < 0x4000) {
			$length |= 0x8000;
			$length = chr( ($length >> 8) & 0xFF) . chr($length & 0xFF);
		}
		else
		if ($length < 0x200000) {
			$length |= 0xC00000;
			$length = chr( ($length >> 8) & 0xFF) . chr( ($length >> 8) & 0xFF) . chr($length & 0xFF);
		}
		else
		if ($length < 0x10000000) {
			$length |= 0xE0000000;
			$length = chr( ($length >> 8) & 0xFF) . chr( ($length >> 8) & 0xFF) . chr( ($length >> 8) & 0xFF) . chr($length & 0xFF);
		}
		else
		if ($length >= 0x10000000)
			$length = chr(0xF0) . chr( ($length >> 8) & 0xFF) . chr( ($length >> 8) & 0xFF) . chr( ($length >> 8) & 0xFF) . chr($length & 0xFF);
		return $length;
	}
	/**************************************************
	 *
	 *************************************************/
	function connect($ip, $login, $password) {
		for ($ATTEMPT = 1; $ATTEMPT <= $this->attempts; $ATTEMPT++) {
			$this->connected = false;
			$this->monitor->show_info('Connection attempt #' . $ATTEMPT . ' to ' . $ip . ':' . $this->params->getPort());
			if ($this->socket = @fsockopen($ip, $this->params->getPort(), $this->error_no, $this->error_str, $this->params->getTimeout()) ) {
				socket_set_timeout($this->socket, $this->params->getTimeout());
				$this->write('/login');
				$RESPONSE = $this->read(false);
				if ($RESPONSE[0] == '!done') {
					if (preg_match_all('/[^=]+/i', $RESPONSE[1], $MATCHES) ) {
						if ($MATCHES[0][0] == 'ret' && strlen($MATCHES[0][1]) == 32) {
							$this->write('/login', false);
							$this->write('=name=' . $login, false);
							$this->write('=response=00' . md5(chr(0) . $password . pack('H*', $MATCHES[0][1]) ) );
							$RESPONSE = $this->read(false);
							if ($RESPONSE[0] == '!done') {
								$this->connected = true;
								break;
							}
						}
					}
				}
				fclose($this->socket);
			}
			sleep($this->params->getDelay());
		}
		return $this->connected;
	}
	/**************************************************
	 *
	 *************************************************/
	function disconnect() {
		fclose($this->socket);
		$this->connected = false;
		$this->monitor->show_info('Disconnected');
	}
	/**************************************************
	 *
	 *************************************************/
	function parse_response($response) {
		if (is_array($response) ) {
			$PARSED = array();
			$CURRENT = null;
			foreach ($response as $x) {
				if (in_array($x, array('!fatal', '!re', '!trap') ) ) {
					if ($x == '!re')
						$CURRENT = &$PARSED[];
					else
						$CURRENT = &$PARSED[$x][];
				}
				else
				if ($x != '!done') {
					if (preg_match_all('/[^=]+/i', $x, $MATCHES) )
						$CURRENT[$MATCHES[0][0]] = (isset($MATCHES[0][1]) ? $MATCHES[0][1] : '');
				}
			}
			return $PARSED;
		}
		else
			return array();
	}
	/**************************************************
	 *
	 *************************************************/
        function array_change_key_name(&$array) {
                if (is_array($array) ) {
                        foreach ($array as $k => $v) {
                                $tmp = str_replace("-","_",$k);
                                $tmp = str_replace("/","_",$tmp);
                                if ($tmp) {
                                        $array_new[$tmp] = $v;
                                } else {
                                        $array_new[$k] = $v;
                                }
                        }
                        return $array_new;
                } else {
                        return $array;
                }
        }
        /**************************************************
         *
         *************************************************/
        function parse_response4smarty($response) {
                if (is_array($response) ) {
                        $PARSED = array();
                        $CURRENT = null;
                        foreach ($response as $x) {
                                if (in_array($x, array('!fatal', '!re', '!trap') ) ) {
                                        if ($x == '!re')
                                                $CURRENT = &$PARSED[];
                                        else
                                                $CURRENT = &$PARSED[$x][];
                                }
                                else
                                if ($x != '!done') {
                                        if (preg_match_all('/[^=]+/i', $x, $MATCHES) )
                                                $CURRENT[$MATCHES[0][0]] = (isset($MATCHES[0][1]) ? $MATCHES[0][1] : '');
                                }
                        }
                        foreach ($PARSED as $key => $value) {
                                $PARSED[$key] = $this->array_change_key_name($value);
                        }
                        return $PARSED;
                }
                else {
                        return array();
                }
        }
	/**************************************************
	 *
	 *************************************************/
   function read($parse = true) {
	   $receiveddone=false;
         $RESPONSE = array();
	       while (true) {
			// Read the first byte of input which gives us some or all of the length
			// of the remaining reply.
			$BYTE = ord(fread($this->socket, 1) );
			$LENGTH = 0;
			//echo "$BYTE\n";
			// If the first bit is set then we need to remove the first four bits, shift left 8
			// and then read another byte in.
			// We repeat this for the second and third bits.
			// If the fourth bit is set, we need to remove anything left in the first byte
			// and then read in yet another byte.
			if ($BYTE & 128) {
				if (($BYTE & 192) == 128) {
					$LENGTH = (($BYTE & 63) << 8 ) + ord(fread($this->socket, 1)) ;
				} else {
				if (($BYTE & 224) == 192) {
					$LENGTH = (($BYTE & 31) << 8 ) + ord(fread($this->socket, 1)) ;
					$LENGTH = ($LENGTH << 8 ) + ord(fread($this->socket, 1)) ;
				} else {
					if (($BYTE & 240) == 224) {
					$LENGTH = (($BYTE & 15) << 8 ) + ord(fread($this->socket, 1)) ;
					$LENGTH = ($LENGTH << 8 ) + ord(fread($this->socket, 1)) ;
					$LENGTH = ($LENGTH << 8 ) + ord(fread($this->socket, 1)) ;
						} else {
				    $LENGTH = ord(fread($this->socket, 1)) ;
					$LENGTH = ($LENGTH << 8 ) + ord(fread($this->socket, 1)) ;
					$LENGTH = ($LENGTH << 8 ) + ord(fread($this->socket, 1)) ;
					$LENGTH = ($LENGTH << 8 ) + ord(fread($this->socket, 1)) ;
					}
				}
			}
			} else {
			$LENGTH = $BYTE;
		}
        // If we have got more characters to read, read them in.
        if ($LENGTH > 0) {
           $_ = "";
           $retlen=0;
           while ($retlen < $LENGTH) {
           $toread = $LENGTH - $retlen ;
           $_ .= fread($this->socket, $toread);
           $retlen = strlen($_);
         }
         $RESPONSE[] = $_ ;
         $this->monitor->show_debug('>>> [' . $retlen . '/' . $LENGTH . ' bytes read.');
        }
        // If we get a !done, make a note of it.
         if ($_ == "!done")
         $receiveddone=true;
        $STATUS = socket_get_status($this->socket);
        if ($LENGTH > 0)
        $this->monitor->show_debug('>>> [' . $LENGTH . ', ' . $STATUS['unread_bytes'] . '] ' . $_);
       if ( (!$this->connected && !$STATUS['unread_bytes']) ||
        ($this->connected && !$STATUS['unread_bytes'] && $receiveddone) )
         break;
     }
     if ($parse)
       $RESPONSE = $this->parse_response($RESPONSE);
      return $RESPONSE;
     }
	/**************************************************
	 *
	 *************************************************/
	function write($command, $param2 = true) {
		if ($command) {
			$data = explode("\n",$command);
			foreach ($data as $com) {
			$com = trim($com);
			        fwrite($this->socket, $this->encode_length(strlen($com) ) . $com);
			        $this->monitor->show_debug('<<< [' . strlen($com) . '] ' . $com);
			}
			if (gettype($param2) == 'integer') {

				fwrite($this->socket, $this->encode_length(strlen('.tag=' . $param2) ) . '.tag=' . $param2 . chr(0) );

				$this->monitor->show_debug('<<< [' . strlen('.tag=' . $param2) . '] .tag=' . $param2);
			}
			else
			if (gettype($param2) == 'boolean')
				fwrite($this->socket, ($param2 ? chr(0) : '') );
			return true;
		}
		else
			return false;
	}
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

class Parser {

	public function __construct($file) {
		$this->_file = $file;
		$this->xml = new SimpleXMLElement($this->_file, NULL, TRUE);
	}

	public function parseFile() {
		foreach ($this->xml->rules->menu as $menu) {
			$tmp = array();
			foreach ($menu->rule as $rule) {
				foreach ($rule->children() as $child) {
					$tmp [ (string) $child->getName()] =  (string) $child;
				}
			$tobeset [ trim ((string) $menu['level'], "/" )] []= $tmp;
			unset ($tmp);
			}
			if (!isset($tobeset))
				$tobeset [ trim ((string) $menu['level'], "/" )] []= $tmp;
		}
		return $tobeset;
    }
}

class Mtcfengine {

	protected $api;

	public function __construct(routeros_api $api) {
		$this->api = $api;
	}

	public function configure(array $parsedconfigarray) {
		//for every menulevel (witch may contain many rules) get array with rules
		foreach ($parsedconfigarray as $menulevel => $tobesetarray ) {
			$this->api->write ( '/' . $menulevel . '/print' );
			//has = array containing all the rules from remote device in specified menulevel
			$has = $this->api->read ( true );
			$collect_ids = array();
			//get all '.id' from every rule in menulevel from table has (from existing rules on remote device)
			foreach ( $has as $id => $value ) {
				if (isset ( $value ['.id'] )) {
					$collect_ids[] = $value ['.id'];
				}
			}
			// reset sve array.  for every menulevel
			$save = array();
			// for every rule row. id = rule number  data = settings in id
			foreach ( $tobesetarray as $id => $data ) {
				//if we have a row (from remote device, doesn't matter what it contains), return the array containing all settings in specified row id (number), else return empty array
				$elem = isset ( $has [$id] ) ? $has [$id] : array ();
				//compare from data against elem. return array containing elements from data not present in elem. = what we want to set on remoe device
				$diff = array_diff ( $data, $elem );
				$this->save_diff($diff, $elem, $menulevel, $data);
				//if key '.id' exists in elem array and $data array is not empty, write '.id' values to array save. this is needet to know with rows in remote device are ment to be kept (do not remove)
				if (array_key_exists ( '.id', $elem ) && !empty($data)) {
					$save[] = $elem ['.id'];
				}
			}
			// pass .id's to remove function (remove rows that do not match desired settings. ). this enables removing of all rules in specified empty menu level config in xml
			if (! empty ( $collect_ids )) {
				$this->remove(array_diff ( $collect_ids, $save ), $menulevel);
			}
		}
    }

    protected function save_diff($diff, $elem, $menulevel, array $data) {
		// if there is no difference do not do anything = configuration on remote device is the same as in config file
    	if (!$diff) {
    		return;
    	}
    	//if there is no setting in rule eg it does not exist add it. else, set everything in row from diff
		if (empty ( $elem )) {
			$this->api->write ( '/' . $menulevel . '/add', false );
			//add settings from data
			$this->api->write_array ( $data );
			$this->api->read ();
		} else {
			$this->api->write ( '/' . $menulevel . '/set', false );
			//if there is an .id key in elem array write it so taht program knows witch one to set. this also solves issue with no '.id' sections eg. /system/clock, or /system/ntp/client
			if (array_key_exists ( '.id', $elem )) {
				$this->api->write ( '=.id=' . $elem ['.id'], false );
			}
			$this->api->write_array ( $diff );
			$this->api->read ();
		}
    }

    protected function remove($remove, $menulevel) {
    	if (empty($remove)) {
    		return;
    	}
		$this->api->write ( '/' . $menulevel . '/remove', false );
		$tmp = array_shift ( $remove );
		$command = '=.id=' . $tmp;
		foreach ( $remove as $id => $value ) {
			$command .= ',' . $value;
		}
		$this->api->write ( $command );
		$this->api->read ();
    }
}

class MtcfengineCLIParams {
	private $required = array('u' => '0', 'p' => '0', 'a' => '0');

	public function __construct() {
		$this->params = getopt("p:u:a:d:vqhl:t:c:P:");
	}

	public function getUser() {
		return $this->getOptionValue('u');
	}

	public function getPassword() {
		return $this->getOptionValue('p');
	}

	public function getAddress() {
		return $this->getOptionValue('a');
	}

	public function getConfigFile() {
		return $this->getOptionValue('c', $this->getAddress() . '.conf');
	}

    public function isDebug() {
		return $this->optionExists('v');
	}

    public function isHelp() {
		return $this->optionExists('h');
	}

	public function isQuiet() {
		return $this->optionExists('q');
	}

	public function isError() {
		return true;
	}

	public function getDelay() {
		return $this->getIntOption('d', $default = 2);
	}

	public function getPort() {
		return $this->getIntOption('P', $default = 8728);
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
		if (array_key_exists($key, $this->params) && is_int($this->params[$key])) {
			return $this->params[$key];
		} else {
			return $default;
		}
	}

	private function optionExists($key) {
		return array_key_exists($key, $this->params);
	}

	private function getOptionValue($key, $default = false) {
		return array_key_exists($key, $this->params) ? $this->params[$key] : $default;
	}
}

class monitorHandler {

	function __construct(MtcfengineCLIParams $options) {
		$this->options = $options;
	}
	function show_help() {
?>
You must specify -u -p -a
	-a address. can be fqdn
	-c configuration file for address. defaults to specified address.conf
	-d delay between connection attempts in seconds (defaults to 2)
	-h this help
	-p password
	-P port. defaults to 8728
	-t connection attempt timeout and data read timeout (defaults to 2)
	-u username
	-v show (api debug) information. be verbose what is going on
	-q be quiet. this supresses info messages
<?php
	}

	function show_error($text) {
		if ($this->options->isError())
			echo $text . "\n";
	}

	function show_debug($text) {
		if ($this->options->isDebug())
			echo $text . "\n";
	}

	function show_info($text) {
		if (!$this->options->isQuiet())
			echo $text . "\n";
	}
}

$options = new MtcfengineCLIParams();
$monitor = new monitorHandler($options);

if (!$options->isValid() || $options->isHelp() || $options->emptyParams()) {
	$monitor->show_help();
	exit;
}

if (!file_exists($options->getConfigFile())) {
	$monitor->show_error("Specified file " . $options->getConfigFile() . " does not exist.\n");
	exit;
}

$parser = new Parser($options->getConfigFile());
$api = new routeros_api($options, $monitor);
$api->connect($options->getAddress(), $options->getUser(), $options->getPassword());
if (!$api->connected) {
	$monitor->show_error("Connection to " . $options->getAddress() . " failed.");
	exit;
}
$configurator = new Mtcfengine($api);
$configurator->configure($parser->parseFile());
$api->disconnect();
// known bug. for example users. if on remote device all users specified in config file exists but with different order you can not change it. mcm tries to set first one's name to second one's witch eventually gives message user with same name already exists.
// some menu levels doesn't accept delete. ip services
// some menus have default unremovable but configurable values. /ppp profile. values can be changed (except name?) but not deleted

?>
