# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.db.models import Q

class Migration(DataMigration):

    def forwards(self, orm):
        url = "http://download.freenas.org/jails/9.3/"

        for jt in orm.JailTemplate.objects.filter(
            Q(jt_name__startswith='pluginjail') |
            Q(jt_name__startswith='portjail') |
            Q(jt_name__startswith='standard')):
            jt.delete()

        for jt in orm.JailTemplate.objects.all():
            jt.jt_system = False
            jt.save()

        for arch in ('x86', 'x64'):
            for name in ('standard', 'pluginjail'):
                if arch == 'x86':
                    name = '%s-x86' % name

                jt = orm.JailTemplate() 
                jt.jt_name = name
                jt.jt_os = 'FreeBSD'
                jt.jt_arch = arch
                jt.jt_url = '%s/%s/freenas-%s-9.3-RELEASE.tgz' % (
                    url, arch, name
                )
                jt.jt_system = True

                jt.save()

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        u'jails.jailmountpoint': {
            'Meta': {'object_name': 'JailMountPoint'},
            'destination': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jail': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'readonly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        u'jails.jails': {
            'Meta': {'object_name': 'Jails'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jail_alias_bridge_ipv4': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'jail_alias_bridge_ipv6': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'jail_alias_ipv4': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'jail_alias_ipv6': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'jail_autostart': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'max_length': '120'}),
            'jail_bridge_ipv4': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'jail_bridge_ipv4_netmask': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '3', 'blank': 'True'}),
            'jail_bridge_ipv6': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'jail_bridge_ipv6_prefix': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '4', 'blank': 'True'}),
            'jail_defaultrouter_ipv4': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'jail_defaultrouter_ipv6': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'jail_flags': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'jail_host': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'jail_iface': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300', 'blank': 'True'}),
            'jail_ipv4': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'jail_ipv4_netmask': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '3', 'blank': 'True'}),
            'jail_ipv6': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'jail_ipv6_prefix': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '4', 'blank': 'True'}),
            'jail_mac': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'jail_nat': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'jail_status': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'jail_type': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'jail_vnet': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'max_length': '120'})
        },
        u'jails.jailsconfiguration': {
            'Meta': {'object_name': 'JailsConfiguration'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jc_collectionurl': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'jc_ipv4_network': ('freenasUI.freeadmin.models.fields.Network4Field', [], {'max_length': '18', 'blank': 'True'}),
            'jc_ipv4_network_end': ('freenasUI.freeadmin.models.fields.Network4Field', [], {'max_length': '18', 'blank': 'True'}),
            'jc_ipv4_network_start': ('freenasUI.freeadmin.models.fields.Network4Field', [], {'max_length': '18', 'blank': 'True'}),
            'jc_ipv6_network': ('freenasUI.freeadmin.models.fields.Network6Field', [], {'max_length': '43', 'blank': 'True'}),
            'jc_ipv6_network_end': ('freenasUI.freeadmin.models.fields.Network6Field', [], {'max_length': '43', 'blank': 'True'}),
            'jc_ipv6_network_start': ('freenasUI.freeadmin.models.fields.Network6Field', [], {'max_length': '43', 'blank': 'True'}),
            'jc_path': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        u'jails.jailtemplate': {
            'Meta': {'object_name': 'JailTemplate'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jt_arch': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'jt_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '120'}),
            'jt_os': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'jt_system': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'jt_url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['jails']
    symmetrical = True
