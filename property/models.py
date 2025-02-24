from django.db import models
from django.contrib.auth.models import User
import random
from datetime import datetime, timedelta
# Create your models here.

class Auction(models.Model):
    auction_type = models.CharField(
        max_length=20,
        choices=[('lien', 'Lien'), ('deed', 'Deed')]
    )
    is_online = models.CharField(
        max_length=20,
        choices=[('online', 'Online'), ('in-person', 'In-person')]
    )
    auction_tax_year = models.IntegerField(null=True, blank=True)
    deposit_deadline = models.DateField(null=True, blank=True)   # Date field for the deposit deadline
    auction_start = models.DateField(null=True, blank=True)  # Date field for the auction start
    auction_end = models.DateField(null=True, blank=True)  # Date field for the auction end
    redemption_period = models.IntegerField(null=True, blank=True)  # Integer field for the redemption period in years
    foreclosure_date = models.DateField(null=True, blank=True)  # Date field for the foreclosure date
    authority_name = models.CharField(max_length=255)  # Name of the authority hosting the tax sale auction, e.g., County or City.
    def __str__(self):
        return f"Auction {self.authority_name} ({self.auction_tax_year})"


class Property(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='properties')  # Many-to-one relationship with Auction
    face_value = models.DecimalField(max_digits=10, decimal_places=2)
    batch_number = models.CharField(max_length=50)
    sort_no = models.CharField(max_length=50)
    bankruptcy_flag = models.BooleanField(default=False)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip = models.CharField(max_length=20)
    parcel_number = models.CharField(max_length=50)
    property_class = models.CharField(max_length=255)
    tax_overdue = models.DecimalField(max_digits=12, decimal_places=2)
    accessed_land_value = models.DecimalField(max_digits=12, decimal_places=2)
    accessed_improvement_value = models.DecimalField(max_digits=12, decimal_places=2)
    total_assessed_value = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount_annual = models.DecimalField(max_digits=12, decimal_places=2)
    zillow_link = models.URLField(max_length=255, blank=True, null=True)
    redfin_link = models.URLField(max_length=255, blank=True, null=True)
    Market_Land_Value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    Market_Improvement_Value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    Total_Market_Value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    year_built = models.IntegerField()
    lot_size_sqft = models.DecimalField(max_digits=12, decimal_places=2)
    lot_size_acres = models.DecimalField(max_digits=12, decimal_places=2)
    building_size_sqft = models.DecimalField(max_digits=12, decimal_places=2)
    bedroom_number = models.IntegerField()
    bathroom_number = models.IntegerField()
    nearby_schools = models.CharField(max_length=255, blank=True, null=True)
    walk_score = models.IntegerField(null=True, blank=True)
    transit_score = models.IntegerField(null=True, blank=True)
    bike_score = models.IntegerField(null=True, blank=True)
    environmental_hazard_status = models.CharField(max_length=100, blank=True, null=True)
    flood_status = models.CharField(max_length=100, blank=True, null=True)
    flood_risk = models.CharField(max_length=100, blank=True, null=True)
    latest_sale_date = models.DateField(null=True, blank=True)
    latest_sale_price = models.DecimalField(max_digits=12, decimal_places=2)
    foreclose_score = models.IntegerField(
        default=0,
        choices=[
            (0, '0'),
            (1, '1'),
            (2, '2'),
            (3, '3'),
            (4, '4'),
            (5, '5')
        ],
    )  # 新增字段：允许的值为 0~5，默认值为 0

    owners = models.ManyToManyField('Owner', related_name='properties')
    # 新增字段
    block = models.CharField(max_length=100, blank=True, null=True)  # Block
    lot = models.CharField(max_length=100, blank=True, null=True)  # Lot
    qualifier = models.CharField(max_length=100, blank=True, null=True)  # Qualifier
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)  # Latitude
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)  # Longitude
    def __str__(self):
        return self.street_address



class Loan(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='loans')
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2,blank=True, null=True)
    loan_due_date = models.DateField(blank=True, null=True)
    loan_type = models.CharField(max_length=100,blank=True, null=True)
    
    def __str__(self):
        return f"Loan for {self.property.street_address}"


class Owner(models.Model):
    name = models.CharField(max_length=255)  # Added name field
    phone_1 = models.CharField(max_length=20)
    phone_2 = models.CharField(max_length=20, blank=True, null=True)
    phone_3 = models.CharField(max_length=20, blank=True, null=True)
    phone_4 = models.CharField(max_length=20, blank=True, null=True)
    phone_5 = models.CharField(max_length=20, blank=True, null=True)
    
    email_1 = models.EmailField()
    email_2 = models.EmailField(blank=True, null=True)
    email_3 = models.EmailField(blank=True, null=True)
    email_4 = models.EmailField(blank=True, null=True)
    email_5 = models.EmailField(blank=True, null=True)
    
    Homestead_Exemptions = models.BooleanField(max_length=255, blank=True, null=True)
    primary_address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.phone_1} - {self.email_1}"
    
# property/models.py



    