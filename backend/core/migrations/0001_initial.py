from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('booking', 'Booking'), ('payment', 'Payment'), ('packing', 'Packing'), ('safari_tips', 'Safari Tips'), ('general', 'General')], default='general', max_length=20)),
                ('question', models.CharField(max_length=300)),
                ('answer', models.TextField()),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'FAQ',
                'verbose_name_plural': 'FAQs',
                'ordering': ['category', 'order'],
            },
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('role', models.CharField(max_length=100)),
                ('bio', models.TextField()),
                ('photo', models.ImageField(upload_to='team/')),
                ('order', models.PositiveIntegerField(default=0, help_text='Display order')),
            ],
            options={
                'ordering': ['order', 'name'],
            },
        ),
    ]
