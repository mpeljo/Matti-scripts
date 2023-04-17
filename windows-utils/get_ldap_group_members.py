
import sys
from ldap3 import Server, Connection, ALL, NTLM, ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES, AUTO_BIND_NO_TLS, SUBTREE
from ldap3.core.exceptions import LDAPCursorError

server_name = 'win-dc1.prod.lan'
domain_name = 'prod'
user_name = 'u25834'
password = '8*Conductivity'

format_string = '{:25} {:>6} {:19} {:19} {}'
print(format_string.format('User', 'Logins', 'Last Login', 'Expires', 'Description'))

server = Server(server_name, get_info=ALL)
# Connection works (but maybe shouldn't) when auto_bind=True
conn = Connection(server, user='{}\\{}'.format(domain_name, user_name), password=password, authentication=NTLM, auto_bind=AUTO_BIND_NO_TLS)
conn.search('dc={},dc=lan'.format(domain_name), '(objectclass=person)', attributes=[ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES])
print(len(conn.entries))
for e in conn.entries:
    try:
        desc = e.description
    except LDAPCursorError:
        desc = ""
    #except LDAPCursorError:
    #    desc = ""
    name = str(e.name).split("-")
    matchers = ['LT', 'PC', 'SL', 'ml', 'md', 'HCP02']
    if not name[0] in matchers:
        print(format_string.format(str(e.name), 'xxxxxx', 'xxxxxx'[:19], 'xxxxxx'[:19], desc))
