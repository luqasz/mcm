# -*- coding: UTF-8 -*-


'''
'type'      Menu type. May be: uniquekey, single, ordered.
'keys'      Tuple with key names to treat as uniqie key. May be 1 or more. If more then one, it is treated as a compound key. This field is important only for 'type' : 'uniquekey'
'modord'    Modification order. Possible values 'ADD', 'SET', 'DEL'. This also works as possible actions that can be taken for given menu. If eg. 'DEL' is not specified, delete actions will be skipped.
'''

MENU_PATHS = {
'/interface/ethernet': {
    'keys': ('name',),
    'modord': ('SET',),
    'type': 'uniquekey'
    },
'/interface/bridge/settings': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/interface/l2tp-server/server': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/interface/ovpn-server/server': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/interface/pptp-server/server': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/interface/sstp-server/server': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/interface/wireless/align': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/interface/wireless/cap': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/interface/wireless/security-profiles': {
    'keys': ('name',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/interface/wireless/sniffer': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/interface/wireless/snooper': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/ip/accounting': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/ip/accounting/web-access': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/ip/dhcp-client/option': {
    'keys': ('name',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/ip/dhcp-server/config': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/ip/dns': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/ip/firewall/address-list': {
    'keys': ('list','address'),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/ip/firewall/connection/tracking': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/ip/hotspot/profile': {
    'keys': ('name',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/ip/hotspot/user/profile': {
    'keys': ('name',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/ip/ipsec/mode-config': {
    'keys': ('name',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/ip/ipsec/policy': {
    'keys': ('name',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/ip/ipsec/policy/group': {
    'keys': ('name',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/ip/ipsec/proposal': {
    'keys': ('name',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/ip/neighbor/discovery': {
    'keys': ('name',),
    'modord': ('SET',),
    'type': 'uniquekey'
    },
'/ip/neighbor/discovery/settings': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/ip/proxy': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/ip/settings': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/ip/smb': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/ip/smb/shares': {
    'keys': ('name',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/ip/smb/users': {
    'keys': ('name',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/ip/socks': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/ip/traffic-flow': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/ip/upnp': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/ip/upnp/interfaces': {
    'keys': ('interface',),
    'modord': ('SET', 'ADD', 'DEL'),
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
'/ip/service': {
    'keys': ('name',),
    'modord': ('SET',),
    'type': 'uniquekey'
    },
'/ipv6/nd': {
    'keys': ('interface',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/ipv6/nd/prefix': {
    'keys': ('interface',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/ipv6/nd/prefix/default': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/ipv6/address': {
    'keys': ('interface',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/ipv6/settings': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/port': {
    'keys': ('name',),
    'modord': ('SET',),
    'type': 'uniquekey'
    },
'/ppp/aaa': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/ppp/secret': {
    'keys': ('name',),
    'modord': ('SET', 'ADD', 'DEL'),
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
'/queue/type': {
    'keys': ('name',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
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
'/routing/bfd/interface': {
    'keys': ('interface',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/routing/bgp/instance': {
    'keys': ('name',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/routing/igmp-proxy': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/routing/mme': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/routing/pim': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/routing/rip': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/routing/ripng': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/routing/ospf-v3/area': {
    'keys': ('name',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/routing/ospf-v3/interface': {
    'keys': ('interface',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/routing/ospf-v3/instance': {
    'keys': ('name',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/routing/ospf/area': {
    'keys': ('name',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/routing/ospf/instance': {
    'keys': ('name',),
    'modord': ('SET', 'ADD', 'DEL'),
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
'/user': {
    'keys': ('name',),
    'modord': ('ADD', 'SET', 'DEL'),
    'type': 'uniquekey'
    },
'/user/group': {
    'keys': ('name',),
    'modord': ('ADD', 'SET', 'DEL'),
    'type': 'uniquekey'
    },
'/mpls': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/mpls/interface': {
    'keys': ('interface',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/mpls/ldp': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/caps-man/aaa': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/caps-man/channel': {
    'keys': ('name',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/caps-man/manager': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/port/remote-access': {
    'keys': (),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'ordered'
    },
'/port/firmware': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/radius': {
    'keys': (),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'ordered'
    },
'/radius/incoming': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/snmp': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/snmp/community': {
    'keys': ('name',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/system/ntp/server': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/system/ntp/client': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/system/clock': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/system/clock/manual': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/system/console/screen': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/system/gps': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/system/hardware': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/system/health': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/system/identity': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/system/lcd': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/system/lcd/page': {
    'keys': (),
    'modord': ('SET',),
    'type': 'ordered'
    },
'/system/logging': {
    'keys': (),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'ordered'
    },
'/system/logging/action': {
    'keys': ('name',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/system/note': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/system/package/update': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/system/upgrade/mirror': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/system/watchdog': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/tool/bandwidth-server': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/tool/e-mail': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/tool/graphing': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/tool/graphing/interface': {
    'keys': (),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'ordered'
    },
'/tool/graphing/queue': {
    'keys': (),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'ordered'
    },
'/tool/graphing/resource': {
    'keys': (),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'ordered'
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
'/tool/mac-server/ping': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/tool/romon': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/tool/romon/port': {
    'keys': ('interface',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/tool/sms': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/tool/sniffer': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/tool/traffic-generator': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/tool/user-manager/customer': {
    'keys': ('login',),
    'modord': ('SET', 'ADD', 'DEL'),
    'type': 'uniquekey'
    },
'/tool/user-manager/database': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    },
'/user/aaa': {
    'keys': (),
    'modord': ('SET',),
    'type': 'single'
    }
}
