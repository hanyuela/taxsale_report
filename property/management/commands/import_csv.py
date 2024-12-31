from django.utils.dateparse import parse_date
from decimal import Decimal
import pandas as pd
from django.core.management.base import BaseCommand
from django.apps import apps
from datetime import datetime
import os
from decimal import Decimal, InvalidOperation
import re

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
        # 定义可选的 auction_id 参数
        parser.add_argument(
            '--auction_id',
            type=int,
            help='绑定的 Auction ID（可选）',
        )


    def handle(self, *args, **options):
        # 动态加载模型
        Auction = apps.get_model('property', 'Auction')
        Property = apps.get_model('property', 'Property')
        Owner = apps.get_model('property', 'Owner')
        Loan = apps.get_model('property', 'Loan')  # 动态加载 Loan 模型

        # 获取文件路径参数
        file_path = options['file_path']
        auction_id = options.get('auction_id')  # 获取可选的 auction_id 参数

        if not os.path.exists(file_path):  # 检查文件路径是否存在
            self.stdout.write(self.style.ERROR(f"文件路径不存在：{file_path}"))
            return

        try:
            # 如果传递了 auction_id，使用现有的 Auction
            if auction_id:
                try:
                    auction = Auction.objects.get(id=auction_id)
                    self.stdout.write(self.style.SUCCESS(f"使用现有 Auction，ID: {auction.id}"))
                except Auction.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Auction ID {auction_id} 不存在"))
                    return
            else:
                # 创建 Auction 实例（如果没有提供 auction_id）
                auction_data = {
                    "auction_tax_year": "2024",  # 示例数据
                    "auction_type": "tax lien",
                    "is_online": "online",
                    "deposit_deadline": None,
                    "auction_start": None,
                    "auction_end": None,
                    "redemption_period": None,
                    "foreclosure_date": None,
                    "authority_name": "Example Authority",  # 示例数据
                }

                # 创建并保存 Auction
                auction = Auction.objects.create(**auction_data)
                self.stdout.write(self.style.SUCCESS(f"新建 Auction，ID: {auction.id}"))

            # 读取 CSV 文件
            df = pd.read_csv(file_path, encoding='utf-8')
            self.stdout.write(self.style.SUCCESS(f"成功读取文件：{file_path}"))

            
            # 遍历每一行数据并创建 Property
            for index, row in df.iterrows():
                self.stdout.write(f"正在处理第 {index + 1} 行数据: {row.to_dict()}")

                try:
                    # 获取 Property 数据并绑定到 Auction
                    property_address = self.safe_string(row.get('Property Address', ''))
                    city = self.safe_string(row.get('Municipality', ''))
                    state = self.safe_string(row.get('State', ''))
                    parcel_number = self.safe_string(row.get('Parcel Id', ''))

                    # 检查是否存在相同的 property_address+city+state 或 parcel_number
                    existing_property = Property.objects.filter(
                        street_address=property_address,
                        city=city,
                        state=state
                    ).first() or Property.objects.filter(parcel_number=parcel_number).first()

                    if existing_property:
                        self.stdout.write(self.style.WARNING(
                            f"跳过重复的 Property: Address={property_address}, City={city}, State={state}, Parcel={parcel_number}"
                        ))
                        continue  # 跳过当前记录

                    # 构建 property_data 字典
                    property_data = {
                        'auction': auction,
                        'face_value': self.safe_decimal(row.get('Amount', 0)),
                        'batch_number': self.safe_string(row.get('Batch Number', '')),
                        'sort_no': self.safe_string(row.get('Sort No', '')),
                        'bankruptcy_flag': row.get('Bankruptcy Flag', 'False') == 'True',
                        'street_address': property_address,
                        'city': city,
                        'state': state,
                        'zip': self.safe_string(row.get('Location Zip 4', '00000')),
                        'block': self.safe_string(row.get('Block', '')),
                        'lot': self.safe_string(row.get('Lot', '')),
                        'latitude': self.safe_string(row.get('Latitude', '')),
                        'longitude': self.safe_string(row.get('Longitude', '')),
                        'parcel_number': parcel_number,
                        'property_class': self.safe_string(row.get('Standardized Land Use Desc', '')),
                        'tax_overdue': self.safe_decimal(row.get('Property Tax Principal', 0)),
                        'accessed_land_value': self.safe_decimal(row.get('Assessed Land Value', 0)),
                        'accessed_improvement_value': self.safe_decimal(row.get('Assessed Improvement Value', 0)),
                        'total_assessed_value': self.safe_decimal(row.get('Total Assessed Value', 0)),
                        'tax_amount_annual': self.safe_decimal(row.get('Tax Amount', 0)),
                        'zillow_link': self.safe_string(row.get('zillow_link', '')),
                        'redfin_link': self.safe_string(row.get('redfin_link', '')),
                        'Market_Land_Value': self.safe_decimal(row.get('Market Land Value', 0)),
                        'Market_Improvement_Value': self.safe_decimal(row.get('Market Improvement Value', 0)),
                        'Total_Market_Value': self.safe_decimal(row.get('Total Market Value', 0)),
                        'year_built': self.safe_int(row.get('Year Built', 0)),
                        'lot_size_sqft': self.safe_decimal(row.get('Lot Size + Lot Size Unit', 0)),
                        'lot_size_acres': self.safe_decimal(row.get('Acres Scraped', 0)),
                        'building_size_sqft': self.safe_decimal(row.get('Bldg Sq Ft', 0)),
                        'bedroom_number': self.safe_int(row.get('Total Bedrooms', 0)),
                        'bathroom_number': self.safe_int(row.get('Total Bathrooms', 0)),
                        'nearby_schools': self.safe_string(row.get('nearby_schools', '')),
                        'walk_score': self.safe_int(row.get('walk_score', 0)),
                        'transit_score': self.safe_int(row.get('transit_score', 0)),
                        'bike_score': self.safe_int(row.get('bike_score', 0)),
                        'environmental_hazard_status': self.safe_string(row.get('Environmental Hazard Status', '')),
                        'flood_status': self.safe_string(row.get('Flood Status', '')),
                        'flood_risk': self.safe_string(row.get('Flood Risk', '')),
                        'latest_sale_date': self.parse_csv_date(row.get('Latest Sale Date', '')),
                        'latest_sale_price': self.safe_decimal(row.get('Latest Sale Price', 0)),
                        'qualifier': self.safe_string(row.get('Qualifer', '')),
                    }

                    # 创建 Property 实例
                    property_instance = Property.objects.create(**property_data)
                    self.stdout.write(self.style.SUCCESS(f"新建 Property: {property_instance.street_address}"))

                    # 处理 Loan 数据
                    try:
                        for loan_index in range(1, 3):  # 假设最多支持 Loan1 和 Loan2
                            loan_amount = self.safe_decimal(row.get(f'Loan{loan_index} Amount', 0))
                            loan_due_date = self.parse_csv_date(row.get(f'Loan{loan_index} Due Date', ''))
                            loan_type = self.safe_string(row.get(f'Loan{loan_index} Type', ''))

                            if not loan_amount and not loan_due_date and not loan_type:
                                continue

                            Loan.objects.create(
                                property=property_instance,
                                loan_amount=loan_amount,
                                loan_due_date=loan_due_date if loan_due_date else None,
                                loan_type=loan_type,
                            )

                            self.stdout.write(self.style.SUCCESS(
                                f"关联 Loan{loan_index} 到 Property ID {property_instance.id}: "
                                f"Amount={loan_amount}, Due Date={loan_due_date}, Type={loan_type}"
                            ))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"Loan 数据处理时出错: {e}"))

                    # 处理 Owner 数据
                    owner_name = self.safe_string(row.get('Owner Name'))
                    if owner_name:
                        try:
                            owner = Owner.objects.filter(name=owner_name).first()
                            if not owner:
                                owner = Owner.objects.create(
                                    name=owner_name,
                                    phone_1=self.safe_string(row.get('phone_1')),
                                    phone_2=self.safe_string(row.get('phone_2')),
                                    phone_3=self.safe_string(row.get('phone_3')),
                                    phone_4=self.safe_string(row.get('phone_4')),
                                    phone_5=self.safe_string(row.get('phone_5')),
                                    email_1=self.safe_string(row.get('email_1')),
                                    email_2=self.safe_string(row.get('email_2')),
                                    email_3=self.safe_string(row.get('email_3')),
                                    email_4=self.safe_string(row.get('email_4')),
                                    email_5=self.safe_string(row.get('email_5')),
                                    primary_address=self.safe_string(row.get('Owner Address + Owner City State Zip')),
                                    Homestead_Exemptions=self.safe_boolean(row.get('Homestead Exemptions')),
                                )
                                self.stdout.write(self.style.SUCCESS(f"新建 Owner: {owner.name}"))
                            property_instance.owners.add(owner)
                            self.stdout.write(self.style.SUCCESS(
                                f"关联 Owner(s): {[owner.name for owner in property_instance.owners.all()]}"
                            ))
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f"Owner 数据处理时出错: {e}"))

                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Property 数据处理时出错: {e}"))

            self.stdout.write(self.style.SUCCESS("数据导入完成"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"处理文件时出错：{e}"))



    def safe_decimal(self, value):
       
        try:
            # 检查是否为 NaN 或 None
            if value is None or (isinstance(value, float) and str(value).lower() == 'nan'):
                return Decimal(0)
            # 转换为字符串并清理数据
            cleaned_value = str(value).replace('$', '').replace(',', '').strip()
            # 如果清理后的值为空字符串，返回 Decimal(0)
            return Decimal(cleaned_value) if cleaned_value else Decimal(0)
        except (ValueError, InvalidOperation):  # 捕获 Decimal 转换失败的异常
            return Decimal(0)

    def safe_int(self, value):
        try:
            return int(value) if value else 0
        except Exception:
            return 0
    
    def safe_string(self, value):
        
        try:
            # 转换为字符串
            value_str = str(value).strip() if value else ''
            
            # 如果是类似 ZIP 数据的字段，提取纯数字部分
            if "zip" in value_str.lower():
                value_str = re.sub(r'[^\d]', '', value_str)  # 仅保留数字
            
            return value_str
        except Exception:
            return ''
        
    def safe_boolean(self, value):
        
        try:
            if value is None or str(value).lower() == 'nan':  # 如果值是 None 或 'nan'
                return None
            value_str = str(value).strip().lower()
            if value_str in ['true', '1', 'yes']:
                return True
            elif value_str in ['false', '0', 'no']:
                return False
            return bool(value)  # 默认转换为布尔值
        except Exception:
            return None

    def parse_csv_date(self, date_str):
        
        try:
            # 如果是空白值或 NaN，直接返回 None
            if not date_str or isinstance(date_str, float) or str(date_str).strip() == '':
                return None

            # 尝试解析 YYYY/MM/DD 格式
            return datetime.strptime(date_str.strip(), '%m/%d/%Y').date()
        except ValueError:
            try:
                # 尝试解析标准的 YYYY-MM-DD 格式
                return datetime.strptime(date_str.strip(), '%Y-%m-%d').date()
            except ValueError:
                # 如果无法解析，返回 None
                return None
