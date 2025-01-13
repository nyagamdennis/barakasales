# Generated by Django 5.0.7 on 2025-01-04 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BarakaApp', '0006_defaultedproducts'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignedCylindersRecipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RenameField(
            model_name='assignedcylinders',
            old_name='complete_sale',
            new_name='retail_refilled',
        ),
        migrations.RenameField(
            model_name='assignedcylinders',
            old_name='refill_sale',
            new_name='retail_sold',
        ),
        migrations.AddField(
            model_name='assignedcylinders',
            name='transaction_complete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='assignedcylinders',
            name='wholesale_refilled',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='assignedcylinders',
            name='wholesale_sold',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
