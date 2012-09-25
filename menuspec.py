#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
 '/' and '-' in menu names are changed to '_'

allowed dictionary attributes in menu level variables:
offset = how many first offset rules to treat as default. (default are not removable)
key = with attribute will be treated as 'key' one.
mng_def = to 'shift' default enries or not
mod_ord = order in witch mcm will ADD DEL or SET
lst_attr = tuple with 1 element as name of attribute to split it into list, second by what char to split it.
ADD = is it possible to add (bool)
SET = is it possible to set (bool)
DEL = is it possible to delete (bool)
"""


class default:
	"""
	default (fallback) menu specifications, regardless of version
	"""

	_interface_ethernet = {'key':'name', 'ADD':False, 'DEL':False}
	_interface_wireless_security_profiles = {'key':'name'}

	_port = {'key':'name', 'ADD':False, 'DEL':False}

	_routing_bgp_instance = {'key':'name'}
	_routing_ospf_instance = {'key':'name'}
	_routing_ospf_area = {'key':'name'}
	_routing_ospf_interface = {'key':'interface'}
	_routing_ospf_network = {'key':'network'}

	_user = {'key':'name', 'mod_ord':('ADD', 'SET', 'DEL')}
	#policy can be split by , to ease comparison
	_user_group = {'key':'name', 'offset':3, 'lst_attr':('policy', ',')}

	_ip_hotspot_profile = {'key':'name'}
	_ip_hotspot_user_profile = {'key':'name'}
	_ip_firewall_service_port = {'key':'name', 'ADD':False, 'DEL':False}
	_ip_hotspot_service_port = {'key':'name', 'ADD':False, 'DEL':False}
	#can only set
	_ip_neighbour_discovery = {'key':'name', 'ADD':False, 'DEL':False}
	#can only set
	_ip_service = {'key':'name', 'ADD':False, 'DEL':False}
	_ip_smb_shares = {'key':'name'}
	_ip_smb_users = {'key':'name'}
	_ip_address = {'key':'address'}
	_ip_dhcp_client = {'key':'interface'}
	_ip_dhcp_relay = {'key':'name'}
	_ip_dhcp_server = {'key':'name'}
	_ip_dhcp_server_alert = {'key':'interface'}
	_ip_dhcp_server_lease = {'key':'address'}
	_ip_dhcp_server_network = {'key':'address'}
	_ip_dhcp_server_option = {'key':'name'}
	_ip_pool = {'key':'name'}
	_ip_upnp_interfaces = {'key':'interface'}
	_ip_ipsec_proposal = {'key':'name'}

	_queue_simple = {'key':'name'}
	#can only set
	_queue_interface = {'key':'interface', 'ADD':False, 'DEL':False}
	_queue_type = {'key':'name'}

	_ppp_profile = {'key':'interface'}
	#only dynamic entres
	_ppp_active = {'key':'name', 'ADD':False, 'SET':False}
	_ppp_secret = {'key':'name'}

	_tool_mac_server_mac_winbox = {'key':'interface'}
	_tool_mac_server = {'key':'interface'}

	_system_script = {'key':'name'}
	_system_scheduler = {'key':'name'}
	#no order. no key. first 4 are default
	#_system_logging = {'offset':4}
	_system_logging_action  = {'key':'name'}

	_snmp_community = {'key':'name', 'mng_def':True}

"""
sample class for different version dependent menu specification
#for all 3.x versions
class version_3_x:
	_snmp_community = {'key':'community'}

vmap = {'3.0':version_3_x, '3.1':version_3_x, ETC...}
"""
