from django.utils.dateparse import parse_date
from decimal import Decimal
import pandas as pd
from django.core.management.base import BaseCommand
from django.apps import apps
from datetime import datetime
import os

class Command(BaseCommand):
    help = '导入 CSV 数据到数据库'
    def parse_csv_date(self, date_str):
        """
        解析日期字符串，将其转为 YYYY-MM-DD 格式。
        如果解析失败，则返回 None。
        """
        try:
            # 尝试解析 YYYY/MM/DD 格式
            return datetime.strptime(date_str.strip(), '%Y/%m/%d').date()
        except ValueError:
            try:
                # 尝试解析标准的 YYYY-MM-DD 格式
                return parse_date(date_str.strip())
            except Exception:
                # 如果无法解析，返回 None
                return None
    def add_arguments(self, parser):
        # 定义一个参数 file_path
        parser.add_argument(
            'file_path',
            type=str,
            help='CSV 文件路径'
        )

    def handle(self, *args, **options):
        # 动态加载模型
        Auction = apps.get_model('property', 'Auction')
        Property = apps.get_model('property', 'Property')
        Owner = apps.get_model('property', 'Owner')

        # 获取文件路径参数
        file_path = options['file_path']
        if not os.path.exists(file_path):  # 检查文件路径是否存在
            self.stdout.write(self.style.ERROR(f"文件路径不存在：{file_path}"))
            return

        try:
            # 读取 CSV 文件
            df = pd.read_csv(file_path, encoding='utf-8')
            self.stdout.write(self.style.SUCCESS(f"成功读取文件：{file_path}"))

            for index, row in df.iterrows():
                auction_data = {}
                property_data = {}

                # 打印当前行号和数据
                self.stdout.write(f"正在处理第 {index + 1} 行数据: {row.to_dict()}")

                # 获取 Auction 数据
                auction_data['auction_tax_year'] = row.get('auction_tax_year', '').strip()
                auction_data['auction_type'] = row.get('auction_type', '').strip()
                auction_data['is_online'] = row.get('is_online', '').strip()
                auction_data['deposit_deadline'] = self.parse_csv_date(row.get('deposit_deadline', '').strip())
                auction_data['auction_start'] = self.parse_csv_date(row.get('auction_start', '').strip())
                auction_data['auction_end'] = self.parse_csv_date(row.get('auction_end', '').strip())
                auction_data['redemption_period'] = row.get('redemption_period', '').strip()
                auction_data['foreclosure_date'] = self.parse_csv_date(row.get('foreclosure_date', '').strip())
                auction_data['authority_name'] = row.get('authority_name', '').strip()

                # 创建 Auction 实例
                try:
                    clean_auction_data = {field: value for field, value in auction_data.items() if value not in [None, "", "nan"]}
                    auction = Auction.objects.create(**clean_auction_data)
                    self.stdout.write(self.style.SUCCESS(
                        f"新建 Auction: {auction.authority_name} ({auction.auction_tax_year})"))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Auction 导入时出错: {e}"))
                    continue

                # 获取 Property 数据
                try:
                    property_data['auction'] = auction
                    property_data['face_value'] = row.get('face_value', 0)
                    property_data['batch_number'] = row.get('batch_number', '')
                    property_data['sort_no'] = row.get('sort_no', '')
                    property_data['bankruptcy_flag'] = row.get('bankruptcy_flag', 'False') == 'True'
                    property_data['street_address'] = row.get('property_location', '')
                    property_data['city'] = row.get('city', '')
                    property_data['state'] = row.get('state', '')
                    property_data['zip'] = row.get('zip', '00000')
                    property_data['parcel_number'] = row.get('parcel_number', '')
                    property_data['property_class'] = row.get('property_class', '')
                    property_data['tax_overdue'] = self.safe_decimal(row.get('tax_overdue', 0))
                    property_data['accessed_land_value'] = self.safe_decimal(row.get('accessed_land_value', 0))
                    property_data['accessed_improvement_value'] = self.safe_decimal(row.get('accessed_improvement_value', 0))
                    property_data['total_assessed_value'] = self.safe_decimal(row.get('total_assessed_value', 0))
                    property_data['tax_amount_annual'] = self.safe_decimal(row.get('tax_amount_annual', 0))
                    property_data['zillow_link'] = row.get('zillow_link', '')
                    property_data['redfin_link'] = row.get('redfin_link', '')
                    property_data['market_value'] = self.safe_decimal(row.get('market_value', 0))
                    property_data['year_built'] = row.get('year_built', 0)
                    property_data['lot_size_sqft'] = self.safe_decimal(row.get('lot_size_sqft', 0))
                    property_data['lot_size_acres'] = self.safe_decimal(row.get('lot_size_acres', 0))
                    property_data['building_size_sqft'] = self.safe_decimal(row.get('building_size_sqft', 0))
                    property_data['bedroom_number'] = self.safe_int(row.get('bedroom_number', 0))
                    property_data['bathroom_number'] = self.safe_int(row.get('bathroom_number', 0))
                    property_data['nearby_schools'] = row.get('nearby_schools', '')
                    property_data['walk_score'] = self.safe_int(row.get('walk_score', 0))
                    property_data['transit_score'] = self.safe_int(row.get('transit_score', 0))
                    property_data['bike_score'] = self.safe_int(row.get('bike_score', 0))
                    property_data['environmental_hazard_status'] = row.get('environmental_hazard_status', '')
                    property_data['flood_status'] = row.get('flood_status', '')
                    property_data['flood_risk'] = row.get('flood_risk', '')
                    property_data['latest_sale_date'] = self.parse_csv_date(row.get('latest_sale_date', '').strip())
                    property_data['latest_sale_price'] = self.safe_decimal(row.get('latest_sale_price', 0))
                    property_data['foreclose_score'] = self.safe_int(row.get('foreclose_score', 0))

                    # 创建 Property 实例
                    property_instance = Property.objects.create(**property_data)
                    self.stdout.write(self.style.SUCCESS(f"新建 Property: {property_instance.street_address}"))

                    # 获取 Owner 数据并关联到 Property
                    try:
                        owner_name = row.get('owner_name', '').strip()
                        if owner_name:
                            owner, created = Owner.objects.get_or_create(
                                name=owner_name,
                                defaults={
                                    'phone_1': '',
                                    'email_1': '',
                                    'primary_address': ''
                                }
                            )
                            property_instance.owners.add(owner)

                        self.stdout.write(self.style.SUCCESS(
                            f"关联 Owner(s): {[owner.name for owner in property_instance.owners.all()]}"
                        ))

                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"Owner 处理时出错: {e}"))
                        continue

                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Property 导入时出错: {e}"))
                    continue

            self.stdout.write(self.style.SUCCESS("数据导入完成"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"处理文件时出错：{e}"))


    def safe_decimal(self, value):
        try:
            return Decimal(value.replace('$', '').replace(',', '')) if value else Decimal(0)
        except Exception:
            return Decimal(0)

    def safe_int(self, value):
        try:
            return int(value) if value else 0
        except Exception:
            return 0
