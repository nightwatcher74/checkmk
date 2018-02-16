#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# +------------------------------------------------------------------+
# |             ____ _               _        __  __ _  __           |
# |            / ___| |__   ___  ___| | __   |  \/  | |/ /           |
# |           | |   | '_ \ / _ \/ __| |/ /   | |\/| | ' /            |
# |           | |___| | | |  __/ (__|   <    | |  | | . \            |
# |            \____|_| |_|\___|\___|_|\_\___|_|  |_|_|\_\           |
# |                                                                  |
# | Copyright Mathias Kettner 2014             mk@mathias-kettner.de |
# +------------------------------------------------------------------+
#
# This file is part of Check_MK.
# The official homepage is at http://mathias-kettner.de/check_mk.
#
# check_mk is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# tails. You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

import json

import sites, notify, table
import livestatus
import notifications

#   .--Overview------------------------------------------------------------.
#   |              ___                       _                             |
#   |             / _ \__   _____ _ ____   _(_) _____      __              |
#   |            | | | \ \ / / _ \ '__\ \ / / |/ _ \ \ /\ / /              |
#   |            | |_| |\ V /  __/ |   \ V /| |  __/\ V  V /               |
#   |             \___/  \_/ \___|_|    \_/ |_|\___| \_/\_/                |
#   |                                                                      |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'

def dashlet_overview(nr, dashlet):

    html.open_table(class_="dashlet_overview")
    html.open_tr()
    html.open_td(valign="top")
    html.open_a(href="https://mathias-kettner.com/check_mk.html")
    html.img("images/check_mk.trans.120.png", style="margin-right: 30px;")
    html.close_a()
    html.close_td()

    html.open_td()
    html.h2("Check_MK Multisite")
    html.write_html('Welcome to Check_MK Multisite. If you want to learn more about Multisite, please visit '
                    'our <a href="https://mathias-kettner.com/checkmk_multisite.html">online documentation</a>. '
                    'Multisite is part of <a href="https://mathias-kettner.com/check_mk.html">Check_MK</a> - an Open Source '
                    'project by <a href="https://mathias-kettner.com">Mathias Kettner</a>.')
    html.close_td()

    html.close_tr()
    html.close_table()

dashlet_types["overview"] = {
    "title"       : _("Overview / Introduction"),
    "description" : _("Displays an introduction and Check_MK logo."),
    "render"      : dashlet_overview,
    "allowed"     : config.builtin_role_ids,
    "selectable"  : False, # can not be selected using the dashboard editor
}

#.
#   .--MK-Logo-------------------------------------------------------------.
#   |               __  __ _  __     _                                     |
#   |              |  \/  | |/ /    | |    ___   __ _  ___                 |
#   |              | |\/| | ' /_____| |   / _ \ / _` |/ _ \                |
#   |              | |  | | . \_____| |__| (_) | (_| | (_) |               |
#   |              |_|  |_|_|\_\    |_____\___/ \__, |\___/                |
#   |                                           |___/                      |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'

def dashlet_mk_logo(nr, dashlet):
    html.open_a(href="https://mathias-kettner.com/check_mk.html")
    html.img("images/check_mk.trans.120.png", style="margin-right: 30px;")
    html.close_a()

dashlet_types["mk_logo"] = {
    "title"       : _("Check_MK Logo"),
    "description" : _("Shows the Check_MK logo."),
    "render"      : dashlet_mk_logo,
    "allowed"     : config.builtin_role_ids,
    "selectable"  : False, # can not be selected using the dashboard editor
}

#.
#   .--Globes/Stats--------------------------------------------------------.
#   |       ____ _       _                  ______  _        _             |
#   |      / ___| | ___ | |__   ___  ___   / / ___|| |_ __ _| |_ ___       |
#   |     | |  _| |/ _ \| '_ \ / _ \/ __| / /\___ \| __/ _` | __/ __|      |
#   |     | |_| | | (_) | |_) |  __/\__ \/ /  ___) | || (_| | |_\__ \      |
#   |      \____|_|\___/|_.__/ \___||___/_/  |____/ \__\__,_|\__|___/      |
#   |                                                                      |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'

