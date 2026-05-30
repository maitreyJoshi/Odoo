{
    'name': 'Odoo Keep Notes',
    'version': '19.0.1.0.0',
    'summary': 'Google Keep like notes application for Odoo 19',
    'description': """
        Odoo Keep Notes
        ===============
        Create and manage notes just like Google Keep.
        Features:
        - Kanban view with colors
        - Pinned notes
        - Tags and labels
        - Archive notes
    """,
    'author': 'Mj',
    'website': '',
    'category': 'Productivity',
    'depends': ['base', 'mail'],
    'data': [
        'security/keep_note_security.xml',
        'security/ir.model.access.csv',
        'data/keep_note_stage_data.xml',
        'data/keep_note_mail_template.xml',
        'views/keep_note_views.xml',
        'views/keep_note_tag_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'odoo_keep_notes/static/src/keep_note_fab.js',
        ],
    },
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
    # 'license': 'OPL-1',
    # 'price': 5.99,
    # 'currency': 'USD',
    'images': ['static/description/banner.png'],
}
