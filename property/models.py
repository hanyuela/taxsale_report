from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Property(models.Model):
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip = models.CharField(max_length=20)
    parcel_number = models.CharField(max_length=50)
    property_class = models.CharField(max_length=255)
    tax_overdue = models.BooleanField(default=False)
    accessed_land_value = models.DecimalField(max_digits=12, decimal_places=2)
    accessed_improvement_value = models.DecimalField(max_digits=12, decimal_places=2)
    total_assessed_value = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount_annual = models.DecimalField(max_digits=12, decimal_places=2)
    zillow_link = models.URLField(max_length=255, blank=True, null=True)
    redfin_link = models.URLField(max_length=255, blank=True, null=True)
    market_value = models.DecimalField(max_digits=12, decimal_places=2)
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
    latest_sale_date = models.DateField()
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
    users = models.ManyToManyField(User, related_name='properties', through='PropertyUserAgreement')

    def __str__(self):
        return self.street_address

class PropertyUserAgreement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    agreed = models.BooleanField(default=False)  # 是否同意字段

    class Meta:
        unique_together = ('user', 'property')  # 保证每个用户在同一个房产下只能有一个记录


class Auction(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='auctions')
    face_value = models.DecimalField(max_digits=10, decimal_places=2)
    auction_type = models.CharField(
        max_length=20,
        choices=[('lien', 'Lien'), ('deed', 'Deed')]
    )
    is_online = models.CharField(
        max_length=20,
        choices=[('online', 'Online'), ('in-person', 'In-person')]
    )
    auction_tax_year = models.IntegerField(null=True, blank=True)
    batch_number = models.CharField(max_length=50)
    sort_no = models.CharField(max_length=50)
    bankruptcy_flag = models.BooleanField(default=False)
    deposit_deadline = models.DateField(null=True, blank=True)   # Date field for the deposit deadline
    auction_start = models.DateField(null=True, blank=True)  # Date field for the auction start
    auction_end = models.DateField(null=True, blank=True)  # Date field for the auction end
    redemption_period = models.IntegerField(null=True, blank=True)  # Integer field for the redemption period in years
    foreclosure_date = models.DateField(null=True, blank=True)  # Date field for the foreclosure date
    authority_name = models.CharField(max_length=255)  # Name of the authority hosting the tax sale auction, e.g., County or City.
    def __str__(self):
        return f"Auction {self.batch_number} - {self.sort_no}"


class Loan(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='loans')
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    loan_due_date = models.DateField()
    loan_type = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Loan for {self.property.street_address}"


class Owner(models.Model):
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
    
    is_veteran = models.BooleanField(default=False)
    primary_address = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.phone_1} - {self.email_1}"
    
# property/models.py

def import_sample_data():
    # 创建一些示例 Property 数据
    property1 = Property.objects.create(
        street_address="1234 Main St",
        city="City",
        state="State",
        zip="12345",
        parcel_number="0001",
        property_class="Residential",
        tax_overdue=False,
        accessed_land_value=100000.00,  # 确保给这个字段赋值
        accessed_improvement_value=50000.00,
        total_assessed_value=150000.00,
        tax_amount_annual=1500.00,
        market_value=200000.00,
        year_built=1990,
        lot_size_sqft=5000.00,
        lot_size_acres=0.1,
        building_size_sqft=2500.00,
        bedroom_number=3,
        bathroom_number=2,
        latest_sale_date="2022-01-01",
        latest_sale_price=180000.00
    )
    
    property2 = Property.objects.create(
        street_address="5678 Oak St",
        city="Another City",
        state="Another State",
        zip="67890",
        parcel_number="0002",
        property_class="Commercial",
        tax_overdue=True,
        accessed_land_value=200000.00,
        accessed_improvement_value=100000.00,
        total_assessed_value=300000.00,
        tax_amount_annual=3000.00,
        market_value=350000.00,
        year_built=2000,
        lot_size_sqft=10000.00,
        lot_size_acres=0.2,
        building_size_sqft=5000.00,
        bedroom_number=0,  # Commercial property
        bathroom_number=4,
        latest_sale_date="2023-01-01",
        latest_sale_price=280000.00
    )

    property3 = Property.objects.create(
        street_address="9101 Pine St",
        city="New City",
        state="New State",
        zip="98765",
        parcel_number="0003",
        property_class="Residential",
        tax_overdue=False,
        accessed_land_value=150000.00,
        accessed_improvement_value=75000.00,
        total_assessed_value=225000.00,
        tax_amount_annual=2250.00,
        market_value=250000.00,
        year_built=2010,
        lot_size_sqft=6000.00,
        lot_size_acres=0.14,
        building_size_sqft=3000.00,
        bedroom_number=4,
        bathroom_number=3,
        latest_sale_date="2022-06-15",
        latest_sale_price=230000.00
    )

    # 创建一些示例 Auction 数据
    auction1 = Auction.objects.create(
        property=property1,
        face_value=200000.00,
        auction_type="lien",
        is_online="online",
        batch_number="A123",
        sort_no="S001",
        authority_name="County Tax Authority",
        auction_start="2023-01-01",
        auction_end="2023-01-02"
    )

    auction2 = Auction.objects.create(
        property=property2,
        face_value=300000.00,
        auction_type="deed",
        is_online="in-person",
        batch_number="A124",
        sort_no="S002",
        authority_name="City Tax Authority",
        auction_start="2023-02-15",
        auction_end="2023-02-16"
    )

    auction3 = Auction.objects.create(
        property=property3,
        face_value=250000.00,
        auction_type="lien",
        is_online="online",
        batch_number="A125",
        sort_no="S003",
        authority_name="State Tax Authority",
        auction_start="2023-03-10",
        auction_end="2023-03-11"
    )

    print("Sample Property and Auction data has been imported.")

    