def dashlet_hoststats(nr, dashlet):
    table = [
       ( _("Up"), "#0b3",
        "searchhost&is_host_scheduled_downtime_depth=0&hst0=on",
        "Stats: state = 0\n" \
        "Stats: scheduled_downtime_depth = 0\n" \
        "StatsAnd: 2\n"),

       ( _("Down"), "#f00",
        "searchhost&is_host_scheduled_downtime_depth=0&hst1=on",
        "Stats: state = 1\n" \
        "Stats: scheduled_downtime_depth = 0\n" \
        "StatsAnd: 2\n"),

       ( _("Unreachable"), "#f80",
        "searchhost&is_host_scheduled_downtime_depth=0&hst2=on",
        "Stats: state = 2\n" \
        "Stats: scheduled_downtime_depth = 0\n" \
        "StatsAnd: 2\n"),

       ( _("In Downtime"), "#0af",
        "searchhost&search=1&is_host_scheduled_downtime_depth=1",
        "Stats: scheduled_downtime_depth > 0\n" \
       )
    ]
    filter = "Filter: custom_variable_names < _REALNAME\n"

    render_statistics('dashlet_%d' % nr, "hosts", table, filter, dashlet)

dashlet_types["hoststats"] = {
    "title"       : _("Host Statistics"),
    "sort_index"  : 45,
    "description" : _("Displays statistics about host states as globe and a table."),
    "render"      : dashlet_hoststats,
    "refresh"     : 60,
    "allowed"     : config.builtin_role_ids,
    "size"        : (30, 18),
    "resizable"   : False,
}

def dashlet_servicestats(nr, dashlet):
    table = [
       ( _("OK"), "#0b3",
        "searchsvc&hst0=on&st0=on&is_in_downtime=0",
        "Stats: state = 0\n" \
        "Stats: scheduled_downtime_depth = 0\n" \
        "Stats: host_scheduled_downtime_depth = 0\n" \
        "Stats: host_state = 0\n" \
        "Stats: host_has_been_checked = 1\n" \
        "StatsAnd: 5\n"),

       ( _("In Downtime"), "#0af",
        "searchsvc&is_in_downtime=1",
        "Stats: scheduled_downtime_depth > 0\n" \
        "Stats: host_scheduled_downtime_depth > 0\n" \
        "StatsOr: 2\n"),

       ( _("On Down host"), "#048",
        "searchsvc&hst1=on&hst2=on&hstp=on&is_in_downtime=0",
        "Stats: scheduled_downtime_depth = 0\n" \
        "Stats: host_scheduled_downtime_depth = 0\n" \
        "Stats: host_state != 0\n" \
        "StatsAnd: 3\n"),

       ( _("Warning"), "#ff0",
        "searchsvc&hst0=on&st1=on&is_in_downtime=0",
        "Stats: state = 1\n" \
        "Stats: scheduled_downtime_depth = 0\n" \
        "Stats: host_scheduled_downtime_depth = 0\n" \
        "Stats: host_state = 0\n" \
        "Stats: host_has_been_checked = 1\n" \
        "StatsAnd: 5\n"),

       ( _("Unknown"), "#f80",
        "searchsvc&hst0=on&st3=on&is_in_downtime=0",
        "Stats: state = 3\n" \
        "Stats: scheduled_downtime_depth = 0\n" \
        "Stats: host_scheduled_downtime_depth = 0\n" \
        "Stats: host_state = 0\n" \
        "Stats: host_has_been_checked = 1\n" \
        "StatsAnd: 5\n"),

       ( _("Critical"), "#f00",
        "searchsvc&hst0=on&st2=on&is_in_downtime=0",
        "Stats: state = 2\n" \
        "Stats: scheduled_downtime_depth = 0\n" \
        "Stats: host_scheduled_downtime_depth = 0\n" \
        "Stats: host_state = 0\n" \
        "Stats: host_has_been_checked = 1\n" \
        "StatsAnd: 5\n"),
    ]
    filter = "Filter: host_custom_variable_names < _REALNAME\n"

    render_statistics('dashlet_%d' % nr, "services", table, filter, dashlet)


dashlet_types["servicestats"] = {
    "title"       : _("Service Statistics"),
    "sort_index"  : 50,
    "description" : _("Displays statistics about service states as globe and a table."),
    "render"      : dashlet_servicestats,
    "refresh"     : 60,
    "allowed"     : config.builtin_role_ids,
    "size"        : (30, 18),
    "resizable"   : False,
}

