import scorebot_game.models
import scorebot_grid.models
import scorebot_core.models

from django import forms
from django.contrib import admin
from scorebot.utils.general import import_all_models
from scorebot.utils.constants import CONST_CORE_ACCESS_KEY_LEVELS


class TokenAdmin(admin.ModelAdmin):
    exclude = ('uuid',)
    readonly_fields = ('uuid',)


class AccessTokenForm(forms.ModelForm):
    class Meta:
        model = scorebot_core.models.AccessToken
        fields = ['token']

    access_sys_cli = forms.BooleanField(required=False, label='SYS.CLI')
    access_sys_flag = forms.BooleanField(required=False, label='SYS.FLAG')
    access_all_read = forms.BooleanField(required=False, label='ALL.READ')
    access_dns_read = forms.BooleanField(required=False, label='DNS.READ')
    access_sys_store = forms.BooleanField(required=False, label='SYS.STORE')
    access_flag_read = forms.BooleanField(required=False, label='Flag.READ')
    access_team_read = forms.BooleanField(required=False, label='Team.READ')
    access_game_read = forms.BooleanField(required=False, label='Game.READ')
    access_host_read = forms.BooleanField(required=False, label='Host.READ')
    access_sys_ticket = forms.BooleanField(required=False, label='SYS.TICKET')
    access_all_update = forms.BooleanField(required=False, label='ALL.UPDATE')
    access_all_create = forms.BooleanField(required=False, label='ALL.CREATE')
    accces_all_delete = forms.BooleanField(required=False, label='ALL.DELETE')
    access_sys_beacon = forms.BooleanField(required=False, label='SYS.BEACON')
    access_score_read = forms.BooleanField(required=False, label='Score.READ')
    access_dns_update = forms.BooleanField(required=False, label='DNS.UPDATE')
    access_dns_create = forms.BooleanField(required=False, label='DNS.CREATE')
    access_dns_delete = forms.BooleanField(required=False, label='DNS.DELETE')
    access_game_update = forms.BooleanField(required=False, label='Game.UPDATE')
    access_game_create = forms.BooleanField(required=False, label='Game.CREATE')
    access_game_delete = forms.BooleanField(required=False, label='Game.DELETE')
    access_player_read = forms.BooleanField(required=False, label='Player.READ')
    access_team_create = forms.BooleanField(required=False, label='Team.CREATE')
    access_flag_update = forms.BooleanField(required=False, label='Flag.UPDATE')
    access_flag_create = forms.BooleanField(required=False, label='Flag.CREATE')
    access_flag_delete = forms.BooleanField(required=False, label='Flag.DELETE')
    access_host_update = forms.BooleanField(required=False, label='Host.UPDATE')
    access_host_create = forms.BooleanField(required=False, label='Host.CREATE')
    access_host_delete = forms.BooleanField(required=False, label='Host.DELETE')
    access_ticket_read = forms.BooleanField(required=False, label='Ticket.READ')
    access_content_read = forms.BooleanField(required=False, label='Content.READ')
    access_monitor_read = forms.BooleanField(required=False, label='Monitor.READ')
    access_options_read = forms.BooleanField(required=False, label='Options.READ')
    access_score_update = forms.BooleanField(required=False, label='Score.UPDATE')
    access_score_create = forms.BooleanField(required=False, label='Score.CREATE')
    access_score_delete = forms.BooleanField(required=False, label='Score.DELETE')
    access_service_read = forms.BooleanField(required=False, label='Service.READ')
    access_ticket_update = forms.BooleanField(required=False, label='Ticket.UPDATE')
    access_ticket_create = forms.BooleanField(required=False, label='Ticket.CREATE')
    access_ticket_delete = forms.BooleanField(required=False, label='Ticket.DELETE')
    access_gameteam_read = forms.BooleanField(required=False, label='GameTeam.READ')
    access_player_create = forms.BooleanField(required=False, label='Player.CREATE')
    access_content_update = forms.BooleanField(required=False, label='Content.UPDATE')
    access_content_create = forms.BooleanField(required=False, label='Content.CREATE')
    access_content_delete = forms.BooleanField(required=False, label='Content.DELETE')
    access_monitor_update = forms.BooleanField(required=False, label='Monitor.UPDATE')
    access_monitor_create = forms.BooleanField(required=False, label='Monitor.CREATE')
    access_monitor_delete = forms.BooleanField(required=False, label='Monitor.DELETE')
    access_options_update = forms.BooleanField(required=False, label='Options.UPDATE')
    access_options_create = forms.BooleanField(required=False, label='Options.CREATE')
    access_options_delete = forms.BooleanField(required=False, label='Options.DELETE')
    access_service_update = forms.BooleanField(required=False, label='Service.UPDATE')
    access_service_create = forms.BooleanField(required=False, label='Service.CREATE')
    access_service_delete = forms.BooleanField(required=False, label='Service.DELETE')
    access_compromise_read = forms.BooleanField(required=False, label='Compromise.READ')
    access_gameteam_update = forms.BooleanField(required=False, label='GameTeam.UPDATE')
    access_gameteam_create = forms.BooleanField(required=False, label='GameTeam.CREATE')
    access_gameteam_delete = forms.BooleanField(required=False, label='GameTeam.DELETE')
    access_gamemonitor_read = forms.BooleanField(required=False, label='GameMonitor.READ')
    access_gamemonitor_update = forms.BooleanField(required=False, label='GameMonitor.UPDATE')
    access_gamemonitor_create = forms.BooleanField(required=False, label='GameMonitor.CREATE')
    access_gamemonitor_delete = forms.BooleanField(required=False, label='GameMonitor.DELETE')

    def __init__(self, *args, **kwargs):
        access_instance = kwargs.get('instance', None)
        if access_instance:
            access_keys = dict()
            for key_name in CONST_CORE_ACCESS_KEY_LEVELS.keys():
                if '_' in key_name:
                    key_model = key_name.replace('__', '').split('_')
                else:
                    key_model = key_name.split('.')
                access_keys['access_%s_%s' % (key_model[0].lower(), key_model[1].lower())] = access_instance[key_name]
            kwargs.update(initial=access_keys)
        super(AccessTokenForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        if not self.is_valid():
            return super(AccessTokenForm, self).save(commit)
        access_data = self.clean()
        access_instance = super(AccessTokenForm, self).save(commit)
        for key_name in CONST_CORE_ACCESS_KEY_LEVELS.keys():
            if '_' in key_name:
                key_model = key_name.replace('__', '').split('_')
            else:
                key_model = key_name.split('.')
            access_instance[key_name] = access_data.get('access_%s_%s' % (key_model[0].lower(), key_model[1].lower()))
        access_instance.save()
        return access_instance


class AccessTokenAdmin(admin.ModelAdmin):
    form = AccessTokenForm


import_all_models(scorebot_core.models)
import_all_models(scorebot_grid.models)
import_all_models(scorebot_game.models)
