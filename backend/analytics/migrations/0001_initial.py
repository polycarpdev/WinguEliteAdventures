from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PageView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('path', models.CharField(db_index=True, max_length=300)),
                ('referrer', models.CharField(blank=True, help_text='Referring host, empty for direct/internal', max_length=200)),
                ('visitor', models.CharField(db_index=True, max_length=16)),
                ('device', models.CharField(choices=[('mobile', 'Mobile'), ('tablet', 'Tablet'), ('desktop', 'Desktop')], max_length=10)),
                ('browser', models.CharField(blank=True, max_length=30)),
                ('timezone', models.CharField(blank=True, max_length=60)),
                ('language', models.CharField(blank=True, max_length=10)),
                ('is_entry', models.BooleanField(default=False, help_text='First page of a visit (arrived from outside the site)')),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['created_at', 'visitor'], name='analytics_p_created_b366d3_idx')],
            },
        ),
    ]
