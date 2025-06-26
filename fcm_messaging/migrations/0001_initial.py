# fcm_messaging/migrations/0001_initial.py

from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='FCMCertificate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(
                    max_length=255, unique=True,
                    help_text='A unique name for this Firebase project/certificate.',
                )),
                ('certificate_json', models.JSONField()),
            ],
        ),
    ]
