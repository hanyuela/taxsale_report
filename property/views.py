from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from criterion.models import Criterion, States
from property.models import Property, Auction, PropertyUserAgreement
import ast
from django.http import JsonResponse
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
    auctions = Auction.objects.select_related('property').all()

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
            "property_id":auction.property_id
        })

    return render(request, "datatable.html", {
        "data": data,
        "user_criteria": user_criteria,  # 传递筛选条件，便于前端显示或调试
    })



@login_required
def report(request):
    return render(request, 'report.html')

@login_required
def agree_to_view(request):
    if request.method == "POST":
        # 获取传递的 property_id 和 user_id
        property_id = request.POST.get('property_id')  # 从 POST 数据中获取 property_id
        default = request.POST.get('default') == 'true'  # 获取是否选择默认同意付费

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

            # 创建或更新 PropertyUserAgreement 记录
            agreement, created = PropertyUserAgreement.objects.get_or_create(
                property=property,
                user=request.user,  # 使用当前登录的用户
                defaults={"default": default}  # 如果选择默认付费，存储为 True
            )

            if not created:
                print("Agreement already exists.")
                return JsonResponse({"error": "Agreement already exists."})

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
                    print("Holding record already exists.")
            except Exception as e:
                print(f"Error while creating Holding record: {str(e)}")
                return JsonResponse({"error": f"Error while creating Holding record: {str(e)}"})

            print("Successfully created PropertyUserAgreement record.")
            return JsonResponse({"success": True})

        except Property.DoesNotExist:
            return JsonResponse({"error": "Property not found."})
        except Exception as e:
            return JsonResponse({"error": f"Unexpected error: {str(e)}"})

    return JsonResponse({"error": "Invalid request method."})


