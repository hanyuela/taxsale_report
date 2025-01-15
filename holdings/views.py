from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from property.models import Property,Auction
from django.http import JsonResponse
from holdings.models import Holding,UserInput
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render
import json

@login_required
def holdings(request):
    # 获取当前登录用户
    user = request.user

    # 获取当前用户的所有 Holding 记录
    agreements = Holding.objects.filter(user=user)

    # 获取所有关联的 Property 实例
    properties = Property.objects.filter(id__in=[agreement.property_id for agreement in agreements])

    # 获取与这些 Property 相关的 Auction 数据
    # 通过 'auction' 字段反向查询与每个 Property 相关联的 Auction 数据
    auctions = Auction.objects.filter(properties__in=properties)

    # 使用 select_related 来优化查询，避免 N+1 查询问题
    auctions = auctions.select_related('auction')  # 需要确认 Auction 是否与 Property 有关联

    # 渲染 holdings.html 页面
    return render(request, 'holdings.html', {
        'user': user,
        'agreements': agreements,
        'properties': properties,
        'auctions': auctions
    })


@login_required
def holdings_data(request):
    # 获取当前登录用户
    user = request.user

    # 获取筛选参数
    label_filter = request.GET.get('Label', '')  # 前端传递的筛选条件

    # 从 Holding 表中获取当前用户的唯一 property_id
    holdings_query = Holding.objects.filter(user=user)

    # 如果有 Label 筛选条件，则根据 status 字段进行过滤
    if label_filter and label_filter != "All":  # 忽略 "All"，返回所有
        if label_filter == "Archived":  # 处理 Archived 的特殊逻辑
            holdings_query = holdings_query.filter(status="Archived")
        else:
            holdings_query = holdings_query.exclude(status="Archived").filter(status=label_filter)
    else:
        # 如果是 All，排除 Archived 的行
        holdings_query = holdings_query.exclude(status="Archived")


    # 从 Holding 表中获取当前用户的唯一 property_id
    property_ids = Holding.objects.filter(user=user).values_list('property_id', flat=True).distinct()

    # 获取与这些 property_id 对应的 Properties
    properties = Property.objects.filter(id__in=property_ids)

    # 获取与这些 Properties 相关的 Auction 数据
    auctions = Auction.objects.filter(id__in=properties.values_list('auction_id', flat=True)).distinct()

    # 构造数据列表
    properties_list = []

    # 使用集合避免重复的 property_id
    seen_property_ids = set()

    for property in properties:

        # 获取与此 Property 相关的 Holding 数据（已经根据 label_filter 筛选过）
        holding = holdings_query.filter(property=property).first()

        # 只有符合筛选条件的 Holding 才能加入最终列表
        if not holding:
            continue
        
        # 确保每个 property 只处理一次
        if property.id in seen_property_ids:
            continue
        seen_property_ids.add(property.id)

        # 获取与此 Property 相关的 Holding
        holding = Holding.objects.filter(property=property, user=user).first()

        # 获取与此 Property 相关的 Auction
        auction = property.auction

        # 获取 UserInput 数据（优先显示 UserInput 中的数据）
        user_input = UserInput.objects.filter(property=property, user=user).first()

        # 构造数据，优先使用 UserInput 表中的值
        properties_list.append({
            'Address': user_input.street_address if user_input and user_input.street_address else property.street_address,
            'Auction Authority': user_input.auction_authority if user_input and user_input.auction_authority else (auction.authority_name if auction else ''),
            'State': user_input.state if user_input and user_input.state else property.state,
            'Amount In Sale': user_input.amount_in_sale if user_input and user_input.amount_in_sale else property.face_value,
            'Deposit Deadline': user_input.deposit_deadline if user_input and user_input.deposit_deadline else (auction.deposit_deadline if auction else ''),
            'Auction Start': user_input.auction_start if user_input and user_input.auction_start else (auction.auction_start if auction else ''),
            'Auction End': user_input.auction_end if user_input and user_input.auction_end else (auction.auction_end if auction else ''),
            'City': user_input.city if user_input and user_input.city else property.city,
            'Zip': user_input.zip if user_input and user_input.zip else property.zip,

            # 新添加的字段
            'Batch Number': user_input.batch_number if user_input and user_input.batch_number else property.batch_number,
            'Sort No': user_input.sort_no if user_input and user_input.sort_no else property.sort_no,
            'Bankruptcy Flag': user_input.bankruptcy_flag if user_input and user_input.bankruptcy_flag is not None else property.bankruptcy_flag,
            'Parcel Number': user_input.parcel_number if user_input and user_input.parcel_number else property.parcel_number,
            'Property Class': user_input.property_class if user_input and user_input.property_class else property.property_class,
            'Tax Overdue': user_input.tax_overdue if user_input and user_input.tax_overdue is not None else property.tax_overdue,
            'Accessed Land Value': user_input.accessed_land_value if user_input and user_input.accessed_land_value is not None else property.accessed_land_value,
            'Accessed Improvement Value': user_input.accessed_improvement_value if user_input and user_input.accessed_improvement_value is not None else property.accessed_improvement_value,
            'Total Assessed Value': user_input.total_assessed_value if user_input and user_input.total_assessed_value is not None else property.total_assessed_value,
            'Tax Amount Annual': user_input.tax_amount_annual if user_input and user_input.tax_amount_annual is not None else property.tax_amount_annual,
            'Zillow Link': user_input.zillow_link if user_input and user_input.zillow_link else property.zillow_link,
            'Redfin Link': user_input.redfin_link if user_input and user_input.redfin_link else property.redfin_link,
            'Market Land Value': user_input.Market_Land_Value if user_input and user_input.Market_Land_Value is not None else property.Market_Land_Value,
            'Market Improvement Value': user_input.Market_Improvement_Value if user_input and user_input.Market_Improvement_Value is not None else property.Market_Improvement_Value,
            'Total Market Value': user_input.Total_Market_Value if user_input and user_input.Total_Market_Value is not None else property.Total_Market_Value,
            'Year Built': user_input.year_built if user_input and user_input.year_built else property.year_built,
            'Lot Size (sqft)': user_input.lot_size_sqft if user_input and user_input.lot_size_sqft is not None else property.lot_size_sqft,
            'Lot Size (acres)': user_input.lot_size_acres if user_input and user_input.lot_size_acres is not None else property.lot_size_acres,
            'Building Size (sqft)': user_input.building_size_sqft if user_input and user_input.building_size_sqft is not None else property.building_size_sqft,
            'Bedroom Number': user_input.bedroom_number if user_input and user_input.bedroom_number is not None else property.bedroom_number,
            'Bathroom Number': user_input.bathroom_number if user_input and user_input.bathroom_number is not None else property.bathroom_number,
            'Nearby Schools': user_input.nearby_schools if user_input and user_input.nearby_schools else property.nearby_schools,
            'Walk Score': user_input.walk_score if user_input and user_input.walk_score is not None else property.walk_score,
            'Transit Score': user_input.transit_score if user_input and user_input.transit_score is not None else property.transit_score,
            'Bike Score': user_input.bike_score if user_input and user_input.bike_score is not None else property.bike_score,
            'Environmental Hazard Status': user_input.environmental_hazard_status if user_input and user_input.environmental_hazard_status else property.environmental_hazard_status,
            'Flood Status': user_input.flood_status if user_input and user_input.flood_status else property.flood_status,
            'Flood Risk': user_input.flood_risk if user_input and user_input.flood_risk else property.flood_risk,
            'Latest Sale Date': user_input.latest_sale_date if user_input and user_input.latest_sale_date else property.latest_sale_date,
            'Latest Sale Price': user_input.latest_sale_price if user_input and user_input.latest_sale_price else property.latest_sale_price,

            'My Bid': holding.my_bid if holding else "No My Bid",  # Holding 的 My Bid
            'Label': holding.status if holding else "No Bid",  # Holding 的状态
            'Note': holding.note if holding else "No Note",  # Holding 的备注

            'is_user_input': {
                'Address': bool(user_input and user_input.street_address),
                'Auction Authority': bool(user_input and user_input.auction_authority),
                'State': bool(user_input and user_input.state),
                'Amount In Sale': bool(user_input and user_input.amount_in_sale),
                'Deposit Deadline': bool(user_input and user_input.deposit_deadline),
                'Auction Start': bool(user_input and user_input.auction_start),
                'Auction End': bool(user_input and user_input.auction_end),
                'City': bool(user_input and user_input.city),
                'Zip': bool(user_input and user_input.zip),
                #新增
                'Batch Number': bool(user_input and user_input.batch_number),
                'Sort No': bool(user_input and user_input.sort_no),
                'Bankruptcy Flag': bool(user_input and user_input.bankruptcy_flag),
                'Parcel Number': bool(user_input and user_input.parcel_number),
                'Property Class': bool(user_input and user_input.property_class),
                'Tax Overdue': bool(user_input and user_input.tax_overdue),
                'Accessed Land Value': bool(user_input and user_input.accessed_land_value),
                'Accessed Improvement Value': bool(user_input and user_input.accessed_improvement_value),
                'Total Assessed Value': bool(user_input and user_input.total_assessed_value),
                'Tax Amount Annual': bool(user_input and user_input.tax_amount_annual),
                'Zillow Link': bool(user_input and user_input.zillow_link),
                'Redfin Link': bool(user_input and user_input.redfin_link),
                'Market Land Value': bool(user_input and user_input.Market_Land_Value),
                'Market Improvement Value': bool(user_input and user_input.Market_Improvement_Value),
                'Total Market Value': bool(user_input and user_input.Total_Market_Value),
                'Year Built': bool(user_input and user_input.year_built),
                'Lot Size (sqft)': bool(user_input and user_input.lot_size_sqft),
                'Lot Size (acres)': bool(user_input and user_input.lot_size_acres),
                'Building Size (sqft)': bool(user_input and user_input.building_size_sqft),
                'Bedroom Number': bool(user_input and user_input.bedroom_number),
                'Bathroom Number': bool(user_input and user_input.bathroom_number),
                'Nearby Schools': bool(user_input and user_input.nearby_schools),
                'Walk Score': bool(user_input and user_input.walk_score),
                'Transit Score': bool(user_input and user_input.transit_score),
                'Bike Score': bool(user_input and user_input.bike_score),
                'Environmental Hazard Status': bool(user_input and user_input.environmental_hazard_status),
                'Flood Status': bool(user_input and user_input.flood_status),
                'Flood Risk': bool(user_input and user_input.flood_risk),
                'Latest Sale Date': bool(user_input and user_input.latest_sale_date),
                'Latest Sale Price': bool(user_input and user_input.latest_sale_price),
            },
            'property_id': property.id,
        })

    # 返回 JSON 格式的数据
    return JsonResponse({'data': properties_list})






