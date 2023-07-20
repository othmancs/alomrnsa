# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
##########################################################################
{
    "name"              :  "Website Base Filters and Attributes",
    "summary"           :  "This module provides a common form for all filters and attributes inside product grid view.",
    "category"          :  "Website",
    "version"           :  "1.0.0",
    "sequence"          :  1,
    "author"            :  "Webkul Software Pvt. Ltd.",
    "license"           :  "Other proprietary",
    "website"           :  "",
    "description"       :  "This module provides a common form to all filters and attributes inside product grid view",
    "live_test_url"     :  "",
    "depends"           :  [
                            'website_sale',
    ],
    "data"              :  [
                            'view/inherit_website_template.xml',
    ],
    "demo"              :  [
    ],
    "images"            :  ['static/description/Banner.png'],
    "application"       :  True,
    "installable"       :  True,
    "auto_install"      :  False,
    "currency"          :  "EUR",
    # "pre_init_hook"     :  "pre_init_check",
}
