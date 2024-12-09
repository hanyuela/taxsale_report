from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from criterion.models import Criterion, States
from property.models import Property, Auction, PropertyUserAgreement
import ast
from django.http import JsonResponse
from holdings.models import Holding
from datetime import datetime
from django.http import Http404
from .models import Property, Owner, PropertyUserAgreement, User
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





from .models import Property, Owner, PropertyUserAgreement

@login_required
def report(request, property_id):
    # 获取指定 property_id 的 Property 对象
    try:
        property = Property.objects.get(id=property_id)
    except Property.DoesNotExist:
        raise Http404("Property not found")

    # 获取 Property 对象的相关数据
    data = {
        'street_address': property.street_address,
        'city': property.city,
        'state': property.state,
        'zip': property.zip,
        'parcel_number': property.parcel_number,
        'property_class': property.property_class,
        'tax_overdue': property.tax_overdue,
        'accessed_land_value': property.accessed_land_value,
        'accessed_improvement_value': property.accessed_improvement_value,
        'total_assessed_value': property.total_assessed_value,
        'tax_amount_annual': property.tax_amount_annual,
        'zillow_link': property.zillow_link,
        'redfin_link': property.redfin_link,
        'market_value': property.market_value,
        'year_built': property.year_built,
        'lot_size_sqft': property.lot_size_sqft,
        'lot_size_acres': property.lot_size_acres,
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
        'users': property.users.all(),    # 获取所有的 users
    }

    # 手动查询 PropertyUserAgreement 中的关联记录
    property_owner_ids = property.owners.values_list('id', flat=True)

    # 根据 owner_id 获取 Owner 的详细信息
    owners = Owner.objects.filter(id__in=property_owner_ids)

    # 将 owners 添加到 data 中
    data['owners'] = owners

    # 渲染模板并传递数据
    return render(request, 'report.html', {'data': data})


@login_required
def agree_to_view(request):
    if request.method == "POST":
        # 获取传递的 property_id 和 user_id
        property_id = request.POST.get('property_id')
        default = request.POST.get('default') == 'true'

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
            property = Property.objects.get(id=property_id)

            print(f"Found Property: {property}")

            # 尝试获取已存在的 PropertyUserAgreement 记录
            agreement = PropertyUserAgreement.objects.filter(
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

            # 创建新的 PropertyUserAgreement 记录
            agreement, created = PropertyUserAgreement.objects.get_or_create(
                property=property,
                user=request.user,  # 使用当前登录的用户
                defaults={"default": default}  # 如果选择默认付费，存储为 True
            )

            if not created:
                print("Agreement already exists. Updating the agreement.")
                agreement.default = default
                agreement.save()

            # 处理 Holding 记录（仅根据 property_id 和当前用户创建）
            try:
                holding, holding_created = Holding.objects.get_or_create(
                    property=property,
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

            print("Successfully created/updated PropertyUserAgreement record.")
            return JsonResponse({
                "success": True,
                "agreement_created": created,  # 是否是新创建的记录
                "holding_created": holding_created  # 是否是新创建的 Holding 记录
            })

        except Property.DoesNotExist:
            return JsonResponse({"error": "Property not found."})
        except Exception as e:
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
            # 查找对应的 Property
            property = Property.objects.get(id=property_id)
            user = User.objects.get(id=user_id)

            print(f"Found Property: {property}, User: {user}")

            # 查找是否存在同意记录
            agreement = PropertyUserAgreement.objects.filter(
                property=property,
                user=user,
            ).exists()

            print(f"Agreement exists: {agreement}")

            return JsonResponse({
                "success": True,
                "agreement_exists": agreement,  # 返回是否已存在同意记录
            })

        except Property.DoesNotExist:
            return JsonResponse({"error": "Property not found."})
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found."})
        except Exception as e:
            return JsonResponse({"error": f"Unexpected error: {str(e)}"})

    return JsonResponse({"error": "Invalid request method."})
