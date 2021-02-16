# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class TimesheetDetail(Document):
	def time_logs_remove(self, cdt, cdn):
		frappe.msgprint(_("cdT {0}").format(cdt), raise_exception=True)
		frappe.msgprint(_("cdN {0}").format(cdn), raise_exception=True)
		frappe.throw(_("cdt {0}").format(cdt))
