# Generated by Django 4.2.7 on 2023-12-15 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_ingredient_id_alter_recipe_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(blank=True, default=1, upload_to='recipe_images/'),
            preserve_default=False,
        ),
    ]