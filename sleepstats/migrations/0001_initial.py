
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('date', models.DateField()),
                ('meal', models.TextField()),
                ('venue', models.TextField()),
                ('yelpUrl', models.TextField()),
                ('food', models.TextField()),
                ('attendee', models.TextField()),
                ('meal_id', models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
    ]