def render_statistics(pie_id, what, table, filter, dashlet):
    pie_diameter     = 130
    pie_left_aspect  = 0.5
    pie_right_aspect = 0.8

    if what == 'hosts':
        info = 'host'
        infos = [ info ]
    else:
        info = 'service'
        infos = [ 'host', 'service' ]
    use_filters = visuals.filters_of_visual(dashlet, infos)
    for filt in use_filters:
        if filt.available() and not isinstance(filt, visuals.FilterSite):
            filter += filt.filter(info)

    query = "GET %s\n" % what
    for entry in table:
        query += entry[3]
    query += filter

    site = dashlet['context'].get('siteopt', {}).get('site')
    if site:
        sites.live().set_only_sites([site])
        result = sites.live().query_row(query)
        sites.live().set_only_sites()
    else:
        result = sites.live().query_summed_stats(query)

    pies = zip(table, result)
    total = sum([x[1] for x in pies])

    html.open_div(class_="stats")
    html.canvas('', class_="pie", id_="%s_stats" % pie_id, width=pie_diameter, height=pie_diameter, style="float: left")
    html.img("images/globe.png", class_="globe")

    html.open_table(class_=["hoststats"] + (["narrow"] if len(pies) > 0 else []), style="float:left")

    table_entries = pies
    while len(table_entries) < 6:
        table_entries = table_entries + [ (("", None, "", ""), HTML("&nbsp;")) ]
    table_entries.append(((_("Total"), "", "all%s" % what, ""), total))

    for (name, color, viewurl, query), count in table_entries:
        url = "view.py?view_name=" + viewurl + "&filled_in=filter&search=1"
        for filter_name, url_params in dashlet['context'].items():
            if filter_name == "wato_folder" and html.has_var("wato_folder"):
                url += "&wato_folder=" + html.var("wato_folder")

            elif filter_name == "svcstate":
                # The svcstate filter URL vars are controlled by dashlet
                continue

            else:
                url += '&' + html.urlencode_vars(url_params.items())

        html.open_tr()
        html.th(html.render_a(name, href=url))
        html.td('', class_="color", style="background-color: %s" % color if color else '')
        html.td(html.render_a(count, href=url))
        html.close_tr()

    html.close_table()

    r = 0.0
    pie_parts = []
    if total > 0:
        # Count number of non-empty classes
        num_nonzero = 0
        for info, value in pies:
            if value > 0:
                num_nonzero += 1

        # Each non-zero class gets at least a view pixels of visible thickness.
        # We reserve that space right now. All computations are done in percent
        # of the radius.
        separator = 0.02                                    # 3% of radius
        remaining_separatorspace = num_nonzero * separator  # space for separators
        remaining_radius = 1 - remaining_separatorspace     # remaining space
        remaining_part = 1.0 # keep track of remaining part, 1.0 = 100%

        # Loop over classes, begin with most outer sphere. Inner spheres show
        # worse states and appear larger to the user (which is the reason we
        # are doing all this stuff in the first place)
        for (name, color, viewurl, q), value in pies[::1]:
            if value > 0 and remaining_part > 0: # skip empty classes

                # compute radius of this sphere *including all inner spheres!* The first
                # sphere always gets a radius of 1.0, of course.
                radius = remaining_separatorspace + remaining_radius * (remaining_part ** (1/3.0))
                pie_parts.append('chart_pie("%s", %f, %f, %r, true);' % (pie_id, pie_right_aspect, radius, color))
                pie_parts.append('chart_pie("%s", %f, %f, %r, false);' % (pie_id, pie_left_aspect, radius, color))

                # compute relative part of this class
                part = float(value) / total # ranges from 0 to 1
                remaining_part           -= part
                remaining_separatorspace -= separator

    html.close_div()

    html.javascript("""
function chart_pie(pie_id, x_scale, radius, color, right_side) {
    var context = document.getElementById(pie_id + "_stats").getContext('2d');
    if (!context)
        return;
    var pie_x = %(x)f;
    var pie_y = %(y)f;
    var pie_d = %(d)f;
    context.fillStyle = color;
    context.save();
    context.translate(pie_x, pie_y);
    context.scale(x_scale, 1);
    context.beginPath();
    if(right_side)
        context.arc(0, 0, (pie_d / 2) * radius, 1.5 * Math.PI, 0.5 * Math.PI, false);
    else
        context.arc(0, 0, (pie_d / 2) * radius, 0.5 * Math.PI, 1.5 * Math.PI, false);
    context.closePath();
    context.fill();
    context.restore();
    context = null;
}


if (has_canvas_support()) {
    %(p)s
}
""" % { "x" : pie_diameter / 2, "y": pie_diameter/2, "d" : pie_diameter, 'p': '\n'.join(pie_parts) })

