from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from criterion.models import Criterion, States
from property.models import Property, Auction
import ast
from django.http import JsonResponse
from holdings.models import Holding
from datetime import datetime
from django.http import Http404
from .models import Property, User
from authentication.models import UserProfile
from holdings.models import Holding
# Create your views here.
@login_required
def datatable(request):
    PROPERTY_TYPE_MAPPING = {
        "single_family_residential": "Single-Family",
        "multi_family_residential": "Multi-Family",
        "other_residential": "Other Residential",
        "commercial": "Commercial",
        "vacant_land": "Vacant Land",
        "industrial": "Industrial",
        "agricultural": "Agricultural",
        "miscellaneous": "Miscellaneous",
    }

    AUCTION_TYPE_MAPPING = {
        "tax lien": "tax lien",
        "tax deed": "tax deed",
    }

    IS_ONLINE_MAPPING = {
        "online": "online",
        "in-person": "in-person",
    }

    # 获取当前用户的筛选条件
    user_criteria = Criterion.objects.filter(user=request.user).first()

    # 初始查询集
    # 初始查询集：筛选 Auction 表中 auction_end 晚于今天的数据
    today = datetime.now()
    auctions = Auction.objects.select_related('property').filter(auction_end__gt=today)

    # 如果用户有筛选条件
    if user_criteria:
        # 1. 按 states 筛选
        if user_criteria.states.exists():
            state_ids = user_criteria.states.values_list('id', flat=True)
            abbreviations = States.objects.filter(id__in=state_ids).values_list('abbreviation', flat=True)
            auctions = auctions.filter(property__state__in=abbreviations)

        # 2. 按 property_type 筛选
        if user_criteria.property_type:
            try:
                selected_property_types = ast.literal_eval(user_criteria.property_type)
                mapped_classes = [
                    PROPERTY_TYPE_MAPPING.get(pt)
                    for pt in selected_property_types
                    if PROPERTY_TYPE_MAPPING.get(pt)
                ]
                if mapped_classes:
                    auctions = auctions.filter(property__property_class__in=mapped_classes)
            except (ValueError, SyntaxError):
                pass

        # 3. 按 is_online 筛选
        if user_criteria.is_online:
            try:
                selected_online_modes = ast.literal_eval(user_criteria.is_online)
                mapped_modes = [
                    IS_ONLINE_MAPPING.get(mode)
                    for mode in selected_online_modes
                    if IS_ONLINE_MAPPING.get(mode)
                ]
                if mapped_modes:
                    auctions = auctions.filter(is_online__in=mapped_modes)
            except (ValueError, SyntaxError):
                pass

        # 4. 按 auction_type 筛选
        if user_criteria.auction_type:
            try:
                selected_auction_types = ast.literal_eval(user_criteria.auction_type)
                mapped_types = [
                    AUCTION_TYPE_MAPPING.get(atype)
                    for atype in selected_auction_types
                    if AUCTION_TYPE_MAPPING.get(atype)
                ]
                if mapped_types:
                    auctions = auctions.filter(auction_type__in=mapped_types)
            except (ValueError, SyntaxError):
                pass

        # 5. 按 market_value 筛选
        if user_criteria.market_value_min is not None:
            auctions = auctions.filter(property__market_value__gte=user_criteria.market_value_min)
        if user_criteria.market_value_max is not None:
            auctions = auctions.filter(property__market_value__lte=user_criteria.market_value_max)

    # 构造数据供模板渲染
    data = []
    for auction in auctions:
        data.append({
            "city": auction.property.city,
            "state": auction.property.state,
            "property_type": auction.property.property_class,
            "is_online": auction.is_online,
            "auction_type": auction.auction_type,
            "amount_in_sale": auction.face_value,
            "deposit_deadline": auction.deposit_deadline,
            "foreclose_score": auction.property.foreclose_score,
            "property_id":auction.property_id,
            "property_class":auction.property.property_class,
            "street_address":auction.property.street_address
        })

    return render(request, "datatable.html", {
        "data": data,
        "user_criteria": user_criteria,  # 传递筛选条件，便于前端显示或调试
    })



