# -*- coding: utf-8 -*-
# Copyright (C) Quocent Pvt. Ltd.
# All Rights Reserved
{
    "name": "Complete Data Clear And Removal",
    "version": "16.0.1.0.0",
    "summary": "This app enables efficient bulk data clearing and deletion, providing a quick solution for comprehensive data cleanup and management.",
    "category": "Deletion Tool",
    "license": "LGPL-3",
    "author": "Quocent Pvt. Ltd.",
    "website": "https://www.quocent.com",
    "description": "This app is designed to simplify large-scale data management, offering tools to clear and delete, data in bulk.",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/qcent_mass_clear_and_delete_data_menu.xml",
        "wizard/clear_all_data.xml",
    ],
    "images": [
        "static/description/banner.png",
    ],
    "installable": True,
}
