{
    'name': 'Maintenance Custom Config',
    'version': '17.0.0',
    'summary': 'Custom configurations for the Maintenance app',
    'category': 'Maintenance',
    'author': 'Your Name',
    'depends': ['maintenance'],
    'data': [
        'views/maintenance_attribute_views.xml',
        'views/maintenance_measurement_views.xml',
        'views/maintenance_transform_views.xml',
        'views/maintenance_metric_views.xml',
    ],
    'installable': True,
    'application': False,
}