#.
#   .--PNP-Graph-----------------------------------------------------------.
#   |         ____  _   _ ____        ____                 _               |
#   |        |  _ \| \ | |  _ \      / ___|_ __ __ _ _ __ | |__            |
#   |        | |_) |  \| | |_) |____| |  _| '__/ _` | '_ \| '_ \           |
#   |        |  __/| |\  |  __/_____| |_| | | | (_| | |_) | | | |          |
#   |        |_|   |_| \_|_|         \____|_|  \__,_| .__/|_| |_|          |
#   |                                               |_|                    |
#   +----------------------------------------------------------------------+
#   | Renders a single performance graph                                   |
#   '----------------------------------------------------------------------'


def dashlet_graph(nr, dashlet):
    html.div('', id_="dashlet_graph_%d" % nr)


def dashlet_graph_reload_js(nr, dashlet):
    # Be compatible to pre 1.5.0i2 format
    if "graph_render_options" not in dashlet:
        if dashlet.pop("show_service", True):
            title_format = ("add_title_infos", ["add_host_name",
                                                "add_service_description"])
        else:
            title_format = ("plain", [])

        dashlet["graph_render_options"] = {
            "show_legend"  : dashlet.pop("show_legend", False),
            "title_format" : title_format,
        }

    host = dashlet['context'].get('host', html.var("host"))
    if not host:
        raise MKUserError('host', _('Missing needed host parameter.'))

    service = dashlet['context'].get('service')
    if not service:
        service = "_HOST_"

    # When the site is available via URL context, use it. Otherwise it is needed
    # to check all sites for the requested host
    if html.has_var('site'):
        site = html.var('site')
    else:
        query = "GET hosts\nFilter: name = %s\nColumns: name" % livestatus.lqencode(host)
        try:
            sites.live().set_prepend_site(True)
            site = sites.live().query_column(query)[0]
        except IndexError:
            raise MKUserError("host", _("The host could not be found on any active site."))
        finally:
            sites.live().set_prepend_site(False)

    # New graphs which have been added via "add to visual" option don't have a timerange
    # configured. So we assume the default timerange here by default.
    timerange = dashlet.get('timerange', '1')

    graph_identification = ("template", {
        "site"                : site,
        "host_name"           : host,
        "service_description" : service,
        "graph_index"         : dashlet["source"] -1,
    })

    graph_render_options = dashlet["graph_render_options"]

    return "dashboard_render_graph(%d, %s, %s, '%s')" % \
            (nr, json.dumps(graph_identification), json.dumps(graph_render_options), timerange)


def pnpgraph_parameters():
    elements = [
        # TODO: Cleanup: switch to generic Timerange() valuespec!
        ("timerange", DropdownChoice(
            title = _('Timerange'),
            default_value = '1',
            choices= [
                ("0", _("4 Hours")),  ("1", _("25 Hours")),
                ("2", _("One Week")), ("3", _("One Month")),
                ("4", _("One Year")),
            ],
        )),
        ("source", Integer(
            title = _('Source (n\'th graph)'),
            default_value = 1,
            minvalue = 1,
        )),
    ]

    import metrics
    if metrics.cmk_graphs_possible():
        elements += [
            ("graph_render_options", metrics.vs_graph_render_options(
                default_values=metrics.default_dashlet_graph_render_options,
                exclude=[
                    "show_time_range_previews",
                ],
            )),
        ]

    return elements


