from django.db import models

class provider(models.Model):
    upn=models.CharField(max_length=100)
    scope=models.CharField(max_length=100)
    publisher_name=models.CharField(max_length=100)
    role_name=models.CharField(max_length=20)
    role_type=models.CharField(max_length=20)
    manageable=models.BooleanField()

class offer(models.Model):
    offerid=models.CharField(max_length=100)
    publisher_id=models.CharField(max_length=100)
    display_text=models.CharField(max_length=100)
    publisher_name=models.CharField(max_length=100)
    offer_type_name=models.CharField(max_length=30)
    status=models.CharField(max_length=10)
    version=models.IntegerField()
    change_time = models.CharField(max_length=30)

class publisher(models.Model):
    version=models.IntegerField()
    publisher_id=models.CharField(max_length=50)
    display_text=models.CharField(max_length=100)
    microsoft_partner_network_id=models.IntegerField()
    public_publisher_id=models.CharField(max_length=100)
    legacy_publisher_id=models.CharField(max_length=100)
    expired_time=models.CharField(max_length=30)
    changed_time=models.CharField(max_length=30)