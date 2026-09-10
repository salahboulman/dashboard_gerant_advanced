import urllib.parse
from odoo import http, fields
from odoo.http import request

class GerantDashboardController(http.Controller):

    @http.route('/gerant', type='http', auth='user', website=False)
    def gerant_dashboard(self, date_filter=None, cashier_id=None, **kw):
        today = fields.Date.today()
        selected_date = date_filter if date_filter else str(today)

        # 1. Filtre Commandes POS (Utilisation de employee_id au lieu de user_id)
        domain_pos = [
            ('date_order', '>=', selected_date + ' 00:00:00'),
            ('date_order', '<=', selected_date + ' 23:59:59')
        ]
        if cashier_id and cashier_id.isdigit():
            domain_pos.append(('employee_id', '=', int(cashier_id)))

        pos_orders = request.env['pos.order'].search(domain_pos)
        ca_jour = sum(pos_orders.mapped('amount_total'))
        commandes_count = len(pos_orders)

        # 2. Liste des caissiers (Exclusion automatique de Administrator)
        cashiers = request.env['hr.employee'].search([
            ('name', '!=', 'Administrator'),
            ('user_id', '!=', 1)
        ])

        # 3. Alertes Stock & Valeur Totale
        products = request.env['product.product'].search([('type', '=', 'product')])
        stock_less_10 = []
        stock_less_0 = []
        valeur_stock_totale = 0.0

        for prod in products:
            qty = prod.qty_available
            valeur_stock_totale += (qty * prod.lst_price)
            if qty <= 0:
                stock_less_0.append({'name': prod.display_name, 'qty': qty})
            elif 0 < qty <= 20:  # Plage 1 à 20
                stock_less_10.append({'name': prod.display_name, 'qty': qty})

        # 4. Masarif (Dépenses)
        masarif_records = request.env['dashboard.masarif'].search([('date', '=', selected_date)])
        total_masarif = sum(masarif_records.mapped('amount'))

        # -------------------------------------------------------------
        # 5. GENERATION DU TEXTE WHATSAPP - STOCK
        # -------------------------------------------------------------
        msg_stock = f"📦 *Rapport Alerte Stock WebPlus* ({selected_date})\n\n"
        if stock_less_0:
            msg_stock += "🔴 *Ruptures (≤ 0) :*\n"
            for item in stock_less_0[:50]:  # Limite 50 dans le message WhatsApp
                msg_stock += f"• {item['name']}: {item['qty']} Pcs\n"
            if len(stock_less_0) > 50:
                msg_stock += f"... et {len(stock_less_0) - 50} autres articles.\n"

        if stock_less_10:
            msg_stock += "\n🟠 *Stock Critique (1 à 20) :*\n"
            for item in stock_less_10[:50]:
                msg_stock += f"• {item['name']}: {item['qty']} Pcs\n"
            if len(stock_less_10) > 50:
                msg_stock += f"... et {len(stock_less_10) - 50} autres articles.\n"

        whatsapp_stock_url = "https://api.whatsapp.com/send?text=" + urllib.parse.quote(msg_stock)

        # -------------------------------------------------------------
        # 6. GENERATION DU TEXTE WHATSAPP - MASARIF
        # -------------------------------------------------------------
        msg_masarif = f"💸 *Rapport Dépenses (Masarif) - WebPlus*\n📅 *Date :* {selected_date}\n\n"
        if masarif_records:
            for m in masarif_records:
                msg_masarif += f"• {m.name} : {m.amount:.2f} DH\n"
            msg_masarif += f"\n💰 *TOTAL MASARIF : {total_masarif:.2f} DH*"
        else:
            msg_masarif += "Aucune dépense enregistrée pour cette date."

        whatsapp_masarif_url = "https://api.whatsapp.com/send?text=" + urllib.parse.quote(msg_masarif)

        return request.render('dashboard_gerant_advanced.gerant_dashboard_template', {
            'user_name': request.env.user.name,
            'selected_date': selected_date,
            'selected_cashier': int(cashier_id) if cashier_id and cashier_id.isdigit() else None,
            'cashiers': cashiers,
            'ca_jour': round(ca_jour, 2),
            'valeur_stock_totale': round(valeur_stock_totale, 2),
            'commandes_count': commandes_count,
            'pos_orders': pos_orders,
            'stock_less_10': stock_less_10,
            'stock_less_0': stock_less_0,
            'masarif_records': masarif_records,
            'total_masarif': round(total_masarif, 2),
            'whatsapp_stock_url': whatsapp_stock_url,
            'whatsapp_masarif_url': whatsapp_masarif_url,
        })

    @http.route('/gerant/add_masarif', type='http', auth='user', methods=['POST'], csrf=False)
    def add_masarif(self, name, amount, **kw):
        if name and amount:
            request.env['dashboard.masarif'].create({
                'name': name,
                'amount': float(amount),
                'date': fields.Date.today(),
            })
        return request.redirect('/gerant')