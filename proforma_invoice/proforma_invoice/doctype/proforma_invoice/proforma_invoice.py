# Copyright (c) 2024, quantbit and contributors
# For license information, please see license.txt

import frappe

import json
from typing import Literal

import frappe
import frappe.utils
from frappe import _, qb
from frappe.contacts.doctype.address.address import get_company_address
from frappe.model.mapper import get_mapped_doc
# from frappe.model.utils import get_fetch_values
from frappe.query_builder.functions import Sum
from frappe.utils import add_days, cint, cstr, flt, get_link_to_form, getdate, nowdate, strip_html


from erpnext.accounts.party import get_party_account
from erpnext.controllers.selling_controller import SellingController

from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
# from erpnext.stock.doctype.item.item import get_item_defaults

# from erpnext.stock.get_item_details import get_default_bom, get_price_list_rate
from erpnext.stock.stock_balance import get_reserved_qty, update_bin_qty

form_grid_templates = {"items": "templates/form_grid/item_grid.html"}

class ProformaInvoice(SellingController):
	def __init__(self, *args, **kwargs):
		super(ProformaInvoice, self).__init__(*args, **kwargs)

	# @frappe.whitelist()
	# def falgset(self):
	# 	frappe.db.set_value("Proforma Invoice", self.name, "flag", 1)
	
	@frappe.whitelist()
	def getitems(self):
		sales_order_doc = frappe.get_doc("Sales Order", self.sales_order)
		self.taxes_and_charges = sales_order_doc.taxes_and_charges
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

		

		
