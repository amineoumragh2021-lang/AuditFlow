# Migration personnalisée : suppression du statut audit et remplacement Indisponible par Abordable
from django.db import migrations, models


def convertir_indisponible_en_abordable(apps, schema_editor):
    ChecklistResponse = apps.get_model('audit', 'ChecklistResponse')
    ChecklistResponse.objects.filter(statut='INDISPONIBLE').update(statut='ABORDABLE')


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0002_remove_checklistresponse_est_conforme_and_more'),
    ]

    operations = [
        migrations.RunPython(convertir_indisponible_en_abordable, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='audit',
            name='statut',
        ),
        migrations.AlterField(
            model_name='checklistresponse',
            name='statut',
            field=models.CharField(
                choices=[
                    ('CONFORME', 'Conforme'),
                    ('NON_CONFORME', 'Non conforme'),
                    ('ABORDABLE', 'Abordable'),
                ],
                default='CONFORME',
                max_length=20,
            ),
        ),
    ]
