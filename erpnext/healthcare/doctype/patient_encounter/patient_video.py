# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import throw, _
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant
from twilio.rest import Client

@frappe.whitelist(allow_guest=True)
def get_room(encounter_name=None, guest_code=None):
	twilio_account_sid = "AC70b39fd03e3485b309ad8a70a1bb225f"
	twilio_api_key_sid = "SKeae44b74f2c50d1d0d87845ffe0084ca"
	twilio_api_key_secret = "mwf41jZu62hfb5KVWilUFPPDUSRRH7mL"

	#either encounter_name or guest_code must be passed
	if not encounter_name and not guest_code:
		frappe.throw("Must provide encounter name or guest code")

	#check if it is a guest patient
	user = frappe.session.user
	if not user or user == 'Guest':
		#check guest's permission code for encounter
		appointment_name = frappe.db.get_value("Patient Appointment", {"tele_code":guest_code}, "name")
		if not guest_code or not appointment_name:
			frappe.throw(_("Access Denied"), frappe.AuthenticationError)

		else:
			encounter_list = frappe.db.get_values("Patient Encounter", {'appointment': appointment_name}, "*", as_dict=True)
			if not encounter_list:
				frappe.throw("Must wait for medic to start consultation.")
			encounter = encounter_list[0]
			#twilio
			identity = encounter.patient_name
			#make sure room_id is the same for user and non-user
			room_id = encounter.name + encounter.patient + encounter.practitioner
			token = AccessToken(twilio_account_sid, twilio_api_key_sid,
				twilio_api_key_secret, identity=identity)
			token.add_grant(VideoGrant(room=room_id))
			return {
				"id": room_id,
				"accessToken": token.to_jwt().decode()
			}
	else:
		#check valid encounter
		if not encounter_name or not frappe.db.get_value("Patient Encounter", {"name":encounter_name}):
			frappe.throw(_("Access Denied"))

		status = frappe.db.get_value("Patient Encounter", {"name":encounter_name}, "docstatus")
		if status == 1 or status == 2:
			frappe.throw(_("Access Denied"))

		patient = frappe.db.get_value("Patient Encounter", {"name":encounter_name}, "patient")
		practitioner = frappe.db.get_value("Patient Encounter", {"name":encounter_name}, "practitioner")

		if user == 'Administrator' or validate_encounter_practitioner(encounter_name):
			#twilio
			first_name = frappe.db.get_value("Healthcare Practitioner", {"user_id":user}, "first_name")
			last_name = frappe.db.get_value("Healthcare Practitioner", {"user_id":user}, "last_name")
			identity = user
			if first_name:
				identity = first_name
			if last_name:
				identity = identity + ' ' + last_name

			#make sure room_id is the same for user and non-user
			room_id = encounter_name + patient + practitioner
			token = AccessToken(twilio_account_sid, twilio_api_key_sid,
				twilio_api_key_secret, identity=identity)
			token.add_grant(VideoGrant(room=room_id))
			return {
				"id": room_id,
				"accessToken": token.to_jwt().decode()
			}

	frappe.throw(_("Access Denied"))


def validate_encounter_practitioner(encounter_name):
	practitioner = frappe.db.get_value("Healthcare Practitioner", {"user_id":frappe.session.user}, "name")
	authorized_practitioner = frappe.db.get_value("Patient Encounter", {"name":encounter_name}, "practitioner")
	if practitioner == authorized_practitioner:
		return True

	return False