@login_required
def report(request, property_id):
    # 获取指定 property_id 的 Property 对象
    try:
        property = Property.objects.select_related().get(id=property_id)
    except Property.DoesNotExist:
        raise Http404("Property not found")
    
    # 计算 Full Address
    full_address = f"{property.street_address}, {property.city}, {property.state} {property.zip}"
    # 确定显示的链接
    primary_link = property.zillow_link if property.zillow_link else property.redfin_link
    # 构造 Property 数据
    lot_size = f"{property.lot_size_sqft} sqft" if property.lot_size_sqft else f"{property.lot_size_acres} acres"
    data = {
        'full_address': full_address,
        'parcel_number': property.parcel_number,
        'property_class': property.property_class,
        'tax_overdue': property.tax_overdue,
        'accessed_land_value': property.accessed_land_value,
        'accessed_improvement_value': property.accessed_improvement_value,
        'total_assessed_value': property.total_assessed_value,
        'tax_amount_annual': property.tax_amount_annual,
        'lot_size': lot_size,
        'primary_link': primary_link,  # 添加主链接字段
        'redfin_link': property.redfin_link,
        'market_value': property.market_value,
        'year_built': property.year_built,
        'building_size_sqft': property.building_size_sqft,
        'bedroom_number': property.bedroom_number,
        'bathroom_number': property.bathroom_number,
        'nearby_schools': property.nearby_schools,
        'walk_score': property.walk_score,
        'transit_score': property.transit_score,
        'bike_score': property.bike_score,
        'environmental_hazard_status': property.environmental_hazard_status,
        'flood_status': property.flood_status,
        'flood_risk': property.flood_risk,
        'latest_sale_date': property.latest_sale_date,
        'latest_sale_price': property.latest_sale_price,
        'foreclose_score': property.foreclose_score,
    }

    # 获取与 Property 关联的 Auction 数据
    auction_data = [
        {
            "auction_type": auction.auction_type,
            "face_value": auction.face_value,
            "is_online": auction.is_online,
            "deposit_deadline": auction.deposit_deadline,
            "batch_number": auction.batch_number,
            "sort_no": auction.sort_no,
            "authority_name": auction.authority_name,
            "auction_start": auction.auction_start,
            "auction_end": auction.auction_end,
            "redemption_period": auction.redemption_period,
            "foreclosure_date": auction.foreclosure_date,
            "bankruptcy_flag": auction.bankruptcy_flag,
            "auction_tax_year": auction.auction_tax_year,
        }
        for auction in property.auctions.all()
    ]

    # 添加 Auction 数据
    data['auctions'] = auction_data

    # 获取关联的 Owners 数据
    owner_data = [
        {
            "name": owner.name,
            "phone_1": owner.phone_1,
            "email_1": owner.email_1,
            "primary_address": owner.primary_address,
        }
        for owner in property.owners.all()
    ]

    # 添加 Owner 数据
    data['owners'] = owner_data

    # 获取 Loans 数据
    loans = property.loans.all()
    loan_data = [
        {
            "loan_amount": loan.loan_amount,
            "loan_due_date": loan.loan_due_date,
            "loan_type": loan.loan_type,
        }
        for loan in loans
    ]

    # 添加 Loan 数据到 data
    data['loans'] = loan_data
    
    # 渲染模板并传递数据
    return render(request, 'report.html', {'data': data})




