from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from property.models import Property,Auction
from django.http import JsonResponse
from holdings.models import Holding
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render
import json

@login_required
def holdings(request):
    # 获取当前登录用户
    user = request.user

    agreements = Holding.objects.filter(user=user)

    properties = Property.objects.filter(id__in=[agreement.property_id for agreement in agreements])

    # 获取与这些 Property 相关的 Auction 数据
    auctions = Auction.objects.filter(property__in=properties)

    # 使用 select_related 来优化查询并获取关联数据
    auctions = auctions.select_related('property')

    # 渲染 holdings.html 页面
    return render(request, 'holdings.html', {'user': user})

@login_required
def holdings_data(request):
    # 获取当前登录用户
    user = request.user
 
    agreements = Holding.objects.filter(user=user)

    properties = Property.objects.filter(id__in=[agreement.property_id for agreement in agreements])

    # 获取与这些 Property 相关的 Auction 数据
    auctions = Auction.objects.filter(property__in=properties)

    # 使用 select_related 来优化查询并获取关联数据
    auctions = auctions.select_related('property')

    # 构造数据列表
    properties_list = []
    for auction in auctions:
        # 获取与此 Auction 相关的所有 Holding 条目
        holdings = Holding.objects.filter(property=auction.property)

        # 假设您需要获取第一个 Holding 的状态（如果有多个 Holding，可以根据需要处理）
        holding_status = holdings.first().status if holdings.exists() else "No Bid"
        holding_note = holdings.first().note if holdings.exists() else "No Note"
        holding_My_Bid= holdings.first().my_bid if holdings.exists() else "No My Bid"
        # 构造数据
        properties_list.append({
            'Full Address': auction.property.street_address,
            'Auction Authority': auction.authority_name,
            'State': auction.property.state,
            'Amount In Sale': auction.face_value,
            'Deposit Deadline': auction.deposit_deadline,
            'Auction Start': auction.auction_start,
            'Auction End': auction.auction_end,
            'My Bid': holding_My_Bid,  # 如果有出价信息，可以填入
            'Label': holding_status,  # 从相关的 Holding 获取状态
            'property_id': auction.property.id ,
            'Note': holding_note,
            
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

