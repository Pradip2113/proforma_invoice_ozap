// erpnext.accounts.taxes.setup_tax_filters("Sales Taxes and Charges");
// erpnext.accounts.taxes.setup_tax_validations("Sales Order");
// erpnext.sales_common.setup_selling_controller();


// erpnext.selling.SalesOrderController = class SalesOrderController extends erpnext.selling.SellingController {

// };
// extend_cscript(cur_frm.cscript, new erpnext.selling.SalesOrderController({frm: cur_frm}));

frappe.ui.form.on("Proforma Invoice", {
	sales_order: function (frm) {
		frm.clear_table("payment_schedule")
		frm.refresh_field('payment_schedule')
        frm.clear_table("items")
		frm.refresh_field('items')
        frm.clear_table("taxes")
		frm.refresh_field('taxes')
		
		frm.call({
			method:'getitems',
			doc: frm.doc
		});
	}
});
