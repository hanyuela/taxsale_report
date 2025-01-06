from django.db import models
from property.models import Property
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class Holding(models.Model):
    BID_STATUS_CHOICES = [
        ('Bid', 'Bid'),
        ('Won', 'Won'),
        ('Foreclosed', 'Foreclosed'),
        ('Archived', 'Archived'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='holdings')  # 引用 Property 表
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='holdings')  # 引用 User 表
    my_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # 竞标金额（美元）
    my_bid_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # 竞标百分比
    status = models.CharField(max_length=20, choices=BID_STATUS_CHOICES)
    note = models.TextField(max_length=50, blank=True)  # 备注，最多50个字符

    def __str__(self):
        return f"{self.property.name} - {self.status} - {self.user.username}"

    class Meta:
        verbose_name = 'Holding'
        verbose_name_plural = 'Holdings'




class UserInput(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='user_inputs')  # 引用 Property 表
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_inputs')  # 引用 User 表
    street_address = models.CharField(max_length=255, blank=True)  # 完整地址
    auction_authority = models.CharField(max_length=255, blank=True)  # 拍卖方
    state = models.CharField(max_length=50, blank=True)  # 所属州
    amount_in_sale = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # 售卖金额
    deposit_deadline = models.DateField(null=True, blank=True)  # 定金截止日期
    auction_start = models.DateField(null=True, blank=True)  # 拍卖开始日期
    auction_end = models.DateField(null=True, blank=True)  # 拍卖结束日期
    city = models.CharField(max_length=100)
    zip = models.CharField(max_length=20)
    
    # 新添加的字段
    batch_number = models.CharField(max_length=50, blank=True)  # 批次号
    sort_no = models.CharField(max_length=50, blank=True)  # 排序号
    bankruptcy_flag = models.BooleanField(default=False)  # 是否破产标记
    parcel_number = models.CharField(max_length=50, blank=True)  # 地块编号
    property_class = models.CharField(max_length=255, blank=True)  # 房产类型
    tax_overdue = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # 欠税
    accessed_land_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # 土地评估价值
    accessed_improvement_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # 改良评估价值
    total_assessed_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # 总评估价值
    tax_amount_annual = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # 年税额
    zillow_link = models.URLField(max_length=255, blank=True, null=True)  # Zillow 链接
    redfin_link = models.URLField(max_length=255, blank=True, null=True)  # Redfin 链接
    Market_Land_Value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # 市场土地价值
    Market_Improvement_Value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # 市场改良价值
    Total_Market_Value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # 总市场价值
    year_built = models.IntegerField(null=True, blank=True)  # 建造年份
    lot_size_sqft = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # 地块大小（平方英尺）
    lot_size_acres = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # 地块大小（英亩）
    building_size_sqft = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # 建筑大小（平方英尺）
    bedroom_number = models.IntegerField(null=True, blank=True)  # 卧室数量
    bathroom_number = models.IntegerField(null=True, blank=True)  # 浴室数量
    nearby_schools = models.CharField(max_length=255, blank=True, null=True)  # 附近学校
    walk_score = models.IntegerField(null=True, blank=True)  # 步行分数
    transit_score = models.IntegerField(null=True, blank=True)  # 交通分数
    bike_score = models.IntegerField(null=True, blank=True)  # 骑行分数
    environmental_hazard_status = models.CharField(max_length=100, blank=True, null=True)  # 环境危险状况
    flood_status = models.CharField(max_length=100, blank=True, null=True)  # 洪水状态
    flood_risk = models.CharField(max_length=100, blank=True, null=True)  # 洪水风险
    latest_sale_date = models.DateField(null=True, blank=True)  # 最新销售日期
    latest_sale_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # 最新销售价格

    def __str__(self):
        return f"{self.property.name} - {self.user.username}"

    class Meta:
        verbose_name = 'User Input'
        verbose_name_plural = 'User Inputs'
