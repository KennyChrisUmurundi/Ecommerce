# Generated by Django 2.2 on 2020-03-26 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='category',
            field=models.CharField(choices=[('S', 'Shirt'), ('SW', 'Sport Wear'), ('OW', 'Out Wea')], default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='item',
            name='label',
            field=models.CharField(choices=[('S', 'secondary'), ('P', 'primary'), ('D', 'danger')], default='P', max_length=100),
            preserve_default=False,
        ),
    ]