@login_required
@csrf_exempt
@require_POST
def update_holding_status(request):
    try:
        # 解析传入的 JSON 数据
        data = json.loads(request.body)

        # 获取传递的数据
        property_id = data.get('property_id')
        label = data.get('Label')
        note = data.get('Note')
        my_bid = data.get('My Bid')

        # 打印调试信息
        print("Received data:", data)

        # 确保 property_id 存在
        if not property_id:
            return JsonResponse({'status': 'error', 'message': 'Missing property_id'})

        # 验证 Label 是否为预期值
        valid_labels = ["Bid", "Won", "Foreclosed", "Archived"]
        if label and label not in valid_labels:
            return JsonResponse({'status': 'error', 'message': 'Invalid Label value'})

        # 限制 note 字段的长度
        if note and len(note) > 1000:
            return JsonResponse({'status': 'error', 'message': 'Note cannot exceed 1000 characters'})

        # 查找对应的 Holding 数据
        holding = Holding.objects.filter(property_id=property_id).first()
        if not holding:
            return JsonResponse({'status': 'error', 'message': 'Holding not found'})

        # 更新字段
        if label:
            holding.status = label
        if note:
            holding.note = note
        if my_bid:
            try:
                holding.my_bid = float(my_bid)
            except ValueError:
                return JsonResponse({'status': 'error', 'message': 'Invalid My Bid value'})

        holding.save()

        return JsonResponse({'status': 'success', 'message': 'Holding data updated successfully'})

    except Exception as e:
        print("Error:", str(e))  # 打印错误信息
        return JsonResponse({'status': 'error', 'message': str(e)})


