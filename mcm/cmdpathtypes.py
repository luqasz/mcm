# -*- coding: UTF-8 -*-


'''
'type'      Menu type. May be: uniquekey, single, ordered.
'keys'      Optional tuple with key names to treat as uniqie key. May be 1 or more. This field is valid only for 'type' : 'uniquekey'
'modord'    Modification order. Possible values 'ADD', 'SET', 'DEL'. This also works as possible actions that can be taken for given menu. If eg. 'DEL' is not specified, delete actions will be skipped.
'''

MENU_PATHS = {
'/interface/ethernet': {
    'keys': ('name',),
    'modord': ('SET',),
    'type': 'uniquekey'
    },
'/ip/address': {
    'keys': ('address',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/ip/dhcp-client': {
    'keys': ('interface',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/ip/dhcp-server': {
    'keys': ('name',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/ip/dhcp-server/alert': {
    'keys': ('interface',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/ip/dhcp-server/lease': {
    'keys': ('address',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/ip/dhcp-server/network': {
    'keys': ('address',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/ip/firewall/service-port': {
    'keys': ('name',),
    'modord': ('SET',),
    'type': 'uniquekey'
    },
'/ip/hotspot/service-port': {
    'keys': ('name',),
    'modord': ('SET',),
    'type': 'uniquekey'
    },
'/ip/neighbour/discovery': {
    'keys': ('name',),
    'modord': ('SET',),
    'type': 'uniquekey'
    },
'/ip/service': {
    'keys': ('name',),
    'modord': ('SET',),
    'type': 'uniquekey'
    },
'/ip/upnp/interfaces': {
    'keys': ('interface',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/port': {
    'keys': ('name',),
    'modord': ('SET',),
    'type': 'uniquekey'
    },
'/ppp/active': {
    'keys': ('name',),
    'modord': ('DEL',),
    'type': 'uniquekey'
    },
'/ppp/profile': {
    'keys': ('interface',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/system/ntp/client': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/queue/simple': {
    'keys': ('name',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/queue/interface': {
    'keys': ('interface',),
    'modord': ('SET',),
    'type': 'uniquekey'
    },
'/routing/ospf/interface': {
    'keys': ('interface',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/routing/ospf/network': {
    'keys': ('network',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/tool/mac-server': {
    'keys': ('interface',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/tool/mac-server/mac-winbox': {
    'keys': ('interface',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/user': {
    'keys': ('name',),
    'modord': ('ADD', 'SET', 'DEL'),
    'type': 'uniquekey'
    },
'/user/group': {
    'keys': ('name',),
    'modord': ('ADD', 'SET', 'DEL'),
    'type': 'uniquekey'
    }
}
