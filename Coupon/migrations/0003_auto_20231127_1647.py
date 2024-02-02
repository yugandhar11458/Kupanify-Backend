# Generated by Django 3.2.23 on 2023-11-27 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Coupon', '0002_alter_coupon_description_alter_coupon_screenshots_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='availedCouponsIds',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='uploadedCouponsIds',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='availedCoupons',
            field=models.ManyToManyField(blank=True, related_name='availed_coupons', to='Coupon.Coupon'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='uploadedCoupons',
            field=models.ManyToManyField(blank=True, related_name='uploaded_coupons', to='Coupon.Coupon'),
        ),
    ]