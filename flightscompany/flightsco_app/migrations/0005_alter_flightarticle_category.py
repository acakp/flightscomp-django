import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("flightsco_app", "0004_seed_lab6_relations"),
    ]

    operations = [
        migrations.AlterField(
            model_name="flightarticle",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="articles",
                to="flightsco_app.flightcategory",
                verbose_name="Категория",
            ),
        ),
    ]
