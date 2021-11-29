# -*- coding: utf-8 -*-
# copyright by gCoded - Sebastian Graup IT Consulting & Software Development

from collections import OrderedDict
from odoo import http, fields
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.osv.expression import OR, AND
from odoo.addons.helpdesk.controllers.portal import CustomerPortal
from odoo.addons.website_helpdesk.controllers.main import WebsiteHelpdesk
from odoo.addons.website_helpdesk_form.controller.main import WebsiteForm


class HelpdeskGabPortalController(CustomerPortal):
    
    # TODO filter for user?!
    @http.route()
    def my_helpdesk_tickets(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, groupby=None, search=None, search_in='content', **kw):
        values = self._prepare_portal_layout_values()
        
        #customer_team_id = request.env.user.parent_id.helpdesk_team_id.id
        #if customer_team_id is False:
            #return request.render("helpdesk.portal_helpdesk_ticket", values) # TODO nicer values!

        domain = []

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
            'id': {'label': _('Ref'), 'order': 'id'},
            'state': {'label': _('Status'), 'order': 'stage_id'},
            'type': {'label': _('Type'), 'order': 'ticket_type_id'},
            'prio': {'label': _('Priority Level'), 'order': 'priority'},
            #'team': {'label': _('Team'), 'order': 'team_id'}
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Content)</span>')}
            # 'message': {'input': 'message', 'label': _('Search in Messages')},
            # 'customer': {'input': 'customer', 'label': _('Search in Customer')},
            # 'id': {'input': 'id', 'label': _('Search ID')},
            # 'all': {'input': 'all', 'label': _('Search in All')}
        }        
        ticket_stages = request.env['helpdesk.stage'].search([], order='name asc')
        ticket_types = request.env['helpdesk.ticket.type'].search([], order='name asc')
        #if customer_team_id is False:
            #ticket_slas = request.env['helpdesk.sla'].search([('active', '=', True)], order='name asc')
            #ticket_teams = request.env['helpdesk.team'].search([('active', '=', True)], order='name asc')
        #else: #  TODO not for admins/users?!
            #ticket_slas = request.env['helpdesk.sla'].search([('active', '=', True), ('team_id', '=', customer_team_id)], order='name asc')
            #ticket_teams = request.env['helpdesk.team'].search([('active', '=', True), ('id', '=', customer_team_id)], order='name asc')
        searchbar_filters = {
            'all': {'label': _('No Filter'), 'domain': []}
        }
        for t_stage in ticket_stages:
            searchbar_filters['stage_' + str(t_stage.id)] = {'label': _('Stage - ') + t_stage.name, 'domain': [("stage_id", "=", t_stage.id)]}
        for t_type in ticket_types:
            searchbar_filters['type_' + str(t_type.id)] = {'label': _('Type - ') + t_type.name, 'domain': [("ticket_type_id", "=", t_type.id)]}
        # for t_sla in ticket_slas:
        #     searchbar_filters['sla_' + str(t_sla.id)] = {'label': _('Priority Level - ') + t_sla.name, 'domain': [("sla_id", "=", t_sla.id)]}
        # # for t_team in ticket_teams:
        #     searchbar_filters['team_' + str(t_team.id)] = {'label': _('Team - ') + t_team.name, 'domain': [("team_id", "=", t_team.id)]}
        for prio in [0, 1, 2, 3]: #  TODO config etc.
            searchbar_filters['prio_' + str(prio)] = {'label': _('Priority Level - ') + str(prio), 'domain': [("priority", "=", prio)]}

        searchbar_groupby = {
            'all': {'label': _('None'), 'domain': []},
            'own': {'label': _('Own'), 'domain': [('partner_id', '=', request.env.user.partner_id.id)]}
        }

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if not groupby:
            groupby = 'own'
        domain += searchbar_groupby[groupby]['domain']

        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups('helpdesk.ticket', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('id', 'all'):
                search_domain = OR([search_domain, [('id', 'ilike', search)]])
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            if search_in in ('customer', 'all'):
                search_domain = OR([search_domain, [('partner_id', 'ilike', search)]])
            if search_in in ('message', 'all'):
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search)]])
            domain += search_domain

        # TODO only own tickets if not admin!?
        # TODO check heldesk rights
        # TODO check customer portal access, not real user
        # TODO do nothing at the moment, keep it as it is

        # pager
        tickets_count = request.env['helpdesk.ticket'].search_count(domain)
        pager = portal_pager(
            url="/my/tickets",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby, 'groupby': groupby},
            total=tickets_count,
            page=page,
            step=self._items_per_page
        )

        tickets = request.env['helpdesk.ticket'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_tickets_history'] = tickets.ids[:100]

        values.update({
            'date': date_begin,
            'tickets': tickets,
            'page_name': 'ticket',
            'default_url': '/my/tickets',
            'pager': pager,
            'archive_groups': archive_groups,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'sortby': sortby,
            'search_in': search_in,
            'search': search,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'searchbar_groupby': OrderedDict(sorted(searchbar_groupby.items())),
            'filterby': filterby,
            'groupby': groupby
        })
        return request.render("helpdesk.portal_helpdesk_ticket", values)


class HelpdeskGabPortalWebsiteController(WebsiteHelpdesk):

    @http.route()
    def website_helpdesk_teams(self, team=None, **kwargs):
        search = kwargs.get('search')
        # For breadcrumb index: get all team
        teams = request.env['helpdesk.team'].search(['|', '|', ('use_website_helpdesk_form', '=', True), ('use_website_helpdesk_forum', '=', True), ('use_website_helpdesk_slides', '=', True)], order="id asc")
        if not request.env.user.has_group('helpdesk.group_helpdesk_manager'):
            teams = teams.filtered(lambda team: team.website_published)
            customer_team_id = request.env.user.parent_id.helpdesk_team_id.id
            if customer_team_id: #  TODO keep all if not set is OK?!
                teams = teams.filtered(lambda team: team.id == customer_team_id)
        if not teams:
            return request.render("website_helpdesk.not_published_any_team")
        result = self.get_helpdesk_team_data(team or teams[0], search=search)
        # For breadcrumb index: get all team
        result['teams'] = teams
        return request.render("website_helpdesk.team", result)


class HelpdeskGabPortalWebsiteFormController(WebsiteForm):

    @http.route()
    def website_helpdesk_form(self, team, **kwargs):
        if not team.active or not team.website_published:
            return request.render("website_helpdesk.not_published_any_team")
        default_values = {}
        if request.env.user.partner_id != request.env.ref('base.public_partner'):
            default_values['name'] = request.env.user.partner_id.name
            default_values['email'] = request.env.user.partner_id.email
        if 'ticket_type_id' in request.params:
            default_values['ticket_type_id'] = int(request.params['ticket_type_id'])
        return request.render("website_helpdesk_form.ticket_submit", {'team': team, 'default_values': default_values})
