
{
    'name': 'Maintenance - AWS IoT Sitewise',
    'version': '17.0.1.0.0',
    'summary': "Custom configurations for the Maintenance app to integrate AWS IoT Sitewise",
    'author': "Hundred Solutions",
    'maintainer': 'Hundred Solutions',
    'company': "Hundred Solutions",
    'website': 'https://www.hundredsolutions.com/',
    'category': 'Maintenance',
    'depends': [
        'maintenance',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/maintenance_attribute_views.xml',
        'views/maintenance_measurement_views.xml',
        'views/maintenance_transform_views.xml',
        'views/maintenance_metric_views.xml',
    ],
    # 'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
}
