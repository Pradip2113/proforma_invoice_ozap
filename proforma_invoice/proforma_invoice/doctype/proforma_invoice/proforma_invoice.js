// // Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// // License: GNU General Public License v3. See license.txt

// // frappe.ui.form.on("Proforma Invoice", {
	
// // });

frappe.ui.form.on("Proforma Invoice", {
	sales_order: async function (frm) {
		frm.clear_table("payment_schedule")
        frm.clear_table("items")
        frm.clear_table("taxes")
		frm.refresh_fields()
		await frm.call({
			method:'getitems',
			doc: frm.doc
		});
	},
});


frappe.ui.form.on("ProForma Invoice Item","rate", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
		if(d.qty >= 0 && d.rate >= 0){
		var result = (d.qty * d.rate).toFixed(2);
		frappe.model.set_value(cdt, cdn, 'amount', result);
	}
});
frappe.ui.form.on("ProForma Invoice Item","qty", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
		if(d.qty >= 0 && d.rate >= 0){
		var result = (d.qty * d.rate).toFixed(2);
		frappe.model.set_value(cdt, cdn, 'amount', result);
	}
});

