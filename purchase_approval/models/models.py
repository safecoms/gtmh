
from odoo import api, fields, models

class PurchaseOrderTypology(models.Model):
	_name = 'purchase.order.type'
	_description = 'Type of purchase order'

	@api.model
	def _get_domain_sequence_id(self):
		seq_type = self.env.ref('purchase.seq_purchase_order')
		return [('code', '=', seq_type.code)]

	name = fields.Char(string='Name', required=True, translate=True)
	description = fields.Text(string='Description', translate=True)
	sequence_id = fields.Many2one(
		comodel_name='ir.sequence', string='Entry Sequence', copy=False,
		domain=_get_domain_sequence_id)
	
	payment_term_id = fields.Many2one('account.payment.term', 'Payment Term')

	first_approval_person = fields.Many2one('res.users',string="1st Approver",store=True)
	second_approval_person = fields.Many2one('res.users',string="2nd Approver",store=True)
	third_approval_person = fields.Many2one('res.users',string="3rd Approver",store=True)


class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'

	def _get_order_type(self):
		return self.env['purchase.order.type'].search([], limit=1)

	type_id = fields.Many2one(
		comodel_name='purchase.order.type', string='Type', default=_get_order_type)

	state = fields.Selection(selection_add=[
			('first_approval_request','Requested to First Approval'),
			('first_approval_approved','Approved First Approval'),
			('second_approval_request','Requested to Second Approval'),
			('second_approval_approved','Approved Second Approval'),
			('third_approval_request','Requested Third Approval'),
			('third_approval_approved','Approved Third Approval'),
		])

	show_first_approval = fields.Boolean(string="Show First",compute="_compute_show_first_approval")

	show_second_approval = fields.Boolean(string="Show Second",compute="_compute_show_second_approval")

	show_third_approval = fields.Boolean(string="Show Third",compute="_compute_show_third_approval")

	is_refused = fields.Boolean("Explicitely Refused by purchasing manager", readonly=True, copy=False)

	def button_confirm(self):
		for order in self:
			order._add_supplier_to_product()
			order.button_approve()
		return True
		
	def action_request_first_approval(self):
		self.write({'state':'first_approval_request'})
		self.first_approval_activity_update()

	def action_request_second_approval(self):
		self.write({'state':'second_approval_request'})
		self.second_approval_activity_update()

	def action_request_third_approval(self):
		self.write({'state':'third_approval_request'})
		self.third_approval_activity_update()

	def action_approve_first_approval(self):
		self.write({'state':'first_approval_approved'})
		self.first_approval_activity_update()

	def action_approve_second_approval(self):
		self.write({'state':'second_approval_approved'})
		self.second_approval_activity_update()

	def action_approve_third_approval(self):
		self.write({'state':'third_approval_approved'})
		self.third_approval_activity_update()

	def first_approval_activity_update(self):
		for purchase in self.filtered(lambda rec:rec.state == 'first_approval_request'):
			self.activity_schedule(
				'purchase_approval.first_approval',
				user_id=purchase.sudo()._get_first_apporval_person().id or self.env.user.id)
		self.filtered(lambda rec:rec.state == "first_approval_approved").activity_feedback(['purchase_approval.first_approval'])
		self.filtered(lambda rec:rec.state == 'cancel').activity_unlink(['purchase_approval.first_approval'])

	def second_approval_activity_update(self):
		for purchase in self.filtered(lambda rec:rec.state == 'second_approval_request'):
			self.activity_schedule(
				'purchase_approval.second_approval',
				user_id=purchase.sudo()._get_second_apporval_person().id or self.env.user.id)
		self.filtered(lambda rec:rec.state == "second_approval_approved").activity_feedback(['purchase_approval.second_approval'])
		self.filtered(lambda rec:rec.state == 'cancel').activity_unlink(['purchase_approval.second_approval'])

	def third_approval_activity_update(self):
		for purchase in self.filtered(lambda rec:rec.state == 'third_approval_request'):
			self.activity_schedule(
				'purchase_approval.third_approval',
				user_id=purchase.sudo()._get_third_apporval_person().id or self.env.user.id)
		self.filtered(lambda rec:rec.state == "third_approval_approved").activity_feedback(['purchase_approval.third_approval'])
		self.filtered(lambda rec:rec.state == 'cancel').activity_unlink(['purchase_approval.third_approval'])

	def _get_first_apporval_person(self):
		return self.type_id.first_approval_person

	def _get_second_apporval_person(self):
		return self.type_id.second_approval_person

	def _get_third_apporval_person(self):
		return self.type_id.third_approval_person

	def _compute_show_first_approval(self):
		for line in self:
			show = False
			if line.state == 'first_approval_request':
				if line._get_first_apporval_person():
					if self.env.user.id == line._get_first_apporval_person().id:
						show = True
			line.show_first_approval = show

	def _compute_show_second_approval(self):
		for line in self:
			show = False
			if line.state == 'second_approval_request':
				if line._get_second_apporval_person():
					if self.env.user.id == line._get_second_apporval_person().id:
						show = True
			line.show_second_approval = show

	def _compute_show_third_approval(self):
		for line in self:
			show = False
			if line.state == 'third_approval_request':
				if line._get_third_apporval_person():
					if self.env.user.id == line._get_third_apporval_person().id:
						show = True
			line.show_third_approval = show

	def refuse_expense(self, reason):
		self.write({'is_refused': True})

		if self.state == 'first_approval_request':
			self.first_approval_activity_update()
		if self.state == 'second_approval_request':
			self.second_approval_activity_update()
		if self.state == 'third_approval_request':
			self.third_approval_activity_update()

		self.write({'state': 'cancel'})
		self.message_post_with_view('purchase_approval.purchase_template_refuse_reason',
												values={'reason': reason,'name': self.name,'state':self.state})

	@api.onchange('type_id')
	def onchange_type_id(self):
		for order in self:
			if order.type_id.payment_term_id:
				order.payment_term_id = order.type_id.payment_term_id.id

	@api.model
	def create(self, vals):
		if vals.get('name', '/') == '/'and vals.get('type_id'):
			purchase_type = self.env['purchase.order.type'].browse(vals['type_id'])
			if purchase_type.sequence_id:
				vals['name'] = purchase_type.sequence_id.next_by_id()
		return super(PurchaseOrder, self).create(vals)

	def _prepare_invoice(self):
		res = super(PurchaseOrder, self)._prepare_invoice()
		if self.type_id:
			res['purchase_type_id'] = self.type_id.id
		return res


