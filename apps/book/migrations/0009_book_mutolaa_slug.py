from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("book", "0008_book_show_on_home"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="mutolaa_slug",
            field=models.CharField(
                blank=True,
                max_length=255,
                null=True,
                verbose_name="Mutolaa slug",
            ),
        ),
    ]