@login_required
def agree_to_view(request):
    if request.method == "POST":
        # 获取传递的 property_id 和 default
        property_id = request.POST.get('property_id')
        default = request.POST.get('default') == 'true'  # 转换为布尔值

        # 获取竞标金额、竞标百分比、备注字段的值
        my_bid = request.POST.get('my_bid')  # 竞标金额
        my_bid_percentage = request.POST.get('my_bid_percentage')  # 竞标百分比
        note = request.POST.get('note')  # 备注

        print(f"Received POST request with property_id: {property_id}, default: {default}")
        print(f"Bid details: my_bid={my_bid}, my_bid_percentage={my_bid_percentage}, note={note}")

        # 输入验证
        if not property_id:
            return JsonResponse({"error": "Missing property_id."})

        try:
            # 查找对应的 Property
            try:
                property = Property.objects.get(id=property_id)
                print(f"Found Property: {property}")
            except Property.DoesNotExist:
                return JsonResponse({"error": "Property not found."})

            # 确保用户的 UserProfile 存在
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)
            user_profile.default = default  # 更新 default 值
            user_profile.save()  # 保存更改
            print(f"UserProfile default updated to: {default} (Created: {created})")

            # 尝试获取已存在的 holding 记录
            agreement = Holding.objects.filter(
                property=property,
                user=request.user,  # 使用当前登录的用户
            ).first()

            if agreement:
                print("Agreement already exists. Directly opening report.")
                # 如果同意记录已存在，直接返回报告 URL
                report_url = f"/report/{property_id}/"
                return JsonResponse({
                    "success": True,
                    "report_url": report_url,  # 返回报告的 URL
                    "agreement_exists": True,  # 标识同意记录已存在
                })


            # 处理 Holding 记录（仅根据 property_id 和当前用户创建）
            try:
                holding, holding_created = Holding.objects.get_or_create(
                    property=property,
                    user=request.user,  # 将当前用户 ID 存入 Holding 记录
                    defaults={
                        "status": "Bid",  # 默认状态
                        "my_bid": my_bid if my_bid else 0.00,  # 如果没有提供竞标金额，默认为 0.00
                        "my_bid_percentage": my_bid_percentage if my_bid_percentage else 0.00,  # 默认为 0.00
                        "note": note if note else "",  # 默认为空备注
                    }
                )

                if holding_created:
                    print("Successfully created Holding record.")
                else:
                    print("Holding record already exists. No update required.")
            except Exception as e:
                print(f"Error while creating Holding record: {str(e)}")
                return JsonResponse({"error": f"Error while creating Holding record: {str(e)}"})

            print("Successfully created/updated Holding record.")
            return JsonResponse({
                "success": True,
                "agreement_created": created,  # 是否是新创建的记录
                "holding_created": holding_created  # 是否是新创建的 Holding 记录
            })

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return JsonResponse({"error": f"Unexpected error: {str(e)}"})

    return JsonResponse({"error": "Invalid request method."})



@login_required
def check_agreement(request):
    if request.method == "GET":
        # 获取传递的 property_id 和 user_id
        property_id = request.GET.get('property_id')
        user_id = request.GET.get('user_id')

        print(f"Checking agreement for property_id: {property_id}, user_id: {user_id}")

        # 输入验证
        if not property_id or not user_id:
            return JsonResponse({"error": "Missing property_id or user_id."})

        try:
            # 查找对应的 Property 和 User
            property = Property.objects.get(id=property_id)
            user = User.objects.get(id=user_id)

            print(f"Found Property: {property}, User: {user}")

            # 检查 UserProfile 的 default 值
            try:
                user_profile = UserProfile.objects.get(user=user)
                default = user_profile.default  # 获取 default 值
                print(f"User default agreement: {default}")
            except UserProfile.DoesNotExist:
                default = False  # 如果 UserProfile 不存在，则认为默认值为 False
                print("UserProfile not found for the user. Default set to False.")

            # 查找是否存在同意记录
            agreement = Holding.objects.filter(
                property=property,
                user=user,
            ).exists()

            print(f"Agreement exists: {agreement}")

            return JsonResponse({
                "success": True,
                "default": default,  # 返回用户的 default 状态
                "agreement_exists": agreement,  # 返回是否已存在同意记录
                "report_url": f"/report/{property_id}/"  # 生成报告的 URL
            })

        except Property.DoesNotExist:
            return JsonResponse({"error": "Property not found."})
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found."})
        except Exception as e:
            return JsonResponse({"error": f"Unexpected error: {str(e)}"})

    return JsonResponse({"error": "Invalid request method."})
