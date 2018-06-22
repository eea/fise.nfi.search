# Generated by Django 2.0.6 on 2018-06-22 12:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0013_auto_20180620_0743'),
    ]

    operations = [
        migrations.CreateModel(
            name='GEMETConcept',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('broader', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='narrower', to='search.GEMETConcept')),
                ('related', models.ManyToManyField(blank=True, related_name='_gemetconcept_related_+', to='search.GEMETConcept')),
            ],
            options={
                'db_table': 'gemet_concept',
            },
        ),
        migrations.CreateModel(
            name='GEMETConceptLanguage',
            fields=[
                ('code', models.CharField(max_length=2, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=60)),
            ],
            options={
                'db_table': 'gemet_concept_language',
            },
        ),
        migrations.CreateModel(
            name='GEMETConceptName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('concept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='names', to='search.GEMETConcept')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='search.GEMETConceptLanguage')),
            ],
            options={
                'db_table': 'gemet_concept_name',
            },
        ),
        migrations.AlterUniqueTogether(
            name='gemetconceptname',
            unique_together={('concept', 'language')},
        ),
    ]
