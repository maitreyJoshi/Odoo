from odoo import models, fields, api

class KeepNoteTodo(models.Model):
    _name = 'keep.note.todo'
    _description = 'Keep Note To-do Item'
    _order = 'sequence, id'

    name = fields.Char(string='Item', required=True)
    is_done = fields.Boolean(string='Done', default=False)
    sequence = fields.Integer(string='Sequence', default=10)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    note_id = fields.Many2one('keep.note', string='Note', ondelete='cascade', required=True)
