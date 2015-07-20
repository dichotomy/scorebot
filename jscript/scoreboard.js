/**************************************************/
/**
 * Created by dichotomy on 7/7/14.
 */

function sleep(millis, callback) {
    setTimeout(function()
            { callback(); }
    , millis);
}

function getMovie() {
    $.getJSON( "http://www.prosversusjoes.net:8090/movie", function(data) {
        $.each( data, function(type, val) {
            if (type == "movie" ) {
                var name = val["name"];
                var length = val["length"];
                var div_movie = $( "<div>", {
                    "class": "movie",
                    id: "MovieElement"
                });
                div_movie.appendTo( "#main" );
                console.log(name)
                console.log(length)
                jwplayer("main").setup({
                    file: name,
                    autostart: true,
                    width: "100%",
                    height: "100%"
                });
                function remove_movie(){
                    $("#main_wrapper").remove()
                    console.log("Movie done");
                }
                sleep(length, remove_movie);
            }
        });
    });
}

function getScores() {
    $.getJSON( "http://www.prosversusjoes.net:8090/scores", function(data) {
        $(".score").remove()
        $(".scoreindent").remove()
        $(".scoreclear").remove()
        $.each( data, function(key,val) {
            var round = val[0];
            var score = val[1];
            var div_indent = $( "<div>", {
                "class": "scoreindent",
                html: "."
            })
            /* Team Name */
            var h5_team = $( "<h5>", {
                "class": "score",
                html: key
            });
            var div_team = $( "<div>", {
                "class": "score",
                html: h5_team
            });
            /* Team Score */
            var h5_team_score = $( "<h5>", {
                "class": "score",
                html: score
            });
            var div_score = $( "<div>", {
                "class": "score",
                html: h5_team_score
            });
            var div_clear = $( "<div>", {
                "class": "scoreclear"
            });
            /* Apply the HTML to the page */
            div_indent.appendTo( "#scorelist" );
            div_team.appendTo(   "#scorelist" );
            div_score.appendTo(  "#scorelist" );
            div_clear.appendTo(  "#scorelist" );
        });
    });
}

function getTickets() {
    $.getJSON( "http://www.prosversusjoes.net:8090/tickets", function(data) {
        $.each( data, function(team, tickets) {
            var ticket_team = "ticket".concat(team);
            var ticket_team_id = "#".concat(ticket_team);
            $( ticket_team_id ).remove();
            var div_team = $( "<div>", {
                "class": "ticket_block",
                "id": ticket_team
            });
            div_team.appendTo("#TicketBlock");
            var div_indent = $( "<div>", {
                "class": "indent",
                html: "."
            });
            div_indent.appendTo(ticket_team_id);
            var h5_team = $( "<h5>", {
                "class": "ticket_title",
                html: team
            });
            var div_ticket_team = $( "<div>", {
                "class": "ticket_team",
                html: h5_team
            });
            div_ticket_team.appendTo(ticket_team_id);
            var all_tickets = "All: ".concat(tickets[0]);
            var h5_all_tickets = $( "<h5>", {
                "class": "ticket",
                html: all_tickets
            });
            var div_all_tickets = $( "<div>", {
                "class": "ticket",
                html: h5_all_tickets
            });
            div_all_tickets.appendTo(ticket_team_id);
            var closed_tickets = "Closed: ".concat(tickets[1]);
            var h5_closed_tickets = $( "<h5>", {
                "class": "ticket",
                html: closed_tickets
            });
            var div_closed_tickets = $( "<div>", {
                "class": "ticket",
                html: h5_closed_tickets
            });
            div_closed_tickets.appendTo(ticket_team_id);
        })
    })
}

function getBeacons() {
    $.getJSON( "http://www.prosversusjoes.net:8090/beacons", function(data) {
        $.each( data, function(bandit, pwnedset) {
            var bandit_id = "#".concat(bandit);
            $( bandit_id).remove();
            var bandit_block = $( "<div>", {
                "class": "beacon_block",
                "id": bandit
            });
            bandit_block.appendTo("#BeaconBlock");
            var div_indent = $( "<div>", {
                "class": "indent",
                html: "."
            })
            div_indent.appendTo(bandit_id);
            var h5_bandit = $( "<h5>", {
                "class": "beacon",
                html: bandit
            });
            var div_bandit = $( "<div>", {
                "class": "beacon_label",
                html: h5_bandit
            });
            div_bandit.appendTo(bandit_id);
            $.each( pwnedset, function(team, count) {
                var beacon_team = "beacon".concat(team);
                var team_id = "#".concat(beacon_team);
                $( team_id).remove();
                var div_beacon_team = $( "<div>", {
                    "class": "beacon_team",
                    html: ".",
                    "id": beacon_team
                })
                div_beacon_team.appendTo(bandit_id);
                var div_indent = $( "<div>", {
                    "class": "indent",
                    html: "."
                })
                div_indent.appendTo(team_id);
                var h5_team = $( "<h5>", {
                    "class": "beacon",
                    html: team
                });
                var div_beacon_team_title = $( "<div>", {
                    "class": "beacon_team_title",
                    html: h5_team
                });
                div_beacon_team_title.appendTo(team_id);
                for (i=0; i< count; i++) {
                    var skull_img = $( "<img>", {
                        "src": "/images/redskull.jpeg",
                        "height": "40px"
                    });
                    var skull_div = $( "<div>", {
                        "class": "beacon",
                        html: skull_img
                    })
                    skull_div.appendTo(team_id);
                }
            })
        })
    })
}

