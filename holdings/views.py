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
        property_id = data.get('property_id')  # 获取传递的 property_id
        label = data.get('Label')  # 获取传递的 Label 数据
        note = data.get('Note')  # 获取传递的 Note 数据
        my_bid = data.get('My Bid')  # 获取传递的 My Bid 数据
        
        # 打印调试信息，查看接收到的参数
        print("Received data:")
        print(f"property_id: {property_id}")
        print(f"Label: {label}")
        print(f"Note: {note}")
        print(f"My Bid: {my_bid}")
        
        # 确保传递的数据有效
        if not property_id:
            return JsonResponse({'status': 'error', 'message': 'Missing property_id'})
        
        # 限制 note 字段最多 50 个字符
        if note and len(note) > 1000:
            return JsonResponse({'status': 'error', 'message': 'Note cannot exceed 1000 characters'})
        
        # 查找对应的 Holding 数据
        try:
            holding = Holding.objects.get(property_id=property_id)  # 查找对应的 Holding 数据
            
            # 更新字段
            if label:
                holding.status = label  # 更新 status 字段为传递的 Label
            if note:
                holding.note = note  # 更新 note 字段
            if my_bid:
                try:
                    holding.my_bid = float(my_bid)  # 转换 My Bid 为浮点数并更新
                except ValueError:
                    return JsonResponse({'status': 'error', 'message': 'Invalid My Bid value'})
            
            holding.save()  # 保存更新后的状态
            
        except Holding.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Holding not found'})

        return JsonResponse({'status': 'success', 'message': 'Holding data updated successfully'})

    except Exception as e:
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

            # 如果有更新字段才保存
            if updated_fields:
                user_input.save()
                print(f"Updated fields: {updated_fields}")

            return JsonResponse({"status": "success", "message": "Data saved successfully."})
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request."})

@login_required
def holdings1(request):
    return render(request,'holdings1.html')  # 用户未登录，重定向到登录页面