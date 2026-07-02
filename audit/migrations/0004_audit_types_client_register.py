from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0003_remove_audit_statut_abordable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audit',
            name='type_audit',
            field=models.CharField(
                choices=[
                    ('QUALITE', 'Audit qualité'),
                    ('SECURITE', 'Audit sécurité'),
                    ('ENVIRONNEMENT', 'Audit environnement'),
                    ('INTERNE', 'Audit interne'),
                ],
                default='QUALITE',
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name='checklistitem',
            name='type_audit',
            field=models.CharField(
                choices=[
                    ('QUALITE', 'Audit qualité'),
                    ('SECURITE', 'Audit sécurité'),
                    ('ENVIRONNEMENT', 'Audit environnement'),
                    ('INTERNE', 'Audit interne'),
                ],
                max_length=30,
            ),
        ),
    ]
