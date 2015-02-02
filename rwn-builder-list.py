#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# 
# Create foreman-host-builder csv file querying docet rwn
#
# Copyright (C) 2014 INFN T1 Farming - farming@lists.cnaf.infn.it
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import xmlrpclib, csv, sys
from socket import gethostbyname
from optparse import OptionParser

desc="""rwn-builder-list.py can help you creating the file requested by
foreman-rwn-builder.py.
The template format is a csv like file as follows: 
HOSTNAME;DOMAIN;SUBNET;ENVIRONMENT;ARCHITECTURE;HOSTGROUP;OPERATING_SYSTEM;MAC;IP;PTABLE;MEDIA;PUPPET_CA_PROXY;PUPPET_PROXY
"""

parser = OptionParser(description=desc)
parser.add_option('--rack', 
                  help = 'Provide the rack number in your domain (format zone-rack [ddd-dd]: 201-01)', 
                  dest = 'rack'
					       )
parser.add_option('--file', 
                  help = 'Output file with csv entries (file name suggested: Rack-201-01)',
                  dest = 'file'
                  )

(opts, args) = parser.parse_args()

mandatories = ['rack','file']

for m in mandatories:
  if not opts.__dict__[m]:
    print "A mandatory option is missing\n"
    parser.print_help()
    sys.exit(-1)	
  
docet_endpoint = 'http://docet.cr.cnaf.infn.it:8000'

# Create XML-RPC server proxy
s = xmlrpclib.ServerProxy(docet_endpoint)
# Ask the list of real worker nodes
rwn = s.chiedi('rwn')
        
# Make a list comprehension of both real and hypervisor worker nodes by splitting with the | char
# Get only hostname, ip, mac, switch by slicing [2:6]
#rwns = [i.split('|')[2:6] for i in rwn.split() if i.split('|')[2:6]] # Is it possible to simplify the double split?
rwns = [i.split('|')[2:6] for i in rwn.split() if i.split('|')[2].split('-')[0] == 'wn']
hvns = [i.split('|')[2:6] for i in rwn.split() if i.split('|')[2].split('-')[0] == 'hv']
            
# Slice the list on a rack dictionary
# WN hostnames contain rack numbers 
# (es. for wn-201-01-31-04-a rack num is Rack-201-01, for hv-205-06-01-01-b is HV-205-06)
rwnsd = {}
for nl,line in enumerate(rwns):
    if rwns[nl][-1:][0] != 'None':
    	rwnsd.setdefault('Rack-'+rwns[nl][0][3:9],[]).append(line)

hvnsd = {}
for nl,line in enumerate(hvns):
	if hvns[nl][-1:][0] != 'None':
		hvnsd.setdefault('HV-group',[]).append(line)

domain = 'cr.cnaf.infn.it'
hostgroup = 'Rack-'+opts.rack
subnet = str(9)
environment = 'farming'
os = 'Scientific-Farming-Snap'
partition_table = 'Farming-part-WN'
installation_media = 'SL6 T1 OS server'
puppet_ca = 'Puppet'
puppet_master = 'Puppet Dev'

file = open(opts.file, 'w')
for key in rwnsd:
    if key == hostgroup:
        for i in rwnsd[key]:
            file.write(i[0]+';'+domain+';'+subnet+';'+environment+';'+hostgroup+';'+os+';'+i[2]+';'+i[1]+';'+partition_table+';'+installation_media+';'+puppet_ca+';'+puppet_master+'\n')
file.close()


    