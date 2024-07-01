# -*- coding: utf-8 -*-
{
    'name': "Website Floating Social Icon",
    'summary': "Floating Social Icons for website side bar | Using the floating sidebar, you can put social media share buttons on your website. Easily customizable buttons for social network sharing  in india bangladesh pakistan dubai nepal bhuatan",
    'description': "Floating Social Icons for website side bar",
    'author': "Metamorphosis",
    'website': "https://metamorphosis.com.bd",
    'category': 'Website',
    'version': '16.0.0.0',
    'icon' :  '/meta_web_floating_social_icon/static/description/icon.png',
    'images':  ['static/description/images/banner.gif'],
    'license': 'AGPL-3',

    'depends': ['base','website'],


    'data': [
        # 'security/ir.model.access.csv',
        'views/social_floating_icon.xml',
        'views/views.xml',
    ],
    
    'assets':{
        
        'web.assets_frontend':[
            'meta_web_floating_social_icon/static/src/scss/social_floating_icon.scss',
            
        ],
        
    },
    
    'sequence':0,
    'application':True,
    'installable':True,
    'auto-install':False
}
