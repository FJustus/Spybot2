# Generated by Django 4.1.3 on 2022-12-14 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spybot', '0005_hourlyactivity_hourlyactiv_datetim_96f0af_idx'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='tsuseractivity',
            index=models.Index(fields=['start_time'], name='TSUserActiv_startTi_95ea75_idx'),
        ),
    ]
