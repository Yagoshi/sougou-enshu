from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='discounted_total',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
