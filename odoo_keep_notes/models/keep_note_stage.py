from odoo import models, fields

class KeepNoteStage(models.Model):
    _name = 'keep.note.stage'
    _description = 'Keep Note Stage'
    _order = 'sequence, id'

    name = fields.Char(string='Stage Name', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    fold = fields.Boolean(string='Folded in Kanban', default=False)
    active = fields.Boolean(string='Active', default=True)
