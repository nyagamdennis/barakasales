# Generated by Django 5.0.7 on 2025-01-13 01:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BarakaApp', '0020_alter_employees_options'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignedOtherProducts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_quantity', models.PositiveIntegerField(default=0)),
                ('spoiled', models.PositiveIntegerField(default=0)),
                ('wholesale_sold', models.PositiveIntegerField(default=0)),
                ('retail_sold', models.PositiveIntegerField(default=0)),
                ('missing_products', models.PositiveIntegerField(default=0)),
                ('transaction_complete', models.BooleanField(default=False)),
                ('date_assigned', models.DateTimeField(auto_now_add=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='BarakaApp.otherproducts')),
                ('sales_team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='other_products_salesTeam', to='BarakaApp.salesteam')),
            ],
        ),
    ]
