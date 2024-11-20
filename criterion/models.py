from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User



class States(models.Model):
    state = models.CharField(max_length=50, unique=True)
    abbreviation = models.CharField(max_length=2, unique=True)

    def __str__(self):
        return f"{self.state} ({self.abbreviation})"

class Criterion(models.Model):
    # 添加外键关联到用户表
    user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    null=True,  # 允许为空
    blank=True,
    default=None  # 默认值为空
    )

    # Timestamp fields
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间，仅保留 auto_now_add
    updated_at = models.DateTimeField(auto_now=True)  # 更新时间

    # Auction type choices
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
    # Property type choices (多选存储为逗号分隔的字符串)
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


    # Fields
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

    # 市场价值和预算字段改为 CharField
    market_value = models.CharField(
        max_length=20, null=True, blank=True, default=""
    )
    budget_face_value = models.CharField(
        max_length=20, null=True, blank=True, default=""
    )
    
    # Relationships
    states = models.ManyToManyField(
        'States', blank=True
    )  # 感兴趣的州（多对多关系）

    def __str__(self):
        return f"{self.auction_type or 'No Auction Type'} - {self.goal or 'No Goal'}"


    def get_property_types(self):
        """
        返回解析后的房产类型列表
        """
        return self.property_type.split(",") if self.property_type else []