dashlet_types["pnpgraph"] = {
    "title"        : _("Performance Graph"),
    "sort_index"   : 20,
    "description"  : _("Displays a performance graph of a host or service."),
    "render"       : dashlet_graph,
    "refresh"      : 60,
    "size"         : (60, 21),
    "allowed"      : config.builtin_role_ids,
    "infos"        : ["service", "host"],
    "single_infos" : ["service", "host"],
    "parameters"   : Dictionary(
        title = _('Properties'),
        render = 'form',
        optional_keys = [],
        elements = pnpgraph_parameters,
    ),
    "styles": """
.dashlet.pnpgraph .dashlet_inner {
    background-color: #f8f4f0;
    color: #000;
    text-align: center;
}
.dashlet.pnpgraph .graph {
    border: none;
    box-shadow: none;
}
.dashlet.pnpgraph .container {
    background-color: #f8f4f0;
}
.dashlet.pnpgraph div.title a {
    color: #000;
}
""",
    "on_resize"    : dashlet_graph_reload_js,
    # execute this js handler instead of refreshing the dashlet by calling "render" again
    "on_refresh"   : dashlet_graph_reload_js,
    "script": """
var dashlet_offsets = {};
function dashboard_render_graph(nr, graph_identification, graph_render_options, timerange)
{
    // Get the target size for the graph from the inner dashlet container
    var inner = document.getElementById('dashlet_inner_' + nr);
    var c_w = inner.clientWidth;
    var c_h = inner.clientHeight;

    var post_data = "spec=" + encodeURIComponent(JSON.stringify(graph_identification))
                  + "&render=" + encodeURIComponent(JSON.stringify(graph_render_options))
                  + "&timerange=" + encodeURIComponent(timerange)
                  + "&width=" + c_w
                  + "&height=" + c_h
                  + "&id=" + nr;

    call_ajax("graph_dashlet.py", {
        post_data        : post_data,
        method           : "POST",
        response_handler : handle_dashboard_render_graph_response,
        handler_data     : nr,
    });
}

function handle_dashboard_render_graph_response(handler_data, response_body)
{
    var nr = handler_data;

    // Fallback to PNP graph handling
    if (response_body.indexOf('pnp4nagios') !== -1) {
        var img_url = response_body;
        dashboard_render_pnpgraph(nr, img_url);
        return;
    }

    var container = document.getElementById('dashlet_graph_' + nr);
    container.innerHTML = response_body;
    executeJSbyObject(container);
}

function dashboard_render_pnpgraph(nr, img_url)
{
    // Get the target size for the graph from the inner dashlet container
    var inner = document.getElementById('dashlet_inner_' + nr);
    var c_w = inner.clientWidth;
    var c_h = inner.clientHeight;

    var container = document.getElementById('dashlet_graph_' + nr);
    var img = document.getElementById('dashlet_img_' + nr);
    if (!img) {
        var img = document.createElement('img');
        img.setAttribute('id', 'dashlet_img_' + nr);
        container.appendChild(img);
    }

    // This handler is called after loading the configured graph image to verify
    // it fits into the inner dashlet container.
    // One could think that it can simply be solved by requesting an image of the
    // given size from PNP/rrdtool, but this is not the case. When we request an
    // image of a specified size, this size is used for the graphing area. The
    // resulting image has normally labels which are added to the requested size.
    img.onload = function(nr, url, w, h) {
        return function() {
            var i_w = this.clientWidth;
            var i_h = this.clientHeight;

            // difference between the requested size and the real size of the image
            var x_diff = i_w - w;
            var y_diff = i_h - h;

            if (Math.abs(x_diff) < 10 && Math.abs(y_diff) < 10) {
                return; // Finished resizing
            }

            // When the target height is smaller or equal to 81 pixels, PNP
            // returns an image which has no labels, just the graph, which has
            // exactly the requested height. In this situation no further resizing
            // is needed.
            if (h <= 81 || h - y_diff <= 81) {
                this.style.width = '100%';
                this.style.height = '100%';
                return;
            }

            // Save the sizing differences between the requested size and the
            // resulting size. This is, in fact, the size of the graph labels.
            // load_graph_img() uses these dimensions to try to get an image
            // which really fits the requested dimensions.
            if (typeof dashlet_offsets[nr] == 'undefined') {
                dashlet_offsets[nr] = [x_diff, y_diff];
            } else if (dashlet_offsets[nr][0] != x_diff || dashlet_offsets[nr][1] != y_diff) {
                // was not successful in getting a correctly sized image. Seems
                // that PNP/rrdtool was not able to render this size. Terminate
                // and automatically scale to 100%/100%
                this.style.width = '100%';
                this.style.height = '100%';
                return;
            }

            load_graph_img(nr, this, url, w, h);
        };
    }(nr, img_url, c_w, c_h);

    img.style.width = 'auto';
    img.style.height = 'auto';
    load_graph_img(nr, img, img_url, c_w, c_h);
}

function load_graph_img(nr, img, img_url, c_w, c_h)
{
    if (typeof dashlet_offsets[nr] == 'undefined'
        || (c_h > 1 && c_h - dashlet_offsets[nr][1] < 81)) {
        // use this on first load and later when the graph is less high than 81px
        img_url += '&graph_width='+c_w+'&graph_height='+c_h;
    } else {
        img_url += '&graph_width='+(c_w - dashlet_offsets[nr][0])
                  +'&graph_height='+(c_h - dashlet_offsets[nr][1]);
    }
    img_url += '&_t='+Math.floor(Date.parse(new Date()) / 1000); // prevent caching
    img.src = img_url;
}
"""
}

#.
#   .--nodata--------------------------------------------------------------.
#   |                                  _       _                           |
#   |                  _ __   ___   __| | __ _| |_ __ _                    |
#   |                 | '_ \ / _ \ / _` |/ _` | __/ _` |                   |
#   |                 | | | | (_) | (_| | (_| | || (_| |                   |
#   |                 |_| |_|\___/ \__,_|\__,_|\__\__,_|                   |
#   |                                                                      |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'

