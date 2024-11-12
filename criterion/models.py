from django.db import models

class States(models.Model):
    state = models.CharField(max_length=50, unique=True)
    abbreviation = models.CharField(max_length=2, unique=True)

    def __str__(self):
        return f"{self.state} ({self.abbreviation})"

class Criterion(models.Model):
    AUCTION_TYPE_CHOICES = [
        ('tax deed', 'Tax Deed'),
        ('tax lien', 'Tax Lien'),
        ('both', 'Both'),
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
    ]

    auction_type = models.CharField(max_length=10, choices=AUCTION_TYPE_CHOICES)
    goal = models.CharField(max_length=15, choices=GOAL_CHOICES)
    states = models.ManyToManyField('States', limit_choices_to={'id__lte': 50})
    property_type = models.CharField(max_length=30, choices=PROPERTY_TYPE_CHOICES)
    market_value = models.DecimalField(max_digits=12, decimal_places=2)
    budget_face_value = models.DecimalField(max_digits=12, decimal_places=2)
    total_budget = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.auction_type} - {self.goal}"
