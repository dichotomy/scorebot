
var sb3_message = '';
var sb3_delete_on_missing = true;
var sb3_message_default = 'This is Scorebot v3';

var _sb3_teams = [];
var _sb3_game_mode = 0;
var _sb3_message_div = null;
var _sb3_message_text = null;
var _sb3_game_name_div = null;
var _sb3_message_text_length = null;

function sb3_init()
{
    sb3_update_teams();
    sb3_set_message(null);
    setInterval(sb3_marquee, 25);
    setInterval(sb3_update_teams, 5000);
}
function sb3_marquee()
{
    if(_sb3_message_div === null)
        _sb3_message_div = document.getElementById('sb3_message');
    if(_sb3_message_text === null)
        _sb3_message_text = document.getElementById('sb3_message_text');
    if(_sb3_message_text_length === null)
    {
        var _sb3_message_canvas = document.createElement('canvas');
        var _sb3_message_canvas_context = _sb3_message_canvas.getContext('2d');
        _sb3_message_canvas_context.font = '25px Arial';
        _sb3_message_text_length = _sb3_message_canvas_context.measureText(sb3_message).width;
    }
    _sb3_message_text.innerText = sb3_message;
    var _sb3_message_offset = parseInt(_sb3_message_text.style.left.replace('px', ''));
    var _sb3_message_size = _sb3_message_div.offsetWidth;
    if(_sb3_message_offset >= _sb3_message_size) _sb3_message_offset = -1 * _sb3_message_text_length;
    else _sb3_message_offset += 2;
    _sb3_message_text.style.left = _sb3_message_offset + 'px';
}
function _sb3_team_draw()
{
    var _sb3_team_div = document.getElementById('sb3_team_div_' + this.id);
    if(_sb3_game_mode === 0 && this.offense === true)
    {
        if(_sb3_team_div !== null)
        {
            _sb3_team_div.outerHTML = '';
            delete _sb3_team_div;
        }
        return;
    }
    if(_sb3_team_div === null)
    {
        _sb3_team_div = document.createElement('div');
        _sb3_team_div.id = 'sb3_team_div_' + this.id;
        _sb3_team_div.innerHTML = '<div class="sb3_team_info" id="sb3_team_div_info_' + this.id + '"></div>' +
                '<div class="sb3_team_health"><table><tr><td class="sb3_team_health_left" id="sb3_team_div_left_' + this.id +
                '"></td><td class="sb3_team_health_right"><table id="sb3_team_div_health_' + this.id +
                '" class="sb3_team_health_stats"></table></td></tr></table></div><div class="sb3_team_stats">' +
                '<table><tr><td class="sb3_team_status_health" id="sb3_team_div_status_health_' + this.id +
                '">0</td><td class="sb3_team_status_flags" id="sb3_team_div_status_flags_' + this.id +
                '"></td><td class="sb3_team_status_tickets" id="sb3_team_div_status_tickets_' + this.id +
                '"></td><td class="sb3_team_status_beacons" id="sb3_team_div_status_beacons_' + this.id +
                '"></td></tr></table></div>';
        _sb3_team_div.classList.add('sb3_team');
        var _sb3_board = document.getElementById('sb3_teams');
        if(_sb3_board !== null)
            _sb3_board.appendChild(_sb3_team_div);
    }
    _sb3_team_div.style.border ='2px solid ' + this.color;
    var _sb3_team_div_pointer = document.getElementById('sb3_team_div_info_' + this.id);
    if(_sb3_team_div_pointer !== null)
    {
        _sb3_team_div_pointer.innerHTML = this.name + ' : ' + this.score.total;
        if(this.offense === true)
        {
            _sb3_team_div_pointer.innerHTML += '<div class="sb3_team_info_off"></div>';
            _sb3_team_div.classList.add('sb3_team_off');
        }
        else _sb3_team_div.classList.remove('sb3_team_off');
    }
    _sb3_team_div_pointer = document.getElementById('sb3_team_div_left_' + this.id);
    if(_sb3_team_div_pointer !== null)
    {
        _sb3_team_div_pointer.style.background = this.color;
        _sb3_team_div_pointer.innerHTML = '<div class="sb3_team_logo" style="background: url(\'' +
            window.location.origin + '/static/img/team/' + this.logo + '\'); no-repeat;"></div>';
    }
    var _sb3_max_services = 0;
    var _sb3_host_index;
    for(_sb3_host_index = 0; _sb3_host_index < this.hosts.length; _sb3_host_index++)
        if(this.hosts[_sb3_host_index].services.length > _sb3_max_services)
            _sb3_max_services = this.hosts[_sb3_host_index].services.length;
    for(_sb3_host_index = 0; _sb3_host_index < this.hosts.length; _sb3_host_index++)
    {
        _sb3_team_div_pointer = document.getElementById('sb3_team_div_health_' + this.id + '_' + this.hosts[_sb3_host_index].id);
        if(_sb3_team_div_pointer === null && !this.hosts[_sb3_host_index].delete)
        {
            var _sb3_team_health_container = document.getElementById('sb3_team_div_health_' + this.id);
            _sb3_team_div_pointer = document.createElement('tr');
            _sb3_team_div_pointer.id = 'sb3_team_div_health_' + this.id + '_' + this.hosts[_sb3_host_index].id;
            _sb3_team_health_container.appendChild(_sb3_team_div_pointer);
        }
        else if(_sb3_team_div_pointer === null) continue;
        else if(this.hosts[_sb3_host_index].delete)
        {
            _sb3_team_div_pointer.outerHTML = '';
            delete _sb3_team_div_pointer;
            continue;
        }
        var _sb3_host_bonus = [], _sb3_service_index;
        for(_sb3_service_index = 0; _sb3_service_index < this.hosts[_sb3_host_index].services.length; _sb3_service_index++)
            if(this.hosts[_sb3_host_index].services[_sb3_service_index].bonus === true) _sb3_host_bonus.push(this.hosts[_sb3_host_index].services[_sb3_service_index]);
        var _sb3_host_blanks = _sb3_max_services - this.hosts[_sb3_host_index].services.length;
        if(_sb3_host_blanks < 0) _sb3_host_blanks = 0;
        var _sb3_host_health = '<td class="sb3_team_health_status_name';
        if(this.hosts[_sb3_host_index].online === false) _sb3_host_health += ' sb3_team_health_status_offline';
        _sb3_host_health += '">' + this.hosts[_sb3_host_index].name + '</td>';
        for(_sb3_service_index = 0; _sb3_service_index < this.hosts[_sb3_host_index].services.length; _sb3_service_index++)
            if(this.hosts[_sb3_host_index].services[_sb3_service_index].bonus === false)
            {
                _sb3_host_health += '<td class="sb3_team_health_status_' + this.hosts[_sb3_host_index].services[_sb3_service_index].status +
                    '">' + this.hosts[_sb3_host_index].services[_sb3_service_index].port;
                _sb3_host_health += this.hosts[_sb3_host_index].services[_sb3_service_index].protocol.toUpperCase() + '</td>';
            }
        var _sb3_host_empty_count;
        for(_sb3_host_empty_count = 0; _sb3_host_empty_count < _sb3_host_blanks; _sb3_host_empty_count++)
            _sb3_host_health += '<td class="sb3_team_health_status_empty"></td>';
        for(_sb3_service_index = 0; _sb3_service_index < _sb3_host_bonus.length; _sb3_service_index++)
        {
            _sb3_host_health += '<td class="sb3_team_health_status_bonus';
            if(_sb3_host_bonus[_sb3_service_index].status !== "")
                _sb3_host_health += ' sb3_team_health_status_' + _sb3_host_bonus[_sb3_service_index].status;
            _sb3_host_health += '">' + _sb3_host_bonus[_sb3_service_index].port;
            _sb3_host_health += _sb3_host_bonus[_sb3_service_index].protocol.toUpperCase() + '</td>';
        }
        _sb3_team_div_pointer.innerHTML = _sb3_host_health;
    }
    _sb3_team_div_pointer = document.getElementById('sb3_team_div_status_health_' + this.id);
    if(_sb3_team_div_pointer !== null)
        _sb3_team_div_pointer.innerText = this.score.health;
    _sb3_team_div_pointer = document.getElementById('sb3_team_div_status_flags_' + this.id);
    if(_sb3_team_div_pointer !== null)
        _sb3_team_div_pointer.innerHTML = this.flags.open + ' / <span class="sb3_team_status_lost">' + this.flags.lost + '</span>';
    _sb3_team_div_pointer = document.getElementById('sb3_team_div_status_tickets_' + this.id);
    if(_sb3_team_div_pointer !== null)
        _sb3_team_div_pointer.innerHTML = this.tickets.open + ' / <span class="sb3_team_status_lost">' + this.tickets.closed + '</span>';
    _sb3_team_div_pointer = document.getElementById('sb3_team_div_status_beacons_' + this.id);
    if(_sb3_team_div_pointer !== null)
        _sb3_team_div_pointer.innerText = this.beacons;
}
function sb3_update_teams()
{
    var _sb3_get = new XMLHttpRequest();
    _sb3_get.onreadystatechange = function() { sb3_update_json(_sb3_get); };
    _sb3_get.open("GET", sb3_server + '/api/scoreboard/' + sb3_game + '/', true);
    _sb3_get.send(sb3_update_json);
}
function sb3_add_team(team_dict)
{
    if(team_dict === null) return;
    var _sb3_team_id = parseInt(team_dict['id']);
    if(_sb3_team_id !== null)
    {
        var _sb3_team_iter;
        for (_sb3_team_iter = 0; _sb3_team_iter < _sb3_teams.length; _sb3_team_iter++)
            if(_sb3_teams[_sb3_team_iter].id === _sb3_team_id)
            {
               _sb3_teams[_sb3_team_iter].update(team_dict);
               return;
            }
    }
    else return;
    team_dict.draw = _sb3_team_draw;
    team_dict.update = _sb3_team_update;
    _sb3_teams.push(team_dict);
    return team_dict;
}
function sb3_set_message(message)
{
    if(message !== null && message.length > 0) sb3_message = message;
    else sb3_message = sb3_message_default;
    _sb3_message_text_length = null;
}
function sb3_update_json(http_request)
{
    if(http_request.readyState === 4)
    {
        if(http_request.status === 200)
        {
            var _sb3_data = http_request.responseText;
            try
            {
                var _sb3_json_data = JSON.parse(_sb3_data), _sb3_json_int;
                _sb3_game_mode = parseInt(_sb3_json_data.mode);
                if(_sb3_game_name_div === null) _sb3_game_name_div = document.getElementById('sb3_game_title');
                if(_sb3_game_name_div !== null) _sb3_game_name_div.innerText = _sb3_json_data.name;
                if(_sb3_json_data.message !== null && _sb3_json_data.message.length > 0)
                    sb3_set_message(_sb3_json_data.message);
                for(_sb3_json_int = 0; _sb3_json_int < _sb3_json_data['teams'].length; _sb3_json_int++)
                    sb3_add_team(_sb3_json_data['teams'][_sb3_json_int]);
                if(sb3_delete_on_missing)
                {
                    var _sb3_remove_team = false, _sb3_json_int1;
                    for(_sb3_json_int = 0; _sb3_json_int < _sb3_teams.length; _sb3_json_int++)
                    {
                        _sb3_remove_team = true;
                        for(_sb3_json_int1 = 0; _sb3_json_int1 < _sb3_json_data['teams'].length; _sb3_json_int1++)
                            if(_sb3_teams[_sb3_json_int].id === parseInt(_sb3_json_data['teams'][_sb3_json_int1].id))
                            {
                                _sb3_remove_team = false;
                                break;
                            }
                        if(_sb3_remove_team)
                        {
                            var _sb3_team_div = document.getElementById('sb3_team_div_' + _sb3_teams[_sb3_json_int].id);
                            _sb3_team_div.outerHTML = '';
                            delete _sb3_team_div;
                            delete _sb3_teams[_sb3_json_int];
                        }
                    }
                    var _sb3_teams1 = [];
                    for(_sb3_json_int = 0; _sb3_json_int < _sb3_teams.length; _sb3_json_int++)
                    {
                        if(_sb3_teams[_sb3_json_int] !== null)
                            _sb3_teams1.push(_sb3_teams[_sb3_json_int]);
                    }
                    _sb3_teams = _sb3_teams1;
                }
                for(_sb3_json_int = 0; _sb3_json_int < _sb3_teams.length; _sb3_json_int++)
                    _sb3_teams[_sb3_json_int].draw();

            }
            catch(exception)
            {
                console.error('Exception occurred! ' + exception)
            }
        }
        else
        {
            console.error('Scoreboard returned ' + http_request.status + ' when attempting to update!');
            console.error(http_request.responseText);

        }
    }
}
function _sb3_team_update(team_update)
{
    this.name = team_update['name'];
    this.logo = team_update['logo'];
    this.color = team_update['color'];
    this.offense = team_update['offense'];
    this.beacons = parseInt(team_update['beacons']);
    this.flags['open'] = parseInt(team_update['flags']['open']);
    this.flags['lost'] = parseInt(team_update['flags']['lost']);
    this.score['total'] = parseInt(team_update['score']['total']);
    this.score['health'] = parseInt(team_update['score']['health']);
    this.tickets['open'] = parseInt(team_update['tickets']['open']);
    this.tickets['closed'] = parseInt(team_update['tickets']['closed']);
    var team_host_int, team_service_int;
    for(team_host_int = 0; team_host_int < team_update['hosts'].length; team_host_int++)
    {
        var team_host_ins = null, _sb3_host_inc;
        for(_sb3_host_inc = 0; _sb3_host_inc < this.hosts.length; _sb3_host_inc++)
            if(parseInt(this.hosts[_sb3_host_inc].id) === parseInt(team_update['hosts'][team_host_int].id))
            {
                team_host_ins = this.hosts[_sb3_host_inc];
                break;
            }
        if(team_host_ins === null)
        {
            team_host_ins = {};
            team_host_ins.services = [];
            this.hosts.push(team_host_ins);
        }
        team_host_ins.delete = false;
        team_host_ins.name = team_update['hosts'][team_host_int]['name'];
        team_host_ins.id = parseInt(team_update['hosts'][team_host_int].id);
        team_host_ins.online = team_update['hosts'][team_host_int]['online'];
        for(team_service_int = 0; team_service_int < team_update['hosts'][team_host_int]['services'].length; team_service_int++)
        {
            var team_service_ins = null, _sb3_service_inc;
            if(team_host_ins.services.length > 0)
                for(_sb3_service_inc = 0; _sb3_service_inc < team_host_ins.services.length; _sb3_service_inc++)
                    if(parseInt(team_host_ins.services[_sb3_service_inc].id) === parseInt(team_update['hosts'][team_host_int]['services'][team_service_int].id))
                    {
                        team_service_ins = team_host_ins.services[_sb3_service_inc];
                        break;
                    }
            if(team_service_ins === null)
            {
                team_service_ins = {};
                team_host_ins.services.push(team_service_ins);
            }
            team_service_ins.id = parseInt(team_update['hosts'][team_host_int]['services'][team_service_int].id);
            team_service_ins.bonus = team_update['hosts'][team_host_int]['services'][team_service_int]['bonus'];
            team_service_ins.status = team_update['hosts'][team_host_int]['services'][team_service_int]['status'];
            team_service_ins.protocol = team_update['hosts'][team_host_int]['services'][team_service_int]['protocol'];
            team_service_ins.port = parseInt(team_update['hosts'][team_host_int]['services'][team_service_int]['port']);
        }
    }
    if(sb3_delete_on_missing)
    {
        var _sb3_host_inc, _sb3_host_inc1, _sb3_host_mark;
        for(_sb3_host_inc = 0; _sb3_host_inc < this.hosts.length; _sb3_host_inc++)
        {
            _sb3_host_mark = true;
            for(_sb3_host_inc1 = 0; _sb3_host_inc1 < team_update['hosts'].length; _sb3_host_inc1++)
                if(this.hosts[_sb3_host_inc].id === parseInt(team_update['hosts'][_sb3_host_inc1].id))
                {
                   _sb3_host_mark = false;
                   break;
                }
            if(_sb3_host_mark)
                this.hosts[_sb3_host_inc].delete = true;
        }
    }
}