@csrf_exempt
@login_required
def save_user_input(request):
    if request.method == "POST":
        try:
            # 解析请求数据
            data = json.loads(request.body)

            # 获取用户和 property_id
            property_id = data.get("property_id")
            user = request.user

            # 查找或创建 UserInput
            user_input, created = UserInput.objects.get_or_create(
                property_id=property_id,
                user=user
            )

            # 更新字段，只更新用户传递且修改过的字段
            updated_fields = []
            
            if "street_address" in data and data["street_address"] != user_input.street_address:
                user_input.street_address = data["street_address"]
                updated_fields.append("street_address")
            
            if "auction_authority" in data and data["auction_authority"] != user_input.auction_authority:
                user_input.auction_authority = data["auction_authority"]
                updated_fields.append("auction_authority")
            
            if "state" in data and data["state"] != user_input.state:
                user_input.state = data["state"]
                updated_fields.append("state")
            
            if "amount_in_sale" in data and data["amount_in_sale"] != str(user_input.amount_in_sale):
                user_input.amount_in_sale = float(data["amount_in_sale"])
                updated_fields.append("amount_in_sale")
            
            if "deposit_deadline" in data and data["deposit_deadline"] != str(user_input.deposit_deadline):
                user_input.deposit_deadline = data["deposit_deadline"]
                updated_fields.append("deposit_deadline")
            
            if "auction_start" in data and data["auction_start"] != str(user_input.auction_start):
                user_input.auction_start = data["auction_start"]
                updated_fields.append("auction_start")
            
            if "auction_end" in data and data["auction_end"] != str(user_input.auction_end):
                user_input.auction_end = data["auction_end"]
                updated_fields.append("auction_end")

            if "city" in data and data["city"] != str(user_input.city):
                user_input.city = data["city"]
                updated_fields.append("city")
            
            if "zip" in data and data["zip"] != str(user_input.zip):
                user_input.zip = data["zip"]
                updated_fields.append("zip")
            # 处理新的字段
            if "batch_number" in data and data["batch_number"] != user_input.batch_number:
                user_input.batch_number = data["batch_number"]
                updated_fields.append("batch_number")

            if "sort_no" in data and data["sort_no"] != user_input.sort_no:
                user_input.sort_no = data["sort_no"]
                updated_fields.append("sort_no")

            if "bankruptcy_flag" in data and str(data["bankruptcy_flag"]) != str(user_input.bankruptcy_flag):
                user_input.bankruptcy_flag = bool(data["bankruptcy_flag"])
                updated_fields.append("bankruptcy_flag")

            if "parcel_number" in data and data["parcel_number"] != user_input.parcel_number:
                user_input.parcel_number = data["parcel_number"]
                updated_fields.append("parcel_number")

            if "property_class" in data and data["property_class"] != user_input.property_class:
                user_input.property_class = data["property_class"]
                updated_fields.append("property_class")

            if "tax_overdue" in data and data["tax_overdue"] != str(user_input.tax_overdue):
                user_input.tax_overdue = float(data["tax_overdue"])
                updated_fields.append("tax_overdue")

            if "accessed_land_value" in data and data["accessed_land_value"] != str(user_input.accessed_land_value):
                user_input.accessed_land_value = float(data["accessed_land_value"])
                updated_fields.append("accessed_land_value")

            if "accessed_improvement_value" in data and data["accessed_improvement_value"] != str(user_input.accessed_improvement_value):
                user_input.accessed_improvement_value = float(data["accessed_improvement_value"])
                updated_fields.append("accessed_improvement_value")

            if "total_assessed_value" in data and data["total_assessed_value"] != str(user_input.total_assessed_value):
                user_input.total_assessed_value = float(data["total_assessed_value"])
                updated_fields.append("total_assessed_value")

            if "tax_amount_annual" in data and data["tax_amount_annual"] != str(user_input.tax_amount_annual):
                user_input.tax_amount_annual = float(data["tax_amount_annual"])
                updated_fields.append("tax_amount_annual")

            if "zillow_link" in data and data["zillow_link"] != user_input.zillow_link:
                user_input.zillow_link = data["zillow_link"]
                updated_fields.append("zillow_link")

            if "redfin_link" in data and data["redfin_link"] != user_input.redfin_link:
                user_input.redfin_link = data["redfin_link"]
                updated_fields.append("redfin_link")

            if "market_land_value" in data and data["market_land_value"] != str(user_input.Market_Land_Value):
                user_input.Market_Land_Value = float(data["market_land_value"])
                updated_fields.append("market_land_value")

            if "market_improvement_value" in data and data["market_improvement_value"] != str(user_input.Market_Improvement_Value):
                user_input.Market_Improvement_Value = float(data["market_improvement_value"])
                updated_fields.append("market_improvement_value")

            if "total_market_value" in data and data["total_market_value"] != str(user_input.Total_Market_Value):
                user_input.Total_Market_Value = float(data["total_market_value"])
                updated_fields.append("total_market_value")

            if "year_built" in data and data["year_built"] != str(user_input.year_built):
                user_input.year_built = int(data["year_built"])
                updated_fields.append("year_built")

            if "lot_size_sqft" in data and data["lot_size_sqft"] != str(user_input.lot_size_sqft):
                user_input.lot_size_sqft = float(data["lot_size_sqft"])
                updated_fields.append("lot_size_sqft")

            if "lot_size_acres" in data and data["lot_size_acres"] != str(user_input.lot_size_acres):
                user_input.lot_size_acres = float(data["lot_size_acres"])
                updated_fields.append("lot_size_acres")

            if "building_size_sqft" in data and data["building_size_sqft"] != str(user_input.building_size_sqft):
                user_input.building_size_sqft = float(data["building_size_sqft"])
                updated_fields.append("building_size_sqft")

            if "bedroom_number" in data and data["bedroom_number"] != str(user_input.bedroom_number):
                user_input.bedroom_number = int(data["bedroom_number"])
                updated_fields.append("bedroom_number")

            if "bathroom_number" in data and data["bathroom_number"] != str(user_input.bathroom_number):
                user_input.bathroom_number = int(data["bathroom_number"])
                updated_fields.append("bathroom_number")

            if "nearby_schools" in data and data["nearby_schools"] != user_input.nearby_schools:
                user_input.nearby_schools = data["nearby_schools"]
                updated_fields.append("nearby_schools")

            if "walk_score" in data and data["walk_score"] != str(user_input.walk_score):
                user_input.walk_score = int(data["walk_score"])
                updated_fields.append("walk_score")

            if "transit_score" in data and data["transit_score"] != str(user_input.transit_score):
                user_input.transit_score = int(data["transit_score"])
                updated_fields.append("transit_score")

            if "bike_score" in data and data["bike_score"] != str(user_input.bike_score):
                user_input.bike_score = int(data["bike_score"])
                updated_fields.append("bike_score")

            if "environmental_hazard_status" in data and data["environmental_hazard_status"] != user_input.environmental_hazard_status:
                user_input.environmental_hazard_status = data["environmental_hazard_status"]
                updated_fields.append("environmental_hazard_status")

            if "flood_status" in data and data["flood_status"] != user_input.flood_status:
                user_input.flood_status = data["flood_status"]
                updated_fields.append("flood_status")

            if "flood_risk" in data and data["flood_risk"] != user_input.flood_risk:
                user_input.flood_risk = data["flood_risk"]
                updated_fields.append("flood_risk")

            if "latest_sale_date" in data and data["latest_sale_date"] != str(user_input.latest_sale_date):
                user_input.latest_sale_date = data["latest_sale_date"]
                updated_fields.append("latest_sale_date")

            if "latest_sale_price" in data and data["latest_sale_price"] != str(user_input.latest_sale_price):
                user_input.latest_sale_price = float(data["latest_sale_price"])
                updated_fields.append("latest_sale_price")
            # 如果有更新字段才保存
            if updated_fields:
                user_input.save()
                print(f"Updated fields: {updated_fields}")

            return JsonResponse({"status": "success", "message": "Data saved successfully."})
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request."})