def dashlet_nodata(nr, dashlet):
    html.open_div(class_="nodata")
    html.open_div(class_="msg")
    html.write(dashlet.get("text"))
    html.close_div()
    html.close_div()

dashlet_types["nodata"] = {
    "title"       : _("Static text"),
    "sort_index"     : 100,
    "description" : _("Displays a static text to the user."),
    "render"      : dashlet_nodata,
    "allowed"     : config.builtin_role_ids,
    "parameters"  : [
        ("text", TextUnicode(
            title = _('Text'),
            size = 50,
        )),
    ],
    "styles"      : """
div.dashlet_inner div.nodata {
    width: 100%;
    height: 100%;
}

div.dashlet_inner.background div.nodata div.msg {
    color: #000;
}

div.dashlet_inner div.nodata div.msg {
    padding: 10px;
}

}""",
}

#.
#   .--View----------------------------------------------------------------.
#   |                      __     ___                                      |
#   |                      \ \   / (_) _____      __                       |
#   |                       \ \ / /| |/ _ \ \ /\ / /                       |
#   |                        \ V / | |  __/\ V  V /                        |
#   |                         \_/  |_|\___| \_/\_/                         |
#   |                                                                      |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'

def dashlet_view(nr, dashlet):
    import bi # FIXME: Cleanup?
    bi.reset_cache_status() # needed for status icon

    is_reload = html.has_var("_reload")

    display_options = "SIXLW"
    if not is_reload:
        display_options += "HR"

    html.set_var('display_options',  display_options)
    html.set_var('_display_options', display_options)
    html.add_body_css_class('dashlet')

    import views # FIXME: HACK, clean this up somehow
    views.load_views()
    views.prepare_painter_options()
    views.show_view(dashlet, True, True, True)

def dashlet_view_add_url():
    return 'create_view_dashlet.py?name=%s&back=%s' % \
        (html.urlencode(html.var('name')), html.urlencode(html.makeuri([('edit', '1')])))

def dashlet_view_parameters():
    return dashlet_view_render_input, dashlet_view_handle_input

def dashlet_view_render_input(dashlet):
    import views # FIXME: HACK, clean this up somehow
    views.load_views()
    views.transform_view_to_valuespec_value(dashlet)
    return views.render_view_config(dashlet)

def dashlet_view_handle_input(ident, dashlet):
    dashlet['name'] = 'dashlet_%d' % ident
    dashlet.setdefault('title', _('View'))
    import views # FIXME: HACK, clean this up somehow
    views.load_views()
    return views.create_view_from_valuespec(dashlet, dashlet)

dashlet_types["view"] = {
    "title"          : _("View"),
    "sort_index"     : 10,
    "description"    : _("Displays the content of a Multisite view."),
    "size"           : (40, 20),
    "iframe_render"  : dashlet_view,
    "allowed"        : config.builtin_role_ids,
    "add_urlfunc"    : dashlet_view_add_url,
    "parameters"     : dashlet_view_parameters,
}

#.
#   .--Custom URL----------------------------------------------------------.
#   |         ____          _                    _   _ ____  _             |
#   |        / ___|   _ ___| |_ ___  _ __ ___   | | | |  _ \| |            |
#   |       | |  | | | / __| __/ _ \| '_ ` _ \  | | | | |_) | |            |
#   |       | |__| |_| \__ \ || (_) | | | | | | | |_| |  _ <| |___         |
#   |        \____\__,_|___/\__\___/|_| |_| |_|  \___/|_| \_\_____|        |
#   |                                                                      |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'

def dashlet_url(dashlet):
    if dashlet.get('show_in_iframe', True):
        try:
            return dashlet['url']
        except KeyError:
            if "urlfunc" in dashlet:
                raise MKUserError(None,
                    _("You set the dashlet to use a dynamic URL rendering function. It seems "
                      "that this function call failed. You may want to open the dashboard "
                      "in debug mode to get more details."))
            else:
                raise

def dashlet_url_validate(value, varprefix):
    if 'url' not in value and 'urlfunc' not in value:
        raise MKUserError(varprefix, _('You need to provide either an URL or '
                                       'the name of a python function to be used '
                                       'for rendering the dashlet.'))

