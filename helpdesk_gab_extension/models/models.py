# -*- coding: utf-8 -*-
# copyright by gCoded - Sebastian Graup IT Consulting & Software Development

from datetime import datetime
from odoo import models, fields, api

class history(models.Model):
    _name = 'helpdesk_gab_extension.history'
    _description = 'Helpdesk GAB Extension History'
    _order = 'id desc'

    # @api.depends(
    #     'overtime_hours',
    #     'working_time'
    # )
    # def _compute_consumed_time(self):
    #     for rec in self:
    #         rec.consumed_time = rec.overtime_hours + rec.working_time

    # @api.depends(
    #     'consumed_time',
    #     'estimate_time'
    # )
    # def _compute_delay_time(self):
    #     for line in self:
    #         if line.consumed_time > 0.0 and line.estimate_time > 0.0:
    #             line.delay_time = line.consumed_time - line.estimate_time

    # @api.depends(
    #     'start_time',
    #     'end_time'
    # )
    # def _compute_working_time(self):
    #     for line in self:
    #         if line.start_time and line.end_time:
    #             start_time = datetime.strptime(str(line.start_time), '%Y-%m-%d %H:%M:%S')
    #             end_time = datetime.strptime(str(line.end_time), '%Y-%m-%d %H:%M:%S')
    #             if line.calendar_id:
    #                 consumed_hours = line.calendar_id.get_work_hours_count(
    #                     start_time,
    #                     end_time,
    #                     compute_leaves=True)
    #                 line.working_time = consumed_hours

    helpdesk_ticket_id = fields.Many2one(
        'helpdesk.ticket',
        string="Support Ticket",
        ondelete="set null", # TODO
    )
    stage_id = fields.Many2one(
        'helpdesk.stage',
        string="Source Stage",
        required=False,
        ondelete="set null", # TODO
    )
    dest_stage_id = fields.Many2one(
        'helpdesk.stage',
        string="Stage",
        required=False,
        ondelete="set null", # TODO
    )
    start_time = fields.Datetime(
        string="Start At",
    )
    end_time = fields.Datetime(
        string="Done At",
    )
    user_id = fields.Many2one(
        'res.users',
        string="Responsible User",
        ondelete="set null", # TODO
    )
    team_id = fields.Many2one(
        'helpdesk.team',
        string="Team",
        ondelete="set null", # TODO
    )
    calendar_id = fields.Many2one(
        'resource.calendar',
        'Resource Calendar',
        required=False,
        ondelete="set null", # TODO
    )

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        return super(history, self).search(args, offset=offset, limit=limit, order='id asc', count=count)


