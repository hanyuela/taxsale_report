from django.db import models
from django.contrib.auth.models import User


class States(models.Model):
    state = models.CharField(max_length=50, unique=True)
    abbreviation = models.CharField(max_length=2, unique=True)

    def __str__(self):
        return f"{self.state} ({self.abbreviation})"

    @staticmethod
    def populate_states():
        states_data = [
            {"state": "Alabama", "abbreviation": "AL"},
            {"state": "Alaska", "abbreviation": "AK"},
            {"state": "Arizona", "abbreviation": "AZ"},
            {"state": "Arkansas", "abbreviation": "AR"},
            {"state": "California", "abbreviation": "CA"},
            {"state": "Colorado", "abbreviation": "CO"},
            {"state": "Connecticut", "abbreviation": "CT"},
            {"state": "Delaware", "abbreviation": "DE"},
            {"state": "District of Columbia", "abbreviation": "DC"},
            {"state": "Florida", "abbreviation": "FL"},
            {"state": "Georgia", "abbreviation": "GA"},
            {"state": "Hawaii", "abbreviation": "HI"},
            {"state": "Idaho", "abbreviation": "ID"},
            {"state": "Illinois", "abbreviation": "IL"},
            {"state": "Indiana", "abbreviation": "IN"},
            {"state": "Iowa", "abbreviation": "IA"},
            {"state": "Kansas", "abbreviation": "KS"},
            {"state": "Kentucky", "abbreviation": "KY"},
            {"state": "Louisiana", "abbreviation": "LA"},
            {"state": "Maine", "abbreviation": "ME"},
            {"state": "Maryland", "abbreviation": "MD"},
            {"state": "Massachusetts", "abbreviation": "MA"},
            {"state": "Michigan", "abbreviation": "MI"},
            {"state": "Minnesota", "abbreviation": "MN"},
            {"state": "Mississippi", "abbreviation": "MS"},
            {"state": "Missouri", "abbreviation": "MO"},
            {"state": "Montana", "abbreviation": "MT"},
            {"state": "Nebraska", "abbreviation": "NE"},
            {"state": "Nevada", "abbreviation": "NV"},
            #{"state": "New Hampshire", "abbreviation": "NH"},  # no tax sales
            {"state": "New Jersey", "abbreviation": "NJ"},
            {"state": "New Mexico", "abbreviation": "NM"},
            {"state": "New York", "abbreviation": "NY"},
            {"state": "North Carolina", "abbreviation": "NC"},
            {"state": "North Dakota", "abbreviation": "ND"},
            {"state": "Ohio", "abbreviation": "OH"},
            {"state": "Oklahoma", "abbreviation": "OK"},
            {"state": "Oregon", "abbreviation": "OR"},
            {"state": "Pennsylvania", "abbreviation": "PA"},
            {"state": "Rhode Island", "abbreviation": "RI"},
            {"state": "South Carolina", "abbreviation": "SC"},
            {"state": "South Dakota", "abbreviation": "SD"},
            {"state": "Tennessee", "abbreviation": "TN"},
            {"state": "Texas", "abbreviation": "TX"},
            {"state": "Utah", "abbreviation": "UT"},
            {"state": "Vermont", "abbreviation": "VT"},
            {"state": "Virginia", "abbreviation": "VA"},
            {"state": "Washington", "abbreviation": "WA"},
            {"state": "West Virginia", "abbreviation": "WV"},
            {"state": "Wisconsin", "abbreviation": "WI"},
            {"state": "Wyoming", "abbreviation": "WY"},
        ]

        for state_data in states_data:
            States.objects.get_or_create(**state_data)


class Criterion(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    AUCTION_TYPE_CHOICES = [
        ('tax deed', 'Tax Deed'),
        ('tax lien', 'Tax Lien'),
    ]
    IS_ONLINE_CHOICES = [
        ('online', 'Online'),
        ('in-person', 'In-person'),
    ]
    
    PROPERTY_TYPE_CHOICES = [
        ('single_family_residential', 'Single-Family Residential'),
        ('multi_family_residential', 'Multi-Family Residential'),
        ('other_residential', 'Other Residential'),
        ('commercial', 'Commercial'),
        ('vacant_land', 'Vacant Land'),
        ('industrial', 'Industrial'),
        ('agricultural', 'Agricultural'),
        ('miscellaneous', 'Miscellaneous'),
    ]

    auction_type = models.CharField(
        max_length=10, choices=AUCTION_TYPE_CHOICES, null=True, blank=True, default=""
    )
    is_online = models.TextField(
        max_length=10, choices=IS_ONLINE_CHOICES, null=True, blank=True, default=""
    )
    
    property_type = models.TextField(null=True, blank=True, default="")

    # Market value
    Market_Land_Value_min = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    Market_Land_Value_max = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    Market_Improvement_Value_min = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    Market_Improvement_Value_max = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    Total_Market_Value_min = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    Total_Market_Value_max = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    # 新增字段：市场价值范围和面值范围
    Assessed_Land_Value_min = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    Assessed_Land_Value_max = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    Assessed_Improvement_Value_min = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    Assessed_Improvement_Value_max = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    Total_Assessed_Value_min = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    Total_Assessed_Value_max = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    face_value_min = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    face_value_max = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    # Relationships
    states = models.ManyToManyField(
        'States', blank=True
    )

    def __str__(self):
        return f"{self.auction_type or 'No Auction Type'} - {self.goal or 'No Goal'}"

    def get_property_types(self):
        return self.property_type.split(",") if self.property_type else []