dashlet_types["url"] = {
    "title"          : _("Custom URL"),
    "sort_index"     : 80,
    "description"    : _("Displays the content of a custom website."),
    "iframe_urlfunc" : dashlet_url,
    "allowed"        : config.builtin_role_ids,
    "size"           : (30, 10),
    "parameters"     : [
        ("url", TextAscii(
            title = _('URL'),
            size = 50,
            allow_empty = False,
        )),
        ("urlfunc", TextAscii(
            title = _('Dynamic URL rendering function'),
            size = 50,
            allow_empty = False,
        )),
        ("show_in_iframe", Checkbox(
            title = _('Render in iframe'),
            label = _('Render URL contents in own frame'),
            default_value = True,
        )),
    ],
    "opt_params"      : ['url', 'urlfunc'],
    "validate_params" : dashlet_url_validate,
}

#.
#   .--Snapin--------------------------------------------------------------.
#   |                   ____                    _                          |
#   |                  / ___| _ __   __ _ _ __ (_)_ __                     |
#   |                  \___ \| '_ \ / _` | '_ \| | '_ \                    |
#   |                   ___) | | | | (_| | |_) | | | | |                   |
#   |                  |____/|_| |_|\__,_| .__/|_|_| |_|                   |
#   |                                    |_|                               |
#   +----------------------------------------------------------------------+
#   | Render sidebar snapins within the dashboard                          |
#   '----------------------------------------------------------------------'

def dashlet_snapin(nr, dashlet):
    import sidebar # FIXME: HACK, clean this up somehow
    snapin = sidebar.sidebar_snapins.get(dashlet['snapin'])
    if not snapin:
        raise MKUserError(None, _('The configured snapin does not exist.'))

    dashlet_type = dashlet_types[dashlet['type']]

    overflow = ''
    scroll_x, scroll_y = dashlet_type.get("iframe_scroll", (False, False))
    if not scroll_x:
        overflow += 'overflow-x: hidden;\n'
    else:
        overflow += 'overflow-x: auto;\n'
    if not scroll_y:
        overflow += 'overflow-y: hidden;\n'
    else:
        overflow += 'overflow-y: auto;\n'

    html.set_browser_reload(dashlet_type['refresh'])
    html.html_head(_('Snapin Dashlet'), javascripts=['sidebar'], stylesheets=['sidebar', 'status'])
    html.style(''' #side_content {
                        height: auto;
                        top: 0;
                        padding-top: 4px;
                        padding-left: 4px;
                    }
                    div.snapin:last-child {
                        margin-bottom: 0;
                    }
                    div.snapin div.content {
                        background-image: none;
                        background-color: #508AA1;
                    }
                    div.snapin {
                        margin: 0;
                        padding: 0;
                    }
                    body.side {
                        %s
                    }''' % overflow)
    html.open_body(class_="side")
    html.open_div(id_="check_mk_sidebar")
    html.open_div(id_="side_content")
    html.open_div(id_="snapin_container_%s" % dashlet['snapin'], class_="snapin")
    html.open_div(id_="snapin_%s" % dashlet['snapin'], class_="content")
    sidebar.render_snapin_styles(snapin)
    snapin.show()
    html.close_div()
    html.close_div()
    html.close_div()
    html.close_div()
    html.body_end()


def dashlet_snapin_get_snapins():
    import sidebar # FIXME: HACK, clean this up somehow
    return sorted([ (k, v.title()) for k, v in sidebar.sidebar_snapins.items() ],
                    key=lambda x: x[1])


def dashlet_snapin_title(dashlet):
    import sidebar # FIXME: HACK, clean this up somehow
    return sidebar.sidebar_snapins[dashlet['snapin']].title()


dashlet_types["snapin"] = {
    "title"          : _("Sidebar Snapin"),
    "title_func"     : dashlet_snapin_title,
    "sort_index"     : 55,
    "description"    : _("Displays a sidebar snapin."),
    "size"           : (27, 20),
    "iframe_render"  : dashlet_snapin,
    "iframe_scroll"  : (False, True),
    "allowed"        : config.builtin_role_ids,
    "refresh"        : 30,
    "parameters"     : [
        ('snapin', DropdownChoice(
            title = _('Snapin'),
            help = _('Choose the snapin you would like to show.'),
            choices = dashlet_snapin_get_snapins,
        )),
    ],
}


#.
#   .--Notify users--------------------------------------------------------.
#   |        _   _       _   _  __                                         |
#   |       | \ | | ___ | |_(_)/ _|_   _   _   _ ___  ___ _ __ ___         |
#   |       |  \| |/ _ \| __| | |_| | | | | | | / __|/ _ \ '__/ __|        |
#   |       | |\  | (_) | |_| |  _| |_| | | |_| \__ \  __/ |  \__ \        |
#   |       |_| \_|\___/ \__|_|_|  \__, |  \__,_|___/\___|_|  |___/        |
#   |                              |___/                                   |
#   +----------------------------------------------------------------------+
#   | Dashlet for notify user pop up messages                              |
#   '----------------------------------------------------------------------'


