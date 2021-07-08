# Generated by Django 2.1.15 on 2020-04-28 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                (
                    'value',
                    models.TextField(
                        blank=True,
                        help_text='Override value set in settings module. For booleans, use "true" or "false".',
                        null=True,
                    ),
                ),
                ('active', models.BooleanField(default=True)),
            ],
        ),
    ]
