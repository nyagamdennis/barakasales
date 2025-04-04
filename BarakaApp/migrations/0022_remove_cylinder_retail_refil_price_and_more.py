# Generated by Django 5.0.7 on 2025-01-13 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BarakaApp', '0021_assignedotherproducts'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cylinder',
            name='retail_refil_price',
        ),
        migrations.RemoveField(
            model_name='cylinder',
            name='retail_selling_price',
        ),
        migrations.RemoveField(
            model_name='cylinder',
            name='wholesale_refil_price',
        ),
        migrations.RemoveField(
            model_name='cylinder',
            name='wholesale_selling_price',
        ),
        migrations.AlterField(
            model_name='cylinder',
            name='min_retail_refil_price',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='cylinder',
            name='min_retail_selling_price',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='cylinder',
            name='min_wholesale_refil_price',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='cylinder',
            name='min_wholesale_selling_price',
            field=models.PositiveIntegerField(),
        ),
    ]
