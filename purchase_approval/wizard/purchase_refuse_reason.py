from odoo import api, fields, models

class PurchaseRefuseWizard(models.TransientModel):
    _name = "purchase.refuse.wizard"
    _description = "Purchase Refuse Reason Wizard"

    reason = fields.Char(string='Reason', required=True)
    purchase_ids = fields.Many2many('purchase.order')
    
    @api.model
    def default_get(self, fields):
        res = super(PurchaseRefuseWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        refuse_model = self.env.context.get('purchase_refuse_model')
        if refuse_model == 'purchase.order':
            res.update({
                'purchase_ids': active_ids,
            })
        return res

    def purchase_refuse_reason(self):
        self.ensure_one()
        if self.purchase_ids:
            self.purchase_ids.refuse_expense(self.reason)
        return {'type': 'ir.actions.act_window_close'}
