# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

import ipaddr
import os
import subprocess

INTERNAL_IFACE_NF = '/tmp/.failover_internal_iface_not_found'


def failover_hardware():
    from freenasUI.failover.detect import ha_hardware
    return ha_hardware()


def failover_internal_interfaces():
    # XXX: Use in migrations:
    # failover/migrations/0014
    # XXX: DO NOT REMOVE/CHANGE
    hardware = failover_hardware()
    if hardware == 'ECHOSTREAM':
        proc = subprocess.Popen('/usr/sbin/pciconf -lv | grep "card=0xa01f8086 chip=0x10d38086"', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output = proc.communicate()[0]
        if not output:
            if not os.path.exists(INTERNAL_IFACE_NF):
                open(INTERNAL_IFACE_NF, 'w').close()
            return []
        return [output.split('@')[0]]
    elif hardware == 'SBB':
        return ['ix0']
    elif hardware == 'ULTIMATE':
        return ['igb1']
    return []


class Migration(DataMigration):

    depends_on = (
        ('network', '0017_auto__add_field_globalconfiguration_gc_hostname_b'),
    )

    def forwards(self, orm):
        for carp in orm['failover.CARP'].objects.all():

            carp_iface = orm['network.Interfaces'].objects.filter(
                int_interface='carp%d' % carp.carp_number
            )

            if not carp_iface.exists():
                # Could not migrate this entry
                continue
            carp_iface = carp_iface[0]

            if carp.carp_number in (1, 2):
                carp_iface.delete()
                continue

            if not carp_iface.int_ipv4address:
                # No IP configured for CARP
                continue

            carp_ipnet = ipaddr.IPNetwork('%s/32' % carp_iface.int_ipv4address)
            internal_ifaces = failover_internal_interfaces()

            found = False
            for iface in orm['network.Interfaces'].objects.exclude(
                int_interface__startswith='carp',
            ):

                if iface.int_interface in internal_ifaces:
                    iface.delete()
                    continue

                if not iface.int_ipv4address or not iface.int_v4netmaskbit:
                    continue

                iface.int_ipv6address
                ipnet = ipaddr.IPNetwork('%s/%s' % (
                    iface.int_ipv4address,
                    iface.int_v4netmaskbit,
                ))

                # If CARP address is within interface range attach CARP into it
                if ipnet.overlaps(carp_ipnet):
                    found = iface
                    break

            if found is False:
                qs = orm['network.Interfaces'].objects.exclude(int_interface__startswith='carp').filter(int_dhcp=True)
                if qs.exists():
                    found = qs[0]

            if found is not False:
                iface = found
                iface.int_vip = carp_iface.int_ipv4address
                if carp.carp_number is not None:
                    iface.int_carp = carp.carp_number
                if carp.carp_vhid:
                    iface.int_vhid = carp.carp_vhid
                if carp.carp_pass:
                    iface.int_pass = carp.carp_pass
                if carp.carp_critical:
                    iface.int_critical = carp.carp_critical
                if carp.carp_group:
                    iface.int_group = carp.carp_group
                iface.save()
                carp_iface.delete()

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        'failover.carp': {
            'Meta': {'object_name': 'CARP', 'db_table': "'network_carp'"},
            'carp_critical': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'carp_group': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'carp_number': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True'}),
            'carp_pass': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'carp_skew': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'carp_vhid': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'failover.failover': {
            'Meta': {'object_name': 'Failover', 'db_table': "'system_failover'"},
            'disabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'master': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'timeout': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'network.alias': {
            'Meta': {'object_name': 'Alias'},
            'alias_interface': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['network.Interfaces']"}),
            'alias_v4address': ('freenasUI.contrib.IPAddressField.IP4AddressField', [], {'default': "''", 'blank': 'True'}),
            'alias_v4netmaskbit': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '3', 'blank': 'True'}),
            'alias_v6address': ('freenasUI.contrib.IPAddressField.IP6AddressField', [], {'default': "''", 'blank': 'True'}),
            'alias_v6netmaskbit': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '3', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'network.globalconfiguration': {
            'Meta': {'object_name': 'GlobalConfiguration'},
            'gc_domain': ('django.db.models.fields.CharField', [], {'default': "'local'", 'max_length': '120'}),
            'gc_hostname': ('django.db.models.fields.CharField', [], {'default': "'nas'", 'max_length': '120'}),
            'gc_hostname_b': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'gc_hosts': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'gc_httpproxy': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'gc_ipv4gateway': ('freenasUI.contrib.IPAddressField.IP4AddressField', [], {'default': "''", 'blank': 'True'}),
            'gc_ipv6gateway': ('freenasUI.contrib.IPAddressField.IP6AddressField', [], {'default': "''", 'blank': 'True'}),
            'gc_nameserver1': ('freenasUI.contrib.IPAddressField.IPAddressField', [], {'default': "''", 'blank': 'True'}),
            'gc_nameserver2': ('freenasUI.contrib.IPAddressField.IPAddressField', [], {'default': "''", 'blank': 'True'}),
            'gc_nameserver3': ('freenasUI.contrib.IPAddressField.IPAddressField', [], {'default': "''", 'blank': 'True'}),
            'gc_netwait_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'gc_netwait_ip': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'network.interfaces': {
            'Meta': {'ordering': "['int_interface']", 'object_name': 'Interfaces'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'int_carp': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'int_critical': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'int_dhcp': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'int_group': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'int_interface': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'int_ipv4address': ('freenasUI.contrib.IPAddressField.IPAddressField', [], {'default': "''", 'blank': 'True'}),
            'int_ipv4address_b': ('freenasUI.contrib.IPAddressField.IPAddressField', [], {'default': "''", 'blank': 'True'}),
            'int_ipv6address': ('freenasUI.contrib.IPAddressField.IPAddressField', [], {'default': "''", 'blank': 'True'}),
            'int_ipv6auto': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'int_name': ('django.db.models.fields.CharField', [], {'max_length': "'120'"}),
            'int_options': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'int_pass': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'int_v4netmaskbit': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '3', 'blank': 'True'}),
            'int_v6netmaskbit': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '4', 'blank': 'True'}),
            'int_vhid': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'int_vip': ('freenasUI.contrib.IPAddressField.IPAddressField', [], {'null': 'True', 'blank': 'True'})
        },
        'network.lagginterface': {
            'Meta': {'ordering': "['lagg_interface']", 'object_name': 'LAGGInterface'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lagg_interface': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['network.Interfaces']", 'unique': 'True'}),
            'lagg_protocol': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        },
        'network.lagginterfacemembers': {
            'Meta': {'ordering': "['lagg_interfacegroup']", 'object_name': 'LAGGInterfaceMembers'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lagg_deviceoptions': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'lagg_interfacegroup': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['network.LAGGInterface']"}),
            'lagg_ordernum': ('django.db.models.fields.IntegerField', [], {}),
            'lagg_physnic': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '120'})
        },
        'network.staticroute': {
            'Meta': {'ordering': "['sr_destination', 'sr_gateway']", 'object_name': 'StaticRoute'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sr_description': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'sr_destination': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'sr_gateway': ('freenasUI.contrib.IPAddressField.IP4AddressField', [], {'max_length': '120'})
        },
        'network.vlan': {
            'Meta': {'ordering': "['vlan_vint']", 'object_name': 'VLAN'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vlan_description': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'vlan_pint': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'vlan_tag': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'vlan_vint': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        }
    }

    complete_apps = ['network', 'failover']
    symmetrical = True