function getHealth(){
    $.getJSON( "http://www.prosversusjoes.net:8090/health", function(data) {
        $.each ( data, function(team, hosts) {
            host_scores= {}
            servicelist = []
            statuslist = []
            var team_id = "#".concat(team);
            $( team_id).remove();
            var service_block = $( "<div>", {
                "class": "service_block",
                "id": team
            });
            service_block.appendTo("#ServiceBlock");
            var div_indent = $( "<div>", {
                "class": "indent",
                html: "."
            })
            div_indent.appendTo(team_id);
            var h5_team = $( "<h5>", {
                "class": "health",
                html: team
            });
            var div_team = $( "<div>", {
                "class": "health_label",
                html: h5_team
            });
            div_team.appendTo(team_id);
            $.each ( hosts, function(host, services) {
                host_scores[host] = {};
                $.each (services, function(service, status) {
                    indx = servicelist.indexOf(service);
                    if (indx>=0) {
                        true;
                    } else {
                        servicelist.push(service);
                    }
                    host_scores[host][service] = status
                });
            });
            var num_services = servicelist.length;
            for (var i=0; i < num_services; i++) {
                service = servicelist[i];
                var h5_service = $( "<h5>", {
                    "class": "health",
                    html: service
                })
                var div_service = $( "<div>", {
                    "class": "health_service",
                    html: h5_service
                })
                div_service.appendTo(team_id);
            }
            $("<div>", { "class": "clear"}).appendTo(team_id);
            $.each( host_scores, function(host, scores) {
                var div_indent = $( "<div>", {
                    "class": "indent",
                    html: "."
                })
                div_indent.appendTo(team_id);
                var host_h5 = $( "<h5>", {
                    "class": "health",
                    html: host
                });
                var host_div = $( "<div>", {
                    "class": "health_label",
                    html: host_h5
                })
                host_div.appendTo(team_id);
                var num_services = servicelist.length;
                for (var i=0; i < num_services; i++) {
                    service = servicelist[i];
                    if (service in scores) {
                        score = scores[service];
                        if (score == "2") {
                            this_class = "green";
                        } else if ( score == "1" ) {
                            this_class = "yellow";
                        } else if ( score == "0" ) {
                            this_class = "red";
                        }
                        var p = $( "<p>", {html:""});
                        $( "<div>", {
                            "class": this_class,
                            html: p
                        }).appendTo(team_id)
                    } else {
                        var p = $( "<p>", {html:""});
                        $( "<div>", {
                            "class": "empty",
                            html: p
                        }).appendTo(team_id)
                    }
                };
                $( "<div>", {
                    "class": "clear"
                }).appendTo(team_id);
            });
        });
    });
}

function getMarquee() {
    $.getJSON( "http://www.prosversusjoes.net:8090/marquee", function(data) {
        $.each (data, function(key, val) {
            if (key == "marquee") {
                $( ".marquee" ).html(val);
            }
        })
    });
}

