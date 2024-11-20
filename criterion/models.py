from django.db import models
from django.contrib.auth.models import User


class States(models.Model):
    state = models.CharField(max_length=50, unique=True)
    abbreviation = models.CharField(max_length=2, unique=True)

    def __str__(self):
        return f"{self.state} ({self.abbreviation})"


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
    GOAL_CHOICES = [
        ('interest', 'Interest'),
        ('foreclosure', 'Foreclosure'),
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
    goal = models.CharField(
        max_length=15, choices=GOAL_CHOICES, null=True, blank=True, default=""
    )
    property_type = models.TextField(null=True, blank=True, default="")

    # 新增字段：市场价值范围和面值范围
    market_value_min = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    market_value_max = models.DecimalField(
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
