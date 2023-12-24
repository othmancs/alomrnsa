# -*- coding: utf-8 -*-
# Part of Odoo, Aktiv Software.
# See LICENSE file for full copyright & licensing details.

# Author: Aktiv Software.
# mail: odoo@aktivsoftware.com
# Copyright (C) 2015-Present Aktiv Software PVT. LTD.
# Contributions:
# Aktiv Software:
# - Geet Thakkar
# - Aryan Modh
# - Harshil Soni

{
    "name": "Signup With Mobile Number",
    "category": "Extra Tools",
    "summary": """Signup With Mobile (If not Email).
    signup,
    signin,
    reset,
    reset password,
    signup mobile,
    signup with mobile,
    signup with phone,
    signup with number,
    phone signup,
    mobile signup,
    signin mobile,
    signin with number,
    signin with mobile,
    signin with phone,
    phone signin,
    mobile signin,
    signin number,
    signup number,
    signin with number,
    signup with number,
    number signin,
    number signup,""",
    "author": "Aktiv Software",
    "website": "https://www.aktivsoftware.com/",
    "license": "OPL-1",
    "version": "16.0.1.0.0",
    "price": 9.82,
    "currency": "EUR",
    "description": """

    Title: Signup With Mobile Number \n
    Author: Aktiv Software PVT. LTD. \n
    mail: odoo@aktivsoftware.com \n
    Copyright (C) 2015-Present Aktiv Software PVt. LTD. \n
    Contributions: Aktiv Software \n

    This module can create users from the Odoo main screen as an 
    external user and signup with the same credentials.
    It mainly provides validation of email id and mobile number during signup.
    User id has to be  unique for every account so email id and mobile number
    cannot be duplicated.
    signup,
    signin,
    reset,
    reset password,
    signup mobile,
    signup with mobile,
    signup with phone,
    signup with number,
    phone signup,
    mobile signup,
    signin mobile,
    signin with number,
    signin with mobile,
    signin with phone,
    phone signin,
    mobile signin,
    signin number,
    signup number,
    signin with number,
    signup with number,
    number signin,
    number signup,
    """,
    "depends": ["auth_signup", "portal"],
    "data": [
        "data/signup_demo.xml",
        "views/auth_signup.xml",
        "views/auth_signin.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            # External Library
            "signup_with_phone/static/lib/intl_tel_Input/js/intlTelInput.js",
            "signup_with_phone/static/lib/intl_tel_Input/js/data.js",
            "signup_with_phone/static/lib/intl_tel_Input/js/data.min.js",
            "signup_with_phone/static/lib/intl_tel_Input/js/intlTelInput-jquery.js",
            "signup_with_phone/static/lib/intl_tel_Input/js/intlTelInput-jquery.min.js",
            "signup_with_phone/static/lib/intl_tel_Input/js/utils.js",
            "signup_with_phone/static/lib/intl_tel_Input/css/intlTelInput.min.css",
            "signup_with_phone/static/lib/intl_tel_Input/css/intlTelInput.css",
            # Custom
            "signup_with_phone/static/src/js/country_code.js",
            "signup_with_phone/static/src/css/country_code_img.css",
        ],
    },
    "images": ["static/description/banner.jpg"],
    "auto_install": False,
    "installable": True,
    "application": True,
}
