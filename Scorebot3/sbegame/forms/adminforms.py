from django import forms
from sbegame.models import AccessKey


class AccessKeyAdminPanel(forms.ModelForm):
    class Meta:
        model = AccessKey
        fields = ['key_uuid']

    key_perm_read_all = forms.BooleanField(required=False, label='ALL_READ')
    key_perm_read_game = forms.BooleanField(required=False, label='Game.READ')
    key_perm_read_team = forms.BooleanField(required=False, label='Team.READ')
    key_perm_update_all = forms.BooleanField(required=False, label='ALL_UPDATE')
    key_perm_create_all = forms.BooleanField(required=False, label='ALL_CREATE')
    key_perm_delete_all = forms.BooleanField(required=False, label='ALL_DELETE')
    key_perm_read_player = forms.BooleanField(required=False, label='Player.READ')
    key_perm_update_team = forms.BooleanField(required=False, label='Team.UPDATE')
    key_perm_create_team = forms.BooleanField(required=False, label='Team.CREATE')
    key_perm_delete_team = forms.BooleanField(required=False, label='Team.DELETE')
    key_perm_update_game = forms.BooleanField(required=False, label='Game.UPDATE')
    key_perm_create_game = forms.BooleanField(required=False, label='Game.CREATE')
    key_perm_delete_game = forms.BooleanField(required=False, label='Game.DELETE')
    key_perm_read_gamedns = forms.BooleanField(required=False, label='GameDNS.READ')
    key_perm_read_gamehost = forms.BooleanField(required=False, label='GameHost.READ')
    key_perm_read_gameteam = forms.BooleanField(required=False, label='GameTeam.READ')
    key_perm_read_gameflag = forms.BooleanField(required=False, label='GameFlag.READ')
    key_perm_update_player = forms.BooleanField(required=False, label='Player.UPDATE')
    key_perm_create_player = forms.BooleanField(required=False, label='Player.CREATE')
    key_perm_delete_player = forms.BooleanField(required=False, label='Player.DELETE')
    key_perm_update_gamedns = forms.BooleanField(required=False, label='GameDNS.UPDATE')
    key_perm_create_gamedns = forms.BooleanField(required=False, label='GameDNS.CREATE')
    key_perm_delete_gamedns = forms.BooleanField(required=False, label='GameDNS.DELETE')
    key_perm_update_gamehost = forms.BooleanField(required=False, label='GameHost.UPDATE')
    key_perm_create_gamehost = forms.BooleanField(required=False, label='GameHost.CREATE')
    key_perm_delete_gamehost = forms.BooleanField(required=False, label='GameHost.DELETE')
    key_perm_read_gameticket = forms.BooleanField(required=False, label='GameTicket.READ')
    key_perm_read_gameplayer = forms.BooleanField(required=False, label='GamePlayer.READ')
    key_perm_update_gameteam = forms.BooleanField(required=False, label='GameTeam.UPDATE')
    key_perm_create_gameteam = forms.BooleanField(required=False, label='GameTeam.CREATE')
    key_perm_delete_gameteam = forms.BooleanField(required=False, label='GameTeam.DELETE')
    key_perm_update_gameflag = forms.BooleanField(required=False, label='GameFlag.UPDATE')
    key_perm_create_gameflag = forms.BooleanField(required=False, label='GameFlag.CREATE')
    key_perm_delete_gameflag = forms.BooleanField(required=False, label='GameFlag.DELETE')
    key_perm_read_gameservice = forms.BooleanField(required=False, label='GameService.READ')
    key_perm_read_gamecontent = forms.BooleanField(required=False, label='GameContent.READ')
    key_perm_update_gameticket = forms.BooleanField(required=False, label='GameTicket.UPDATE')
    key_perm_create_gameticket = forms.BooleanField(required=False, label='GameTicket.CREATE')
    key_perm_delete_gameticket = forms.BooleanField(required=False, label='GameTicket.DELETE')
    key_perm_update_gameplayer = forms.BooleanField(required=False, label='GamePlayer.UPDATE')
    key_perm_create_gameplayer = forms.BooleanField(required=False, label='GamePlayer.CREATE')
    key_perm_delete_gameplayer = forms.BooleanField(required=False, label='GamePlayer.DELETE')
    key_perm_update_gamecontent = forms.BooleanField(required=False, label='GameContent.UPDATE')
    key_perm_create_gamecontent = forms.BooleanField(required=False, label='GameContent.CREATE')
    key_perm_delete_gamecontent = forms.BooleanField(required=False, label='GameContent.DELETE')
    key_perm_update_gameservice = forms.BooleanField(required=False, label='GameService.UPDATE')
    key_perm_create_gameservice = forms.BooleanField(required=False, label='GameService.CREATE')
    key_perm_delete_gameservice = forms.BooleanField(required=False, label='GameService.DELETE')
    key_perm_read_gamecompromise = forms.BooleanField(required=False, label='GameCompromise.READ')
    key_perm_update_gamecompromise = forms.BooleanField(required=False, label='GameCompromise.UPDATE')
    key_perm_create_gamecompromise = forms.BooleanField(required=False, label='GameCompromise.CREATE')
    key_perm_delete_gamecompromise = forms.BooleanField(required=False, label='GameCompromise.DELETE')

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance:
            intkeys = dict()
            for k in AccessKey.KEY_LEVELS.keys():
                v = k.split('.') if '.' in k else k.split('_')
                intkeys['key_perm_%s_%s' % (v[1].lower(), v[0].lower())] = instance[k]
            kwargs.update(initial=intkeys)
        super(AccessKeyAdminPanel, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        if not self.is_valid():
            return super(AccessKeyAdminPanel, self).save(commit)
        datav = self.clean()
        updated = super(AccessKeyAdminPanel, self).save(commit)
        for k in AccessKey.KEY_LEVELS.keys():
            v = k.split('.') if '.' in k else k.split('_')
            updated[k] = datav.get('key_perm_%s_%s' % (v[1].lower(), v[0].lower()))
        updated.save()
        return updated