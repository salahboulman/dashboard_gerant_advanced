from odoo import models, fields

class DashboardMasarif(models.Model):
    _name = 'dashboard.masarif'
    _description = 'Gestion des Masarif (Dépenses)'
    _order = 'date desc, id desc'

    name = fields.Char(string='Motif / Description', required=True)
    amount = fields.Float(string='Montant (DH)', required=True)
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    user_id = fields.Many2one('res.users', string='Enregistré par', default=lambda self: self.env.user)