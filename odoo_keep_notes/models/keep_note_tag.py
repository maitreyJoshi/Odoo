from odoo import models, fields

class KeepNoteTag(models.Model):
    _name = 'keep.note.tag'
    _description = 'Keep Note Label'

    name = fields.Char(string='Label Name', required=True)
    color = fields.Integer(string='Color Index', default=10)
    user_id = fields.Many2one('res.users', string='Owner', default=lambda self: self.env.user, required=True)

    _sql_constraints = [
        ('name_user_uniq', 'unique (name, user_id)', 'Label name already exists for this user!'),
    ]
