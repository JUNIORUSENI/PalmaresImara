# Generated by Django 4.2.17 on 2025-01-10 17:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('palmares', '0003_annee_scolaire_classe_eleve_resultat_section_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='classe',
            name='unique_classe_section_annee',
        ),
        migrations.RemoveConstraint(
            model_name='section',
            name='unique_section_annee',
        ),
        migrations.RemoveField(
            model_name='classe',
            name='annee_scolaire',
        ),
        migrations.RemoveField(
            model_name='classe',
            name='section',
        ),
        migrations.RemoveField(
            model_name='section',
            name='annee_scolaire',
        ),
        migrations.AlterField(
            model_name='eleve',
            name='nom',
            field=models.CharField(db_index=True, max_length=30, verbose_name='Nom'),
        ),
        migrations.AlterField(
            model_name='eleve',
            name='post_nom',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Post-nom'),
        ),
        migrations.AlterField(
            model_name='eleve',
            name='prenom',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Prénom'),
        ),
        migrations.AlterField(
            model_name='resultat',
            name='annee_scolaire',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resultats_annee', to='palmares.annee_scolaire', verbose_name='Année scolaire'),
        ),
        migrations.AlterField(
            model_name='resultat',
            name='classe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resultats_classe', to='palmares.classe', verbose_name='Classe'),
        ),
        migrations.AlterField(
            model_name='resultat',
            name='pourcentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='Pourcentage'),
        ),
        migrations.AlterField(
            model_name='resultat',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resultats_section', to='palmares.section', verbose_name='Section'),
        ),
        migrations.AddConstraint(
            model_name='classe',
            constraint=models.UniqueConstraint(fields=('nom_classe',), name='unique_classe_section_annee'),
        ),
        migrations.AddConstraint(
            model_name='section',
            constraint=models.UniqueConstraint(fields=('nom_section',), name='unique_section'),
        ),
    ]
