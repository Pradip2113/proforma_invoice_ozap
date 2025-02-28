# # Copyright (c) 2025, Sanpra and contributors
# # For license information, please see license.txt


import frappe
from frappe.model.document import Document
from frappe.utils import money_in_words
# from frappe import _
# from frappe.model.mapper import get_mapped_doc
# from frappe.utils import flt, getdate, nowdate

# from proform_invoice.controllers.selling_controller import SellingController

# form_grid_templates = {"items": "templates/form_grid/item_grid.html"}

from frappe.model.document import Document
import frappe
from frappe.model.document import Document
from frappe.utils import money_in_words
from erpnext.accounts.doctype.sales_taxes_and_charges.sales_taxes_and_charges import (
	SalesTaxesandCharges,
)

class ProformaInvoice(Document):
	def before_save(self):
		self.get_gst_calculation()
		tot_qty = 0
		for m in self.items:
			tot_qty += m.qty
		self.total_qty = tot_qty
		tot_tax = 0
		for j in self.taxes:
			tot_tax += float(j.tax_amount)
		self.total_taxes_and_charges = tot_tax
		self.rounded_total = self.total + tot_tax
		self.in_words = money_in_words(self.rounded_total)



	@frappe.whitelist()
	def get_gst_calculation(self):
		total = 0
		tot_amount = 0
		tot_taxable_amount = 0
		avg_rate = 0
		customer_state = frappe.get_value("Address", self.customer_address, 'state')
		company_state = frappe.get_value("Address", self.company_address, 'state')
		for out in self.get('items', filters={'amount':['!=', None]}):
			tot_amount += float(out.amount)
			item = frappe.get_doc("Item", out.item_code)
			for tax in item.taxes:
				item_tax_template = tax.item_tax_template
				company_tax_template = frappe.get_value("Item Tax Template", item_tax_template, 'company')
				
				if company_tax_template == self.company:
					out.item_tax_template = item_tax_template
					gst_rate = frappe.get_value("Item Tax Template", item_tax_template, 'gst_rate')
					out.gst_rate = gst_rate
					if customer_state == company_state:
						avg_rate += gst_rate / 2
						out.cgst_amount = out.sgst_amount = (float(out.amount) / 100) * (gst_rate / 2)
					else:
						# out.igst_rate = gst_rate
						out.igst_amount = (out.amount / 100) * gst_rate
					break
		for out in self.get('items'):
			tot_taxable_amount += (out.get("igst_amount",0) or 0) + (out.get("cgst_amount",0) or 0) + (out.get("sgst_amount",0) or 0)
		
		avg_rate = avg_rate / len(self.items)
		if customer_state == company_state:
			filter ={'is_inter_state': 0, 'is_reverse_charge': 0,'gst_state': company_state}
			tot_taxable_amount = tot_taxable_amount / 2
		else:
			filter ={'is_inter_state': 1, 'is_reverse_charge': 0,'gst_state': company_state}
		self.total = tot_amount
		tax_cat_list = frappe.get_value("Tax Category",filter,'name')
		self.taxes_and_charges_template = frappe.get_value("Sales Taxes and Charges Template", {'tax_category': tax_cat_list, 'company': self.company}, 'name')
		if self.taxes_and_charges_template:
			taxes_charges_doc = frappe.get_doc("Sales Taxes and Charges Template",{'name':self.taxes_and_charges_template})
			for tx in taxes_charges_doc.taxes:
				if "SGST" in tx.account_head or "IGST" in tx.account_head or "CGST" in tx.account_head:
					exist = self.get('taxes', {"charge_type": tx.charge_type, "account_head": tx.account_head, "description": tx.description, "cost_center": tx.cost_center})
					if exist:
						tot_amount += tot_taxable_amount
						exist[0].tax_amount = tot_taxable_amount
						exist[0].total = round(tot_amount,2)
					else:
						tot_amount += tot_taxable_amount
						self.append("taxes",{
							"charge_type": tx.charge_type,
							"account_head": tx.account_head,
							"description": tx.description,
							"cost_center": tx.cost_center,
							"tax_amount": tot_taxable_amount,
							"total": round(tot_amount,2)
						})
				else:
					exist = self.get('taxes', {"charge_type": tx.charge_type, "account_head": tx.account_head, "description": tx.description, "cost_center": tx.cost_center})
					if exist:
						tot_amount += exist[0].tax_amount
						tot_taxable_amount = (tot_amount / 100) * avg_rate
						exist[0].total = round(tot_amount,2)
					else:
						self.append("taxes",{
							"charge_type": tx.charge_type,
							"account_head": tx.account_head,
							"description": tx.description,
							"cost_center": tx.cost_center,
							"tax_amount": 0,
							"total": round(tot_amount,2)
						})

		self.total_amount = tot_amount
		self.rounded_adjustment = tot_amount - round(tot_amount)
		self.rounded_amount = round(tot_amount)

	@frappe.whitelist()
	def getitems(self):
		sales_order_doc = frappe.get_doc("Sales Order", self.sales_order)
		self.taxes_and_charges = sales_order_doc.taxes_and_charges
		self.customer_address = sales_order_doc.customer_address
		self.address_display = sales_order_doc.address_display
		self.contact_person = sales_order_doc.contact_person
		self.contact_display = sales_order_doc.contact_display
		self.contact_mobile = sales_order_doc.contact_mobile
		self.shipping_address_name = sales_order_doc.shipping_address_name
		self.shipping_address = sales_order_doc.shipping_address
		self.company_address = sales_order_doc.company_address
		self.company_address_display = sales_order_doc.company_address_display
		self.total_qty = sales_order_doc.total_qty
		self.total = sales_order_doc.total
		self.total_taxes_and_charges = sales_order_doc.total_taxes_and_charges
		self.grand_total = sales_order_doc.grand_total
		self.rounding_adjustment = sales_order_doc.rounding_adjustment
		self.rounded_total = sales_order_doc.rounded_total
		self.in_words = sales_order_doc.in_words

		for oc in sales_order_doc.get("items"):
			qty_difference = oc.qty - oc.delivered_qty
			if qty_difference > 0:
				self.append("items", {
					"item_code": oc.item_code,
					"delivery_date": oc.delivery_date,
					"item_name": oc.item_name,
					"qty": qty_difference,
					"discount_percentage": oc.discount_percentage,
					"discount_amount": oc.discount_amount,
					"uom": oc.uom,
					"rate": oc.rate,
					"base_rate": oc.base_rate,
					"amount": oc.amount,
					"base_amount": oc.base_amount,
					"item_tax_template": oc.item_tax_template,
					"net_rate": oc.net_rate,
					"net_amount": oc.net_amount,
					"valuation_rate": oc.valuation_rate,
					"gross_profit": oc.gross_profit,
					"description": oc.description,
					"gst_hsn_code": oc.gst_hsn_code,
					"conversion_factor": oc.conversion_factor,
					"invoice_qty": oc.delivered_qty,
					"sales_order_qty":oc.qty
				})
		for op in sales_order_doc.get("taxes"):
			self.append("taxes", {
				"charge_type": op.charge_type,
				"row_id": op.row_id,
				"account_head": op.account_head,
				"description": op.description,
				"rate": op.rate,
				"account_currency": op.account_currency,
				"tax_amount": op.tax_amount,
				"total": op.total,
				"base_tax_amount": op.base_tax_amount,
				"base_total": op.base_total,
				"item_wise_tax_detail": op.item_wise_tax_detail
			})
		
		for mg in sales_order_doc.get("payment_schedule"):
			self.append("payment_schedule", {
				"due_date": mg.due_date,
				"payment_term": mg.payment_term,
				"description": mg.description,
				"mode_of_payment": mg.mode_of_payment,
				"invoice_portion": mg.invoice_portion,
				"discount_type": mg.discount_type,
				"discount_date": mg.discount_date,
				"discount": mg.discount,
				"payment_amount": mg.payment_amount,
				"paid_amount": mg.paid_amount,
				"base_payment_amount": mg.base_payment_amount
			})








