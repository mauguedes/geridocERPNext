# -*- coding: utf-8 -*-
# Copyright (c) 2015, ESS LLP and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr

class PatientEncounter(Document):
	def on_update(self):
		if(self.appointment):
			frappe.db.set_value("Patient Appointment", self.appointment, "status", "Closed")
		#update_encounter_to_medical_record(self)

	#def after_insert(self):
	#	insert_encounter_to_medical_record(self)

	def on_submit(self):
		insert_encounter_to_medical_record(self)

	def on_cancel(self):
		if(self.appointment):
			frappe.db.set_value("Patient Appointment", self.appointment, "status", "Open")
		delete_medical_record(self)
	def validate(self):
		self.set_encounter_datetime()

	def set_encounter_datetime(self):
		self.encounter_datetime = "%s %s" % (self.encounter_date, self.encounter_time or "00:00:00")

def insert_encounter_to_medical_record(doc):
	subject = set_subject_field(doc)
	medical_record = frappe.new_doc("Patient Medical Record")
	medical_record.patient = doc.patient
	medical_record.subject = subject
	medical_record.status = "Open"
	medical_record.communication_date = doc.encounter_date
	medical_record.reference_doctype = "Patient Encounter"
	medical_record.reference_name = doc.name
	medical_record.reference_owner = doc.owner
	medical_record.save(ignore_permissions=True)

def update_encounter_to_medical_record(encounter):
	medical_record_id = frappe.db.sql("select name from `tabPatient Medical Record` where reference_name=%s", (encounter.name))
	if medical_record_id and medical_record_id[0][0]:
		subject = set_subject_field(encounter)
		frappe.db.set_value("Patient Medical Record", medical_record_id[0][0], "subject", subject)
	else:
		insert_encounter_to_medical_record(encounter)

def delete_medical_record(encounter):
	frappe.db.sql("""delete from `tabPatient Medical Record` where reference_name = %s""", (encounter.name))

def set_subject_field(encounter):
	subject = encounter.practitioner+"<br/>"
	if(encounter.symptoms):
		subject += "Symptoms: "+ cstr(encounter.symptoms)+".<br/>"
	else:
		subject += "No Symptoms <br/>"
	if(encounter.diagnosis):
		subject += "Diagnosis: "+ cstr(encounter.diagnosis)+".<br/>"
	else:
		subject += "No Diagnosis <br/>"
	if(encounter.drug_prescription):
		subject +="\nDrug(s) Prescribed. "
	if(encounter.lab_test_prescription):
		subject += "\nTest(s) Prescribed."
	if(encounter.procedure_prescription):
		subject += "\nProcedure(s) Prescribed."

	return subject

#def query_condition_for_patient_encounter(arg):
#	if 'Physician' in frappe.get_roles(frappe.session.user):
#		return None
#	return "(`tabPatient Encounter`)"
