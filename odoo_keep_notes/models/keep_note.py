from odoo import models, fields, api
from odoo.exceptions import ValidationError

class KeepNote(models.Model):
    _name = 'keep.note'
    _description = 'Keep Note'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'is_pinned desc, id desc'

    name = fields.Char(string='Title', required=True)
    description = fields.Html(string='Note Content', sanitize=True)
    color = fields.Integer(string='Color Index', default=0)
    tag_ids = fields.Many2many('keep.note.tag', string='Labels')
    is_pinned = fields.Boolean(string='Pinned', default=False)
    active = fields.Boolean(string='Active', default=True)
    is_trashed = fields.Boolean(string='Trashed', default=False)
    reminder_date = fields.Datetime(string='Reminder')
    cover_image = fields.Image(string='Cover Image')
    user_id = fields.Many2one('res.users', string='Owner', default=lambda self: self.env.user, required=True, tracking=True)
    stage_id = fields.Many2one('keep.note.stage', string='Stage', ondelete='restrict', tracking=True,
                               group_expand='_read_group_stage_ids',
                               default=lambda self: self._default_stage_id())

    @api.model
    def _default_stage_id(self):
        self.env.cr.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE tablename='keep_note_stage')")
        if self.env.cr.fetchone()[0]:
            return self.env['keep.note.stage'].search([], limit=1).id
        return False

    @api.model
    def _read_group_stage_ids(self, stages, domain, order=None):
        return self.env['keep.note.stage'].search([])

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or not str(vals.get('name')).strip():
                raise ValidationError("Title is required and cannot be empty!")
        records = super().create(vals_list)
        for record in records:
            if record.reminder_date:
                record._create_reminder_activity()
        return records

    def write(self, vals):
        res = super().write(vals)
        if 'reminder_date' in vals:
            for record in self:
                if record.reminder_date:
                    record._update_reminder_activity()
                else:
                    record._remove_reminder_activity()
        return res

    def action_toggle_pinned(self):
        for record in self:
            record.is_pinned = not record.is_pinned

    def _get_reminder_activity_type(self):
        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        if not activity_type:
            activity_type = self.env['mail.activity.type'].search([('category', '=', 'todo')], limit=1)
        return activity_type

    def _create_reminder_activity(self):
        self.ensure_one()
        activity_type = self._get_reminder_activity_type()
        self.env['mail.activity'].create({
            'activity_type_id': activity_type.id if activity_type else False,
            'note': self.description or '',
            'summary': f"Reminder: {self.name}",
            'date_deadline': self.reminder_date.date(),
            'user_id': self.user_id.id or self.env.user.id,
            'res_id': self.id,
            'res_model_id': self.env['ir.model']._get(self._name).id,
        })

    def _update_reminder_activity(self):
        self.ensure_one()
        activity_type = self._get_reminder_activity_type()
        activity = self.env['mail.activity'].search([
            ('res_model', '=', self._name),
            ('res_id', '=', self.id),
            ('activity_type_id', '=', activity_type.id if activity_type else False)
        ], limit=1)
        
        if activity:
            activity.write({
                'date_deadline': self.reminder_date.date(),
                'summary': f"Reminder: {self.name}",
                'note': self.description or '',
            })
        else:
            self._create_reminder_activity()

    def _remove_reminder_activity(self):
        self.ensure_one()
        activity_type = self._get_reminder_activity_type()
        activity = self.env['mail.activity'].search([
            ('res_model', '=', self._name),
            ('res_id', '=', self.id),
            ('activity_type_id', '=', activity_type.id if activity_type else False)
        ])
        if activity:
            activity.unlink()
