# Generated by Django 3.1.4 on 2021-01-24 15:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_remove_category_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='resolution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.resolution'),
        ),
    ]
