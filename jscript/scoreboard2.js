/**
 * Created by dichotomy on 7/12/15.
 */

function sleep(millis, callback) {
    setTimeout(function()
        { callback(); }
        , millis);
}

function trunkname(name) {
    var i = 0;
    shortname = "";
    while (i < name.length) {
        character = name.charAt(i);
        if (!isNaN(character*1)) {
            1;
        } else {
            if (character == character.toUpperCase()){
                shortname += character
            }
        }
        i += 1;
    }
    return shortname

}

function getMovie() {
    $.getJSON( "http://localhost:8090/movie", function(data) {
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

function setCredits() {
    $(".credit").remove();
    $(".creditclear").remove();
    var d = new Date();
    var n = d.getTime();
    var ns = n.toString();
    var b = ns.charAt(ns.length-1);
    var a = +b
    if ((a == 1) || (a == 2)) {
        var h5_credit = $("<h5>", {
            "class": "credit",
            html: "The Pros V Joes 2016 build and support crew:  Gi0cann, idigitalflame"
        });
        h5_credit.appendTo("#creditslist");
    } else if ((a == 3) || (a == 4 )) {
        var h5_credit = $("<h5>", {
            "class": "credit",
            html: "Thanks to Maven Security for their contributions!"
        });
        var img_credit = $("<img>", {
            "class": "credit",
            "src": "/images/logo-no-binary.png"
        });
        var div_credit = $("<div>", {
            "class": "credit",
            html: h5_credit
        });
        img_credit.appendTo(div_credit);
        div_credit.appendTo("#creditslist");
    } else if ((a == 5) || (a == 6))  {
        var h5_credit = $("<h5>", {
            "class": "credit",
            html: "Special thanks to Bijoti for the use of their monitoring equipment and software"
        });
        var img_credit = $("<img>", {
            "class": "credit",
            "src": "/images/data-marshal-transparent.jpg"
        });
        var div_credit = $("<div>", {
            "class": "credit",
            html: h5_credit
        });
        img_credit.appendTo(div_credit);
        div_credit.appendTo("#creditslist");
    } else if ((a == 7) || (a == 8))  {
        var h5_credit = $("<h5>", {
            "class": "credit",
            html: "Special thanks to Gi0cann for his many years of support!"
        });
        var img_credit = $("<img>", {
            "class": "credit",
            "src": "/images/gi0cann.jpg"
        });
        var div_credit = $("<div>", {
            "class": "credit",
            html: h5_credit
        });
        img_credit.appendTo(div_credit);
        div_credit.appendTo("#creditslist");
    } else {
        var h5_credit = $("<h5>", {
            "class": "credit",
            html: "CTF equipment provided by Wilmington University"
        });
        var img_credit = $("<img>", {
            "class": "credit",
            "src": "/images/wilmu.jpeg"
        });
        var div_credit = $("<div>", {
            "class": "credit",
            html: h5_credit
        });
        img_credit.appendTo(div_credit);
        div_credit.appendTo("#creditslist");
    }
    var div_credit_clear = $("<div>", {
        "class": "creditclear"
    });
    div_credit_clear.appendTo("#creditslist");
}

function getTeamNames() {
    $.getJSON( "http://www.prosversusjoes.net:8090/teamnames", function(data) {
        $(".teamname").remove();
        $(".teamindent").remove();
        $.each( data["teamnames"], function(index, name) {
            var shortname = trunkname(name);
            var h5_team = $("<h5>", {
                "class": "teamname",
                html: name + " (" + shortname + ")"
            });
            var div_team = $("<div>", {
                "class": "teamname",
                html: h5_team
            });
            div_team.appendTo("#teamlist");
            var div_indent = $("<div>", {
                "class": "teamindent",
                html: "."
            });
            div_indent.appendTo("#teamlist")
        });
    });
}


function getScores() {
    $.getJSON( "http://localhost:8090/scores2", function(data) {
        $(".score").remove();
        $(".score_type").remove();
        $(".scoreindent").remove();
        $(".scoreclear").remove();
        $.each( data, function (team, scores) {
            var h5_team = $("<h5>", {
                "class": "score",
                html: trunkname(team)
            });
            var div_team = $( "<div>", {
                "class": "score",
                html: h5_team
            });
            div_team.appendTo("#scorelist");
        });
        // Total score
        var div_clear1 = $("<div>", {
            "class": "scoreclear"
        });
        div_clear1.appendTo("#scorelist");
        var div_indent1 = $("<div>", {
            "class": "scoreindent",
            html: "."
        });
        div_indent1.appendTo("#scorelist")
        var h5_total = $("<h4>", {
            "class": "score",
            html: "Total"
        });
        var div_total1 = $("<div>", {
            "class": "score_type",
            html: h5_total
        });
        div_total1.appendTo("#scorelist")
        $.each (data, function (team, scores){
            var h5_total = $("<h4>", {
                "class": "score",
                html: scores["total"]
            });
            var div_total = $("<div>", {
                "class": "score",
                html: h5_total
            });
            div_total.appendTo("#scorelist")
        });
        var div_clear2 = $("<div>", {
            "class": "scoreclear"
        });
        div_clear2.appendTo("#scorelist");
        // Service score
        var div_clear2 = $("<div>", {
            "class": "scoreclear"
        });
        div_clear2.appendTo("#scorelist");
        var div_indent2 = $("<div>", {
            "class": "scoreindent",
            html: "."
        });
        div_indent2.appendTo("#scorelist")
        var h5_service = $("<h5>", {
            "class": "score",
            html: "Services"
        });
        var div_service1 = $("<div>", {
            "class": "score_type",
            html: h5_service
        });
        div_service1.appendTo("#scorelist")
        $.each (data, function (team, scores){
            var h5_service = $("<h5>", {
                "class": "score",
                html: scores["services"]
            });
            var div_service = $("<div>", {
                "class": "score",
                html: h5_service
            });
            div_service.appendTo("#scorelist")
        });
        var div_clear4 = $("<div>", {
            "class": "scoreclear"
        });
        div_clear4.appendTo("#scorelist");
        // Flags score
        var div_clear5 = $("<div>", {
            "class": "scoreclear"
        });
        div_clear5.appendTo("#scorelist");
        var div_indent3 = $("<div>", {
            "class": "scoreindent",
            html: "."
        });
        div_indent3.appendTo("#scorelist")
        var h5_flag1 = $("<h5>", {
            "class": "score",
            html: "Flags"
        });
        var div_flag1 = $("<div>", {
            "class": "score_type",
            html: h5_flag1
        });
        div_flag1.appendTo("#scorelist")
        $.each (data, function (team, scores){
            var h5_flag = $("<h5>", {
                "class": "score",
                html: scores["flags"]
            });
            var div_flag = $("<div>", {
                "class": "score",
                html: h5_flag
            });
            div_flag.appendTo("#scorelist")
        });
        var div_clear5 = $("<div>", {
            "class": "scoreclear"
        });
        div_clear5.appendTo("#scorelist");
        // Tickets score
        var div_clear7 = $("<div>", {
            "class": "scoreclear"
        });
        div_clear7.appendTo("#scorelist");
        var div_indent4 = $("<div>", {
            "class": "scoreindent",
            html: "."
        });
        div_indent4.appendTo("#scorelist")
        var h5_ticket1 = $("<h5>", {
            "class": "score",
            html: "Tickets"
        });
        var div_ticket1 = $("<div>", {
            "class": "score_type",
            html: h5_ticket1
        });
        div_ticket1.appendTo("#scorelist")
        $.each (data, function (team, scores){
            var h5_ticket = $("<h5>", {
                "class": "score",
                html: scores["tickets"]
            });
            var div_ticket = $("<div>", {
                "class": "score",
                html: h5_ticket
            });
            div_ticket.appendTo("#scorelist")
        });
        var div_clear8 = $("<div>", {
            "class": "scoreclear"
        });
        div_clear8.appendTo("#scorelist");
        // Beacons score
        var div_clear9 = $("<div>", {
            "class": "scoreclear"
        });
        div_clear9.appendTo("#scorelist");
        var div_indent5 = $("<div>", {
            "class": "scoreindent",
            html: "."
        });
        div_indent5.appendTo("#scorelist")
        var h5_beacon1 = $("<h5>", {
            "class": "score",
            html: "Beacons"
        });
        var div_beacon1 = $("<div>", {
            "class": "score_type",
            html: h5_beacon1
        });
        div_beacon1.appendTo("#scorelist")
        $.each (data, function (team, scores){
            var h5_beacon = $("<h5>", {
                "class": "score",
                html: scores["beacons"]
            });
            var div_beacon = $("<div>", {
                "class": "score",
                html: h5_beacon
            });
            div_beacon.appendTo("#scorelist")
        });
        var div_clear10 = $("<div>", {
            "class": "scoreclear"
        });
        div_clear10.appendTo("#scorelist");
    });
}

function getTickets() {
    $.getJSON( "http://localhost:8090/tickets", function(data) {
        $(".ticket").remove();
        $(".ticket_type").remove();
        $(".ticketindent").remove();
        $(".ticketclear").remove();
        $.each( data, function(team, tickets) {
            var h5_team = $("<h5>", {
                "class": "ticket",
                html: trunkname(team)
            });
            var div_team = $( "<div>", {
                "class": "ticket",
                html: h5_team
            });
            div_team.appendTo("#ticketlist");
        });
        // Label for the closed tickets row
        var div_clear2 = $("<div>", {
            "class": "ticketclear"
        });
        var div_indent2 = $("<div>", {
            "class": "ticketindent",
            html: "."
        });
        var h5_closed = $("<h5>", {
            "class": "ticket",
            html: "Closed"
        });
        var div_closed = $( "<div>", {
            "class": "ticket_type",
            html: h5_closed
        });
        var closed_ticket_img = $( "<img>", {
            "src": "/images/closedticket.png",
            "class": "ticket"
        });
        closed_ticket_img.appendTo(div_closed);
        div_clear2.appendTo("#ticketlist");
        div_indent2.appendTo("#ticketlist");
        div_closed.appendTo("#ticketlist");
        // Itterate throught the closed tickets
        $.each( data, function(team, tickets) {
            var h5_closed_tickets = $( "<h5>", {
                "class": "ticket_item",
                html: tickets[1]
            });
            var div_closed_tickets = $( "<div>", {
                "class": "ticket",
                html: h5_closed_tickets
            });
            div_closed_tickets.appendTo("#ticketlist");
        });
        var div_clear3 = $("<div>", {
            "class": "ticketclear"
        });
        div_clear3.appendTo("#ticketlist");
        // Label for the open tickets row
        var div_clear1 = $("<div>", {
            "class": "ticketclear"
        });
        var div_indent1 = $("<div>", {
            "class": "ticketindent",
            html: "."
        });
        var h5_open = $("<h5>", {
            "class": "ticket",
            html: "Open"
        });
        var div_open = $( "<div>", {
            "class": "ticket_type",
            html: h5_open
        });
        var open_ticket_img = $( "<img>", {
            "src": "/images/openticket.png",
            "class": "ticket"
        });
        open_ticket_img.appendTo(div_open);
        div_clear1.appendTo("#ticketlist");
        div_indent1.appendTo("#ticketlist");
        div_open.appendTo("#ticketlist");
        // Itterate through the open tickets
        $.each( data, function(team, tickets) {
            var h5_open_tickets = $("<h5>", {
                "class": "ticket_item",
                html: tickets[0]
            });
            var div_open_tickets = $("<div>", {
                "class": "ticket",
                html: h5_open_tickets
            });
            div_open_tickets.appendTo("#ticketlist");
        });
    })
}

function getRedcell() {
    $.getJSON( "http://localhost:8090/redcell", function(data) {
        $(".redcell").remove();
        $(".redflag").remove();
        $(".redskull").remove();
        $(".redcindent").remove();
        $(".redclear").remove();
        $.each( data, function(bandit, achieved) {
            var div_indent = $( "<div>", {
                "class":  "redindent",
                "html": "."
            });
            div_indent.appendTo("relist");
            var h5_bandit = $( "<h5>", {
                "class": "redcell",
                html:bandit
            });
            var div_bandit = $( "<div>", {
                "class": "redcell",
                html: h5_bandit
            });
            div_bandit.appendTo("#redlist");
            $.each(achieved, function(type, result) {
                if (type == "beacons"){
                    $.each( result, function(team, count) {
                        var h5_team = $( "<h5>", {
                            "class": "redcell",
                            html: team
                        });
                        for (i=0; i<count; i++) {
                            var skull_img = $( "<img>", {
                                "src": "/images/redskull.jpeg",
                                "class": "redskull"
                            });
                            skull_img.appendTo("#redlist");
                        }
                    });
                } else if (type == "flags") {
                    var flagcount = result.length;
                    for (i=0; i<flagcount; i++) {
                        var flag_img = $( "<img>", {
                            "src": "/images/stolenflag2.png",
                            "class": "redflag"
                        });
                        flag_img.appendTo("#redlist");
                    }
                }
            });
        });
    });
}

function getFlags() {
    $.getJSON( "http://localhost:8090/flags2", function(data) {
        $(".flag").remove();
        $(".flag_type").remove();
        $(".flagindent").remove();
        $(".flagclear").remove();
        $.each( data, function(type, flags) {
            if (type=="teams") {
                $.each( flags, function(team, flag_types) {
                        var h5_team = $("<h5>", {
                            "class": "flag",
                            html: trunkname(team)
                        });
                        var div_team = $( "<div>", {
                            "class": "flag",
                            html: h5_team
                        });
                        div_team.appendTo("#flaglist");
                });
                // Label for the Found flags row
                var div_clear1 = $("<div>", {
                    "class": "flagclear"
                });
                var div_indent1 = $("<div>", {
                    "class": "flagindent",
                    html: "."
                });
                var h5_found = $("<h5>", {
                    "class": "flag",
                    html: "Found"
                });
                var div_found = $( "<div>", {
                    "class": "flag_type",
                    html: h5_found
                });
                var found_flag_img = $( "<img>", {
                    "class": "flag",
                    "src": "/images/integrityflag.png"
                });
                found_flag_img.appendTo(div_found);
                div_clear1.appendTo("#flaglist");
                div_indent1.appendTo("#flaglist");
                div_found.appendTo("#flaglist");
                // Itterate through the found flags
                $.each( flags, function(team, flag_types) {
                    var h5_found_flags = $("<h5>", {
                        "class": "flag_item",
                        html: flag_types["integrity"].length
                    });
                    var div_found_flags = $("<div>", {
                        "class": "flag",
                        html: h5_found_flags
                    });
                    div_found_flags.appendTo("#flaglist");
                });
                // Label for the closed tickets row
                var div_clear2 = $("<div>", {
                    "class": "flagclear"
                });
                var div_indent2 = $("<div>", {
                    "class": "flagindent",
                    html: "."
                });
                var h5_lost = $("<h5>", {
                    "class": "flag",
                    html: "Lost"
                });
                var div_lost = $( "<div>", {
                    "class": "flag_type",
                    html: h5_lost
                });
                var lost_flag_img = $( "<img>", {
                    "src": "/images/stolenflag2.png",
                    "class": "flag"
                });
                lost_flag_img.appendTo(div_lost);
                div_clear2.appendTo("#flaglist");
                div_indent2.appendTo("#flaglist");
                div_lost.appendTo("#flaglist");
                // Itterate throught the closed tickets
                $.each( flags, function(team, flag_types) {
                    var h5_lost_flags = $( "<h5>", {
                        "class": "flag_item",
                        html: flag_types["lost"].length
                    });
                    var div_lost_flags = $( "<div>", {
                        "class": "flag",
                        html: h5_lost_flags
                    });
                    div_lost_flags.appendTo("#flaglist");
                });
                var div_clear3 = $("<div>", {
                    "class": "flagclear"
                });
                div_clear3.appendTo("#flaglist");
            };
        });
    });
}

function getHealth(){
    $.getJSON( "http://localhost:8090/health", function(data) {
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
                html: trunkname(team)
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

function getBeacons() {
    $.getJSON("http://localhost:8090/beacons/teams", function(data) {
        $(".healthredskull").remove();
        $(".beacon_label").remove();
        $(".beacon_block").remove();
        $(".skulllabel").remove();
        $.each (data, function(team, count) {
            var h5_team = $( "<h5>", {
                "class": "skulllabel",
                html:team
            });
            var div_team = $( "<div>", {
                "class": "beacon_label",
                html: h5_team
            });
            div_team.appendTo("#BeaconBlock");
            for (i=0; i<count; i++) {
                var skull_img = $( "<img>", {
                    "src": "/images/redskull.jpeg",
                    "class": "healthredskull"
                });
                var div_img = $( "<div>", {
                    "class": "beacon_block",
                    html: skull_img
                });
                div_img.appendTo("#BeaconBlock");
            }
        });
    });
}

function getMarquee() {
    $.getJSON( "http://localhost:8090/marquee", function(data) {
        $.each (data, function(key, val) {
            if (key == "marquee") {
                $( ".marquee" ).html(val);
            }
        })
    });
}

getTeamNames();
getScores();
getHealth();
getMarquee();
getFlags();
getBeacons();
getTickets();
getRedcell();
setCredits();

setInterval(function() {
    getScores();
    getHealth();
    getMarquee();
    getFlags();
    getBeacons();
    getTickets();
    getRedcell();
    getTeamNames();
}, 10000);

setInterval(function() {
    setCredits();
}, 5000);
