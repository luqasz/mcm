# -*- coding: UTF-8 -*-


'''
'type'      Menu type. May be: uniquekey, single, ordered.
'keys'      Optional tuple with key names to treat as uniqie key. May be 1 or more. This field is valid only for 'type' : 'uniquekey'
'modord'    Modification order. Possible values 'add', 'set', 'del'. This also works as possible actions that can be taken for given menu. If eg. 'del' is not specified, delete actions will be skipped.
'''

MENU_PATHS = {
'/interface/ethernet': {
    'keys': ('name',),
    'modord': ('set',),
    'type': 'uniquekey'
    },
'/ip/dhcp-client': {
    'keys': ('interface',),
    'modord': ('set', 'add', 'del'),
    'type': 'uniquekey'
    },
'/ip/dhcp-server/alert': {
    'keys': ('interface',),
    'modord': ('set', 'add', 'del'),
    'type': 'uniquekey'
    },
'/ip/dhcp-server/lease': {
    'keys': ('address',),
    'modord': ('set', 'add', 'del'),
    'type': 'uniquekey'
    },
'/ip/dhcp-server/network': {
    'keys': ('address',),
    'modord': ('set', 'add', 'del'),
    'type': 'uniquekey'
    },
'/ip/firewall/service-port': {
    'keys': ('name',),
    'modord': ('set',),
    'type': 'uniquekey'
    },
'/ip/hotspot/service-port': {
    'keys': ('name',),
    'modord': ('set',),
    'type': 'uniquekey'
    },
'/ip/neighbour/discovery': {
    'keys': ('name',),
    'modord': ('set',),
    'type': 'uniquekey'
    },
'/ip/service': {
    'keys': ('name',),
    'modord': ('set',),
    'type': 'uniquekey'
    },
'/ip/upnp/interfaces': {
    'keys': ('interface',),
    'modord': ('set', 'add', 'del'),
    'type': 'uniquekey'
    },
'/port': {
    'keys': ('name',),
    'modord': ('set',),
    'type': 'uniquekey'
    },
'/ppp/active': {
    'keys': ('name',),
    'modord': ('del',),
    'type': 'uniquekey'
    },
'/ppp/profile': {
    'keys': ('interface',),
    'modord': ('set', 'add', 'del'),
    'type': 'uniquekey'
    },
'/queue/interface': {
    'keys': ('interface',),
    'modord': ('set',),
    'type': 'uniquekey'
    },
'/routing/ospf/interface': {
    'keys': ('interface',),
    'modord': ('set', 'add', 'del'),
    'type': 'uniquekey'
    },
'/routing/ospf/network': {
    'keys': ('network',),
    'modord': ('set', 'add', 'del'),
    'type': 'uniquekey'
    },
'/tool/mac-server': {
    'keys': ('interface',),
    'modord': ('set', 'add', 'del'),
    'type': 'uniquekey'
    },
'/tool/mac-server/mac-winbox': {
    'keys': ('interface',),
    'modord': ('set', 'add', 'del'),
    'type': 'uniquekey'
    },
'/user': {
    'keys': ('name',),
    'modord': ('add', 'set', 'del'),
    'type': 'uniquekey'
    },
'/user/group': {
    'keys': ('name',),
    'modord': ('add', 'set', 'del'),
    'type': 'uniquekey'
    }
}
