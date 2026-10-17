from django.db import migrations, models
import django_ckeditor_5.fields

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('content', django_ckeditor_5.fields.CKEditor5Field('Content', config_name='default')),
                ('published_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
