# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo.addons.saudi_hr.controller.main import EmployeeInfo


class EmployeeInfoInherited(EmployeeInfo):
    def get_employee_fill_data(self, employee, kw):
        """
        Processes input data to extract and organize employee qualifications, certifications,
        and experiences before updating the employee data.
        
        :param employee: Method for filling employee data based on certain keys in a dictionary. It
        processes the input data and organizes it into qualification, certification, and experience
        lists before updating the main data dictionary with these lists
        :return: Returning a dictionary `data` that contains information related to an employee. This
        dictionary includes keys such as "qualification_ids", "certification_ids", and "experience_ids"
        which hold lists of qualifications, certifications, and experiences respectively. The method
        processes the input data `kw` to extract relevant information and update the `data` dictionary
        accordingly before returning it.
        """
        data = super(EmployeeInfoInherited, self).get_employee_fill_data(employee, kw)
        available_keys = []
        for key in data.keys():
            if (
                key.startswith("qualification_tr_")
                or key.startswith("certification_tr_")
                or key.startswith("experience_tr_")
                or key in ["dropped_resume", "dropped_resume_filename"]
            ):
                available_keys.append(key)
        # RuntimeError: dictionary changed size during iteration
        for delete_key in available_keys:
            data.pop(delete_key)
        qualification_keys_list = []
        certification_keys_list = []
        experience_keys_list = []
        qualification_temp = {}
        certification_temp = {}
        experience_temp = {}
        for key, value in kw.items():
            if key.startswith("qualification_tr_"):
                qualification_keys_list.append(key.split("qualification_tr_")[1])
            if key.startswith("certification_tr_"):
                certification_keys_list.append(key.split("certification_tr_")[1])
            if key.startswith("experience_tr_"):
                experience_keys_list.append(key.split("experience_tr_")[1])
            if kw.get("dropped_resume"):
                _, encoded_data = kw.get("dropped_resume").split(",", 1)
                data.update(
                    {
                        "attachment_ids": [
                            (0, 0,
                                {
                                    "name": kw.get("dropped_resume_filename"),
                                    "datas": encoded_data,
                                },
                            )
                        ]
                    }
                )
        for key in qualification_keys_list:
            if key[0] in qualification_temp:
                qualification_temp[key[0]].update(
                    {
                        key.split("%s_" % key[0])[1]: kw.get(
                            "qualification_tr_%s" % (key)
                        )
                    }
                )
            else:
                qualification_temp.update(
                    {
                        key[0]: {
                            key.split("%s_" % key[0])[1]: kw.get(
                                "qualification_tr_%s" % (key)
                            )
                        }
                    }
                )

        for key in certification_keys_list:
            if key[0] in certification_temp:
                certification_temp[key[0]].update(
                    {
                        key.split("%s_" % key[0])[1]: kw.get(
                            "certification_tr_%s" % (key)
                        )
                    }
                )
            else:
                certification_temp.update(
                    {
                        key[0]: {
                            key.split("%s_" % key[0])[1]: kw.get(
                                "certification_tr_%s" % (key)
                            )
                        }
                    }
                )

        for key in experience_keys_list:
            if key[0] in experience_temp:
                experience_temp[key[0]].update(
                    {key.split("%s_" % key[0])[1]: kw.get("experience_tr_%s" % (key))}
                )
            else:
                experience_temp.update(
                    {
                        key[0]: {
                            key.split("%s_" % key[0])[1]: kw.get(
                                "experience_tr_%s" % (key)
                            )
                        }
                    }
                )
        qualification_list = []
        for key, value in qualification_temp.items():
            value.update({"company_id": employee.sudo().company_id.id})
            qualification_list.append((0, 0, value))

        certification_list = []
        for key, value in certification_temp.items():
            value.update({"company_id": employee.sudo().company_id.id})
            if "issue_date" in value and value.get("issue_date"):
                datetime_object = datetime.strptime(value["issue_date"], "%m/%d/%Y")
                value.update({"issue_date": datetime_object})
            if "expiry_date" in value and value.get("expiry_date"):
                datetime_object = datetime.strptime(value["expiry_date"], "%m/%d/%Y")
                value.update({"expiry_date": datetime_object})
            certification_list.append((0, 0, value))

        experience_list = []
        for key, value in experience_temp.items():
            value.update({"company_id": employee.sudo().company_id.id})
            if "time_period_from" in value and value.get("time_period_from"):
                datetime_object = datetime.strptime(
                    value["time_period_from"], "%m/%d/%Y"
                )
                value.update({"time_period_from": datetime_object})
            if "time_period_to" in value and value.get("time_period_to"):
                datetime_object = datetime.strptime(value["time_period_to"], "%m/%d/%Y")
                value.update({"time_period_to": datetime_object})
            experience_list.append((0, 0, value))

        data.update(
            {
                "qualification_ids": qualification_list,
                "certification_ids": certification_list,
                "experience_ids": experience_list,
            }
        )
        return data
