
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SleepInstance',
            fields=[
                ('starttime', models.DateTimeField()),
                ('endtime', models.DateTimeField()),
                ('minutes', models.IntegerField()),
                ('sleepQuality', models.IntegerField()),
            ],
        ),
    ]