class ticket_override(models.Model):
    _inherit = 'helpdesk.ticket'

    history_ids = fields.One2many(comodel_name='helpdesk_gab_extension.history', inverse_name='helpdesk_ticket_id')

    sla2_id = fields.Many2one('helpdesk.sla', string='Response SLA Policy', compute='_compute_sla2', store=True)
    sla2_name = fields.Char(string='Response SLA Policy name', compute='_compute_sla2', store=True)  # care if related -> crash on creation with a team.
    deadline2 = fields.Datetime(string='Response Deadline', compute='_compute_sla2', store=True)
    sla2_active = fields.Boolean(string='Response SLA active', compute='_compute_sla_fail2', store=True)
    sla2_fail = fields.Boolean(string='Response Failed SLA Policy', compute='_compute_sla_fail2', store=True)

    # @api.model
    # def recompute_all(self):
    #     #super().recompute_all()

    #     tickets = self.search([('stage_id.is_close', '=', False)])

    #     # original deadline handling (resolution time deadline, whole ticket, every stage, backend shows connected sla only on NEW stage!?)
    #     tickets._compute_sla()
    #     # deadline2 handling (response time deadline, NEW stage only)
    #     tickets._compute_sla2()

    #     tickets._compute_close_hours()
    #     return True

    @api.depends('team_id', 'priority', 'ticket_type_id', 'create_date')
    def _compute_sla2(self):
        if not self.user_has_groups("helpdesk.group_use_sla"):
            return
        for ticket in self:
            # TODO active=True, also in _compute_sla()?!
            # TODO response SLAs, in _compute_sla() restrict resolutions SLAs, too!?
            dom = [('name', 'ilike', 'Ticket Response%'), ('stage_id', '=', 1), ('team_id', '=', ticket.team_id.id), ('priority', '<=', ticket.priority), '|', ('ticket_type_id', '=', ticket.ticket_type_id.id), ('ticket_type_id', '=', False)]
            sla2 = ticket.env['helpdesk.sla'].search(dom, order="time_days, time_hours", limit=1)
            working_calendar = ticket.team_id.resource_calendar_id
            if sla2 and ticket.sla2_id != sla2 and ticket.active and ticket.create_date:
                ticket.sla2_id = sla2.id
                ticket.sla2_name = sla2.name
                ticket_create_date = fields.Datetime.from_string(ticket.create_date)
                if sla2.time_days > 0:
                    deadline2 = working_calendar.plan_days(
                        sla2.time_days+1,
                        ticket_create_date,
                        compute_leaves=True)
                    # We should also depend on ticket creation time, otherwise for 1 day SLA for example all tickets
                    # created on monday will have the deadline as tuesday 8:00
                    deadline2 = deadline2.replace(hour=ticket_create_date.hour, minute=ticket_create_date.minute, second=ticket_create_date.second, microsecond=ticket_create_date.microsecond)
                    # Except if ticket creation time is later than the end time of the working day
                    deadline2_for_working_cal = working_calendar.plan_hours(0, deadline2)
                    if deadline2_for_working_cal and deadline2.day < deadline2_for_working_cal.day:
                        deadline2 = deadline2.replace(hour=0, minute=0, second=0, microsecond=0)
                else:
                    deadline2 = ticket_create_date
                # We should execute the function plan_hours in any case because
                # if i create a ticket for 1 day sla configuration and tomorrow at the same time i don't work,
                # deadline falls on the time that i don't work which is ticket creation time and is not correct
                ticket.deadline2 = working_calendar.plan_hours(
                    sla2.time_hours,
                    deadline2,
                    compute_leaves=True)

    @api.depends('deadline2', 'stage_id.sequence', 'sla2_id.stage_id.sequence')
    def _compute_sla_fail2(self):
        if not self.user_has_groups("helpdesk.group_use_sla"):
            return
        for ticket in self:
            ticket.sla2_active = True
            if not ticket.deadline2:
                ticket.sla2_active = False
                ticket.sla2_fail = False
            elif ticket.sla2_id.stage_id.sequence <= ticket.stage_id.sequence:
                ticket.sla2_active = False
                prev_stage_ids = self.env['helpdesk.stage'].search([('sequence', '<', ticket.sla2_id.stage_id.sequence)])
                next_stage_ids = self.env['helpdesk.stage'].search([('sequence', '>=', ticket.sla2_id.stage_id.sequence)])
                stage_id_tracking_value = self.env['mail.tracking.value'].sudo().search([('field', '=', 'stage_id'),
                                                                                  ('old_value_integer', 'in', prev_stage_ids.ids),
                                                                                  ('new_value_integer', 'in', next_stage_ids.ids),
                                                                                  ('mail_message_id.model', '=', 'helpdesk.ticket'),
                                                                                  ('mail_message_id.res_id', '=', ticket.id)], order='create_date ASC', limit=1)

                if stage_id_tracking_value:
                    if stage_id_tracking_value.create_date > ticket.deadline2:
                        ticket.sla2_fail = True
                # If there are no tracking messages, it means we *just* (now!) changed the state
                elif fields.Datetime.now() > ticket.deadline2:
                    ticket.sla2_fail = True

    @api.model
    def create(self, vals):
        res = super().create(vals)

        hist = self.env['helpdesk_gab_extension.history']
        hist_vals = {
            'helpdesk_ticket_id': res.id,
            'stage_id': res.stage_id.id,
            'dest_stage_id': res.stage_id.id,
            'start_time': fields.Datetime.now(),
            'user_id': res.user_id.id,
            'team_id': res.team_id.id,
            'calendar_id': res.team_id.resource_calendar_id.id
        }
        hist.create(hist_vals)

        return res

    def write(self, vals):
        old_stage_id = self.stage_id.id
        
        res = super().write(vals)

        # TODO on other changes, too?!
        if 'stage_id' in vals:
            prev_hist = self.env['helpdesk_gab_extension.history'].search([('helpdesk_ticket_id', '=', self.id),
                            ('dest_stage_id', '=', old_stage_id), ('end_time', '=', False)], order='id desc', limit=1)
            prev_hist.write({'end_time': datetime.now()})

            #if prev_hist is False:
                # TODO show error!?

            hist = self.env['helpdesk_gab_extension.history']
            hist_vals = {
                'helpdesk_ticket_id': self.id,
                'stage_id': old_stage_id,
                'dest_stage_id': self.stage_id.id,
                'start_time': fields.Datetime.now(),
                'user_id': self.user_id.id,
                'team_id': self.team_id.id,
                'calendar_id': self.team_id.resource_calendar_id.id
            }
            hist.create(hist_vals)

        return res

    def unlink(self):
        self.env['helpdesk_gab_extension.history'].search([('helpdesk_ticket_id', '=', self.id)]).unlink()
        return super().unlink()
        # TODO only admin is allowed to delete (all), not manager is allowed to delete


class customer_override(models.Model):
    _inherit = 'res.partner'

    helpdesk_team_id = fields.Many2one(
        'helpdesk.team',
        string="Helpdesk Team",
    )


class team_override(models.Model):
    _inherit = 'helpdesk.team'

    def get_ticket_types(self):
        return self.env['helpdesk.ticket.type'].search([], order='name asc')