def ajax_delete_user_notification():
    msg_id = html.var("id")
    notify.delete_gui_message(msg_id)


def dashlet_notify_users(nr, dashlet):

    html.open_div(class_="notify_users")
    table.begin("notify_users", sortable=False, searchable=False, omit_if_empty=True)



    for entry in sorted(notify.get_gui_messages(), key=lambda e: e["time"], reverse=True):
        if "dashlet" in entry["methods"]:
            table.row()

            msg_id   = entry["id"]
            datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry['time']))
            message  = entry["text"].replace("\n", " ")

            table.cell(_("Actions"), css="buttons", sortable=False)
            html.icon_button("", _("Delete"), "delete", onclick="delete_user_notification('%s', this);" % msg_id)

            table.cell(_("Message"), html.render_text(message))
            table.cell(_("Date"),    datetime)

    table.end()
    html.javascript('function delete_user_notification(msg_id, btn) {'
               'post_url("ajax_delete_user_notification.py", "id=" + msg_id);'
               'var row = btn.parentNode.parentNode;'
               'row.parentNode.removeChild(row);}')

    html.close_div()

dashlet_types["notify_users"] = {
    "title"       : _("User notifications"),
    "description" : _("Display GUI notifications sent to users."),
    "render"      : dashlet_notify_users,
    "sort_index"  : 75,
    "allowed"     : config.builtin_role_ids,
    "styles"      : ".notify_users { width: 100%; height: 100%; overflow: auto; }"
}


#.
#   .--Failed Notifications------------------------------------------------.
#   |                      _____     _ _          _                        |
#   |                     |  ___|_ _(_) | ___  __| |                       |
#   |                     | |_ / _` | | |/ _ \/ _` |                       |
#   |                     |  _| (_| | | |  __/ (_| |                       |
#   |                     |_|  \__,_|_|_|\___|\__,_|                       |
#   |                                                                      |
#   |       _   _       _   _  __ _           _   _                        |
#   |      | \ | | ___ | |_(_)/ _(_) ___ __ _| |_(_) ___  _ __  ___        |
#   |      |  \| |/ _ \| __| | |_| |/ __/ _` | __| |/ _ \| '_ \/ __|       |
#   |      | |\  | (_) | |_| |  _| | (_| (_| | |_| | (_) | | | \__ \       |
#   |      |_| \_|\___/ \__|_|_| |_|\___\__,_|\__|_|\___/|_| |_|___/       |
#   |                                                                      |
#   +----------------------------------------------------------------------+
#   | Dashlet notifying users in case of failure to send notifications     |
#   '----------------------------------------------------------------------'

def dashlet_failed_notifications(nr, dashlet):
    notdata = notifications.load_failed_notifications(after=notifications.acknowledged_time(),
                                                      stat_only=True)

    if notdata is None:
        failed_notifications = 0
    else:
        failed_notifications = notdata[0]

    if failed_notifications > 0:
        view_url = html.makeuri_contextless(
            [("view_name", "failed_notifications")], filename="view.py")
        content = '<a target="main" href="%s">%d failed notifications</a>' %\
            (view_url, failed_notifications)

        confirm_url = html.makeuri_contextless([], filename="clear_failed_notifications.py")
        content = ('<a target="main" href="%s">'
                    '<img src="images/button_closetimewarp.png" style="width:32px;height:32px;">'
                    '</a>&nbsp;' % confirm_url) + content

        html.open_div(class_="has_failed_notifications")
        html.open_div(class_="failed_notifications_inner")
        html.write(content)
        html.close_div()
        html.close_div()


dashlet_types["notify_failed_notifications"] = {
    "title"       : _("Failed Notifications"),
    "description" : _("Display GUI notifications in case notification mechanism fails"),
    "render"      : dashlet_failed_notifications,
    "sort_index"  : 0,
    "refresh"     : 60,
    "selectable"  : False,
    "styles"      : """
.has_failed_notifications {
    width: 100%;
    height: 100%;
    overflow: auto;
    font-weight: bold;
    font-size: 14pt;

    text-align: center;
    background-color: #ff5500;
}
.failed_notifications_inner {
    display:inline-block;
    margin: auto;
    position: absolute;
    top:0; bottom:0; left:0; right:0;
    height:32px;
}
    """
}
