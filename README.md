Directory Structure:
│   .copier-answers.yml
│   .editorconfig
│   .eslintrc.yml
│   .gitignore
│   .pre-commit-config.yaml
│   .prettierrc.yml
│   .pylintrc
│   .pylintrc-mandatory
│   .ruff.toml
│   LICENSE
│   README.md
│
├───.github
│   └───workflows
│           pre-commit.yml
│           stale.yml
│           test.yml
│
└───sitewise_integration
    │   requirements.txt
    │   __init__.py
    │   __manifest__.py
    │
    ├───lib
    │   ├───boto3-1.34.152-py3-none-any
    │   ├───botocore-1.34.152-py3-none-any
    │   ├───jmespath-1.0.1-py3-none-any
    │   ├───python_dateutil-2.9.0.post0-py2.py3-none-any
    │   ├───s3transfer-0.10.2-py3-none-any
    │   └───urllib3-2.2.2-py3-none-any
    │
    ├───models
    │       maintenance_attribute.py
    │       maintenance_equipment.py
    │       maintenance_measurement.py
    │       maintenance_metric.py
    │       maintenance_transform.py
    │       res_config_settings.py
    │       __init__.py
    │
    ├───security
    │       ir.model.access.csv
    │
    └───views
            maintenance_attribute_views.xml
            maintenance_equipment_views.xml
            maintenance_measurement_views.xml
            maintenance_metric_views.xml
            maintenance_transform_views.xml
            res_config_settings_views.xml
