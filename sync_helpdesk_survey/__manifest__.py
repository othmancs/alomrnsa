# -*- coding: utf-8 -*-
# Part of Synconics. See LICENSE file for full copyright and licensing details.

{
    "name": "Repair Service - Customer Feedback",
    "version": "1.0",
    "category": "Project",
    "author": "Synconics Technologies Pvt. Ltd.",
    "summary": "Allows to user will fill up survey about ticket",
    "website": "www.synconics.com",
    "description": """
Repair Service - Customer Feedback
==================================
* This application allows to user will fill up survey about ticket.
* Predefined survey questions, if manager will need to modify it then modify easily.
* User can select survey boolean in ticket if customer is interested to give feedback by using ratings and survey about ticket.

help desk management

help desk

Helpdesk

ticket

issue

after sales service

service

helpdesk management

repair

repair service

field service

ticket management

issue management

ticket escalate

issue escalate

escalate

RMA

return merchandise authorization

rma sms

sms

repair service management

field service management

after sales service management

auto assign ticket

ticket number

ticket priority

ticket stages

ticket configuration

cancel ticket

ticket monitor

portal

portal user

portal user ticket

portal user chat

portal user login

website portal user

helpdesk ticket

generate ticket

submit ticket

ticket attachment

ticket document

ticket chat

chat

rma warranty

rma refund

refund

warranty

product warranty

warranty expire

product return

warranty template

repair order

sales order

invoice

accounting

account

warehouse

inventory

website

ecommerce

shipment

receipt

report

rma repair order

sla

service level agreement

ticket deadline

sla policy

sla management

call center

sla on ticket

sla performance

ticket performance

salesperson performance

team performance

sla target

sla report

ticket time

ticket timesheet

ticket time start

ticket time stop

timesheet

ticket time spent

track ticket time

ticket time log

log ticket time

timesheet start

timesheet stop

ticket invoice

timesheet invoice

repair invoice

helpdesk invoice

ticket timesheet invoice

timesheet bill

ticket bill

repair intake

product intake

item intake

inventory intake

intake

repair service intake

ticket intake

sign

digital signature

signed document

document

attachment

sign attachment

pdf

intake approval

intake rejection

reject intake

approve intake

out take

product out take

product outtake

outtake

item outtake

item out take

ticket out take

reject outtake

approve out take

repair service out take

out take sign

mail

dashboard

repair service dashboard

team dashboard

graph

bar

pie

line

ticket assign

assign ticket

ticket auto assign

unassign ticket

ticket unassign

support system

repair service support

chat support

chat ticket system

live chat support

live chat ticket support

helpdesk live chat

helpdesk live chat support

helpdesk live chat ticket

product support service

repair service contract

helpdesk contract

contract

service contract

service contract start

service contract stop

ticket contract

monitor contract

contract renewal

service contract renewal

renew contract

service contract renew

renew service contract

helpdesk contract renew

renew helpdesk contract

service contract invoice

service contract bill

helpdesk contract invoice

ticket from lead

lead to ticket

crm to ticket

helpdesk report

ticket report

rma replace

rma repair

refurbishing

refurbish

product refurbished

repair service refurbish

refurb

refurb product

sub contract

contract renew

subscription

contract subscription

recurring contract

reopen ticket

ticket reopen

re open ticket

ticket re open

rework ticket

ticket rework

repair rework

rework repair

ticket quotation

quotation ticket

ticket estimation

repair quotation

quotation repair

estimation ticket

appointment

repair service appointment

customer appointment

client appointment

ticket appointment

recurring service contract

recurring service ticket

recurring ticket

ticket recurring

service ticket recurring

dynamic ticket

auto generate ticket number

ticket sequence

auto assign ticket number

auto sequence ticket number

unique ticket

unique ticket number

ticket type

merge ticket

ticket merge

sub ticket

sub task

sub service ticket

ticket sub ticket

ticket divide

divide ticket

priority ticket

priority

escalation

team escalation

ticket escalation

issue escalation

task escalation

escalate ticket

feedback

customer feedback

client feedback

repair service feedback

ticket feedback

repair service customer feedback

auto mail

mail automation

customer satisfaction

customer rating

customer survey

survey mail

customer forum

forum

customer knowledge base

client knowledge base

repair service knowledge base

support team

support team knowledgebase

faq

frequently ask question

Q&A

helpdesk forum

support system forum

support system knowledge base

support service video

website slider

customer document

document for customer

knowledgebase video

forum video

forum document

customer like

customer dislike

portal customer

ticket sms

auto send sms

sms service

repair service sms

auto ticket create sms

send sms

stage change sms

sms update

ticket update by sms

customer sms

client sms

helpdesk sms

support service sms

helpdesk video

helpdesk timesheet

helpdesk timesheet invoice

helpdesk timesheet bill

intake website form

intake customer website form

intake product customer web form

helpdesk intake form

helpdesk intake web form

helpdesk intake product web form

website timesheet web form

ticket approval

e-signature

esign

esign approval

esignature approval

website esign

website esignature

customer esign

customer esignature

customer esignature

customer approval esign

customer approval e-sign

customer approval esignature

customer approval e-signature

repair service warranty

warranty management

inventory warranty

sales warranty

repair product warranty

customer warranty

sales order warranty

merge timesheet

team timesheet merge

merge timesheet repair service

helpdesk automation

automate helpdesk

automatic ticket system

""",
    "depends": ["survey", "sync_helpdesk", "rating"],
    "data": [
        "security/ir.model.access.csv",
        "data/ticket_template_data.xml",
        "data/survey_demo_feedback.xml",
        "views/ticket_view.xml",
    ],
    "demo": [
        "demo/ticket_stage_demo.xml",
        "demo/ticket_demo.xml",
        "demo/rating_demo.xml",
        "demo/survey_demo.xml",
    ],
    "images": ["static/description/main_screen.png"],
    "price": 40.0,
    "currency": "EUR",
    "application": True,
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}
