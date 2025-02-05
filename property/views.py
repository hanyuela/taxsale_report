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
from django.shortcuts import redirect
# Create your views here.

@login_required
def datatable(request):
    # 获取当前用户的 UserProfile
    user_profile = request.user.profile

    # 检查 member 字段的值
    if user_profile.member == 0:
        return redirect('index')  # 重定向到订阅页面

    PROPERTY_TYPE_MAPPING = {
        "single_family_residential": "Single Family Residential",
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

    # 筛选 Auction 表中 auction_end 晚于今天的数据
    today = datetime.now()
    auctions = Auction.objects.filter(auction_end__gt=today).prefetch_related('properties')

    # 如果用户有筛选条件
    if user_criteria:
        # 按 states 筛选
        if user_criteria.states.exists():
            state_ids = user_criteria.states.values_list('id', flat=True)
            # 获取对应的缩写和全称
            states = States.objects.filter(id__in=state_ids)
            
            # 提取出缩写和全称（假设全称字段是 state）
            abbreviations = states.values_list('abbreviation', flat=True)
            full_names = states.values_list('state', flat=True)  # 改成 'state' 字段

            # 将两者合并成一个集合
            all_states = set(abbreviations) | set(full_names)

            # 过滤 auctions，支持缩写和全称
            auctions = auctions.filter(properties__state__in=all_states)


        # 按 property_type 筛选
        if user_criteria.property_type:
            try:
                selected_property_types = ast.literal_eval(user_criteria.property_type)
                mapped_classes = [
                    PROPERTY_TYPE_MAPPING.get(pt)
                    for pt in selected_property_types
                    if PROPERTY_TYPE_MAPPING.get(pt)
                ]
                if mapped_classes:
                    auctions = auctions.filter(properties__property_class__in=mapped_classes)
            except (ValueError, SyntaxError):
                pass

        # 按 is_online 筛选
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

        # 按 auction_type 筛选
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
        
        # 按 accessed_land_value 筛选
        if user_criteria.Assessed_Land_Value_min is not None:
            auctions = auctions.filter(properties__accessed_land_value__gte=user_criteria.Assessed_Land_Value_min)
        if user_criteria.Assessed_Land_Value_max is not None:
            auctions = auctions.filter(properties__accessed_land_value__lte=user_criteria.Assessed_Land_Value_max)

        # 按 accessed_improvement_value 筛选
        if user_criteria.Assessed_Improvement_Value_min is not None:
            auctions = auctions.filter(properties__accessed_improvement_value__gte=user_criteria.Assessed_Improvement_Value_min)
        if user_criteria.Assessed_Improvement_Value_max is not None:
            auctions = auctions.filter(properties__accessed_improvement_value__lte=user_criteria.Assessed_Improvement_Value_max)

        # 按 total_assessed_value 筛选
        if user_criteria.Total_Assessed_Value_min is not None:
            auctions = auctions.filter(properties__total_assessed_value__gte=user_criteria.Total_Assessed_Value_min)
        if user_criteria.Total_Assessed_Value_max is not None:
            auctions = auctions.filter(properties__total_assessed_value__lte=user_criteria.Total_Assessed_Value_max)
            
        # 按 Market Land Value 筛选
        if user_criteria.Market_Land_Value_min is not None:
            auctions = auctions.filter(properties__Market_Land_Value__gte=user_criteria.Market_Land_Value_min)
        if user_criteria.Market_Land_Value_max is not None:
            auctions = auctions.filter(properties__Market_Land_Value__lte=user_criteria.Market_Land_Value_max)

        # 按 Market Improvement Value 筛选
        if user_criteria.Market_Improvement_Value_min is not None:
            auctions = auctions.filter(properties__Market_Improvement_Value__gte=user_criteria.Market_Improvement_Value_min)
        if user_criteria.Market_Improvement_Value_max is not None:
            auctions = auctions.filter(properties__Market_Improvement_Value__lte=user_criteria.Market_Improvement_Value_max)

        # 按 Total Market Value 筛选
        if user_criteria.Total_Market_Value_min is not None:
            auctions = auctions.filter(properties__Total_Market_Value__gte=user_criteria.Total_Market_Value_min)
        if user_criteria.Total_Market_Value_max is not None:
            auctions = auctions.filter(properties__Total_Market_Value__lte=user_criteria.Total_Market_Value_max)


    # 构造数据供模板渲染
    seen_properties = set()
    data = []

    for auction in auctions:
        for property in auction.properties.all():
            if property.id not in seen_properties:  # 检查是否已处理过
                seen_properties.add(property.id)
                data.append({
                    "city": property.city,
                    "state": property.state,
                    "property_type": property.property_class,
                    "is_online": auction.is_online,
                    "auction_type": auction.auction_type,
                    "amount_in_sale": property.face_value,
                    "deposit_deadline": auction.deposit_deadline,
                    "foreclose_score": property.foreclose_score,
                    "property_id": property.id,
                    "property_class": property.property_class,
                    "street_address": property.street_address
                })

    return render(request, "datatable.html", {
        "data": data,
        "user_criteria": user_criteria,  # 传递筛选条件，便于前端显示或调试
    })


@login_required
def report(request, property_id):
    # 获取指定 property_id 的 Property 对象
    try:
        property = Property.objects.select_related('auction').get(id=property_id)  # 关联 auction 数据
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
        'Total_Market_Value': property.Total_Market_Value,
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
            "auction_type": property.auction.auction_type,
            "face_value": property.face_value,
            "is_online": property.auction.is_online,
            "deposit_deadline": property.auction.deposit_deadline,
            "batch_number": property.batch_number,
            "sort_no": property.sort_no,
            "authority_name": property.auction.authority_name,
            "auction_start": property.auction.auction_start,
            "auction_end": property.auction.auction_end,
            "redemption_period": property.auction.redemption_period,
            "foreclosure_date": property.auction.foreclosure_date,
            "bankruptcy_flag": property.bankruptcy_flag,
            "auction_tax_year": property.auction.auction_tax_year,
        }
    ] if property.auction else []

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
