# encoding: utf-8
import json
import os
import platform
from south.v2 import DataMigration

IS_LINUX = platform.system().lower() == 'linux'


class Migration(DataMigration):

    def forwards(self, orm):

        jf = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "fixtures", "bsdGroups.json")
        with open(jf) as json_fd:
            data = json_fd.read()
        groups = json.loads(data)
        for entry in groups:
            group = orm.bsdGroups(pk=entry['pk'])
            for field in entry['fields']:
                mfield = orm.bsdGroups._meta.get_field(field)
                setattr(group, field, entry['fields'].get(field))
            group.save()

        jf = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "fixtures", "bsdUsers.json")
        with open(jf) as json_fd:
            data = json_fd.read()
        users = json.loads(data)
        for entry in users:
            user = orm.bsdUsers(pk=entry['pk'])
            # bsdUsers.json sets the default shell for root account to
            # /usr/local/bin/zsh which doesn't exist on SCALE so make
            # sure we set it appropriately
            if entry['fields']['bsdusr_uid'] == 0 and IS_LINUX:
                entry['fields']['bsdusr_shell'] = '/usr/bin/zsh'

            for field in entry['fields']:
                mfield = orm.bsdUsers._meta.get_field(field)
                if mfield.rel != None:
                    inst = mfield.rel.to.objects.get(pk=entry['fields'].get(field))
                    setattr(user, field, inst)
                else:
                    setattr(user, field, entry['fields'].get(field))
            user.save()

    def backwards(self, orm):
        "Write your backwards methods here."


    models = {
        'account.bsdgroupmembership': {
            'Meta': {'object_name': 'bsdGroupMembership'},
            'bsdgrpmember_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.bsdGroups']"}),
            'bsdgrpmember_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.bsdUsers']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'account.bsdgroups': {
            'Meta': {'object_name': 'bsdGroups'},
            'bsdgrp_builtin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bsdgrp_gid': ('django.db.models.fields.IntegerField', [], {}),
            'bsdgrp_group': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'account.bsdusers': {
            'Meta': {'object_name': 'bsdUsers'},
            'bsdusr_builtin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bsdusr_full_name': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'bsdusr_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.bsdGroups']"}),
            'bsdusr_home': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'bsdusr_shell': ('django.db.models.fields.CharField', [], {'default': "'/bin/csh'", 'max_length': '120'}),
            'bsdusr_smbhash': ('django.db.models.fields.CharField', [], {'default': "'*'", 'max_length': '128', 'blank': 'True'}),
            'bsdusr_uid': ('django.db.models.fields.IntegerField', [], {'unique': "'True'", 'max_length': '10'}),
            'bsdusr_unixhash': ('django.db.models.fields.CharField', [], {'default': "'*'", 'max_length': '128', 'blank': 'True'}),
            'bsdusr_username': ('django.db.models.fields.CharField', [], {'default': "'User &'", 'unique': 'True', 'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['account']