function getFlags() {
    $.getJSON( "http://www.prosversusjoes.net:8090/flags", function(data) {
        $.each (data, function(type, flags) {
            if (type == "lost") {
                $("#flag-lost").remove()
                var div_lost = $( "<div>", {
                    "class": "flag_container",
                    "id": "flag-lost",
                });
                div_lost.appendTo("#flaglist");
                var div_indent = $( "<div>", {
                    "class": "indent",
                    html: "."
                });
                div_indent.appendTo("#flag-lost");
                var h5_lost_label = $( "<h5>", {
                    "class": "flag_label",
                    html: "Lost Flags"
                });
                var div_lost_label = $( "<div>", {
                    "class": "flag_label",
                    html: h5_lost_label
                });
                div_lost_label.appendTo("#flag-lost");
                $.each (flags, function(team, flags) {
                    var team_label = "lost-".concat(team);
                    var team_lost = team.concat(": ");
                    var div_indent = $( "<div>", {
                        "class": "indent",
                        html: "."
                    });
                    div_indent.appendTo("#flag-lost");
                    var h5_team = $( "<h5>", {
                        "class": "flag_label",
                        html: team_lost
                    });
                    var div_h5_team = $( "<div>", {
                        "class": "flag_label",
                        html: h5_team
                    });
                    var flagcount = flags.length;
                    var div_team = $( "<div>", {
                        "class": "flag_set",
                        "id": team_label,
                    });
                    div_indent.appendTo(div_team);
                    div_h5_team.appendTo(div_team);
                    for (i=0; i< flagcount; i++) {
                        var flag_img = $( "<img>", {
                            "src": "/images/stolenflag2.png",
                            "height": "30px"
                        });
                        var flag_div = $( "<div>", {
                            "class": "flag",
                            html: flag_img
                        })
                        flag_div.appendTo(div_team);
                    }
                    div_team.appendTo("#flag-lost");
                });
            } else if (type == "stolen") {
                $("#flag-stolen").remove()
                var div_stolen = $( "<div>", {
                    "class": "flag_container",
                    "id": "flag-stolen",
                });
                div_stolen.appendTo("#flaglist");
                var div_indent = $( "<div>", {
                    "class": "indent",
                    html: "."
                })
                div_indent.appendTo("#flag-stolen");
                var h5_stolen_label = $( "<h5>", {
                    "class": "flag_label",
                    html: "Stolen Flags"
                });
                var div_stolen_label = $( "<div>", {
                    "class": "flag_label",
                    html: h5_stolen_label
                })
                div_stolen_label.appendTo("#flag-stolen");
                $.each (flags, function(team, flags) {
                    var team_label = "stolen-".concat(team);
                    var team_stolen = team.concat(": ");
                    var flaglist = flags.join(", ");
                    team_stolen = team_stolen.concat(flaglist);
                    var div_indent = $( "<div>", {
                        "class": "indent",
                        html: "."
                    })
                    div_indent.appendTo("#flag-stolen");
                    var h5_team = $( "<h5>", {
                        "class": "flag_label",
                        html: team_stolen
                    });
                    var div_team = $( "<div>", {
                        "class": "flag_label",
                        "id": team_label,
                        html: h5_team
                    });
                    div_team.appendTo("#flag-stolen");
                });
            } else if (type == "integrity") {
                $("#flag-integrity").remove()
                var div_integrity = $( "<div>", {
                    "class": "flag_container",
                    "id": "flag-integrity",
                });
                div_integrity.appendTo("#flaglist");
                var div_indent = $( "<div>", {
                    "class": "indent",
                    html: "."
                })
                div_indent.appendTo("#flag-integrity");
                var h5_integrity_label = $( "<h5>", {
                    "class": "flag_label",
                    html: "Integrity Flags"
                });
                var div_integrity_label = $( "<div>", {
                    "class": "flag_label",
                    html: h5_integrity_label
                });
                div_integrity_label.appendTo("#flag-integrity");
                $.each (flags, function(team, flags) {
                    var team_label = "integrity-".concat(team);
                    var team_intergity = team.concat(": ");
                    var flaglist = flags.join(", ");
                    team_intergity = team_intergity.concat(flaglist);
                    var div_indent = $( "<div>", {
                        "class": "indent",
                        html: "."
                    })
                    div_indent.appendTo("#flag-integrity");
                    var h5_team = $( "<h5>", {
                        "class": "flag_label",
                        html: team_intergity
                    });
                    var div_team = $( "<div>", {
                        "class": "flag_label",
                        "id": team_label,
                        html: h5_team
                    });
                    div_team.appendTo("#flag-integrity");
                });
            } else if (type == "bandits") {
                $("#bandits").remove()
                var div_bandits = $( "<div>", {
                    "class": "flag_container",
                    "id": "bandits",
                });
                div_bandits.appendTo("#flaglist");
                var div_indent = $( "<div>", {
                    "class": "indent",
                    html: "."
                })
                div_indent.appendTo("#bandits");
                var h5_bandits_label = $( "<h5>", {
                    "class": "flag_label",
                    html: "Red Cell Flags"
                });
                var div_bandits_label = $( "<div>", {
                    "class": "flag_label",
                    html: h5_bandits_label
                })
                div_bandits_label.appendTo("#bandits");
                $.each (flags, function(bandit, flags) {
                    var bandit_label = "stolen-".concat(bandit);
                    var bandit_stole = bandit.concat(": ");
                    var flaglist = flags.join(", ");
                    bandit_stole = bandit_stole.concat(flaglist);
                    var div_indent = $( "<div>", {
                        "class": "indent",
                        html: "."
                    })
                    div_indent.appendTo("#bandits");
                    var h5_bandit = $( "<h5>", {
                        "class": "flag_label",
                        html: bandit_stole
                    });
                    var div_bandit = $( "<div>", {
                        "class": "flag_label",
                        "id": bandit_label,
                        html: h5_bandit
                    });
                    div_bandit.appendTo("#bandits");
                });
            }
        })
    })
}

getScores();
getHealth();
getMarquee();
getFlags();
getBeacons();
getTickets();

setInterval(function() {
    getScores();
    getHealth();
    getMarquee();
    getFlags();
    getBeacons();
    getTickets();
}, 10000);
