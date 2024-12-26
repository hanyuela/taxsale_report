from django.shortcuts import render
from .models import Criterion, States
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def criterion(request):
    # 获取或创建当前用户的投资偏好
    user_criteria, created = Criterion.objects.get_or_create(user=request.user)
    all_states = States.objects.all()  # 获取所有州

    if request.method == 'POST':
        # 更新 Property Type（多选）
        property_types = request.POST.getlist('property_type')  # 获取所有选中的 property_type
        if property_types:
            user_criteria.property_type = property_types  # 假设 property_type 是 ArrayField
        else:
            user_criteria.property_type = []  # 如果没有选中，清空列表

        # 更新 Auction Type（多选）
        auction_types = request.POST.getlist('auction_type')  # 获取所有选中的 auction_type
        if auction_types:
            user_criteria.auction_type = auction_types  # 假设 auction_type 是 ArrayField
        else:
            user_criteria.auction_type = []  # 如果没有选中，清空列表

        # 更新 Auction Mode（多选）
        is_online_modes = request.POST.getlist('is_online')  # 获取所有选中的 is_online
        if is_online_modes:
            user_criteria.is_online = is_online_modes  # 假设 is_online 是 ArrayField
        else:
            user_criteria.is_online = []  # 如果没有选中，清空列表

        # 更新市场价值范围
        Total_Assessed_Value_min = request.POST.get('Total_Assessed_Value_min', None)
        Total_Assessed_Value_max = request.POST.get('Total_Assessed_Value_max', None)
        user_criteria.Total_Assessed_Value_min = Total_Assessed_Value_min if Total_Assessed_Value_min else None
        user_criteria.Total_Assessed_Value_max = Total_Assessed_Value_max if Total_Assessed_Value_max else None

        Assessed_Land_Value_min = request.POST.get('Assessed_Land_Value_min', None)
        Assessed_Land_Value_max = request.POST.get('Assessed_Land_Value_max', None)
        user_criteria.Assessed_Land_Value_min = Assessed_Land_Value_min if Assessed_Land_Value_min else None
        user_criteria.Assessed_Land_Value_max = Assessed_Land_Value_max if Assessed_Land_Value_max else None

        Assessed_Improvement_Value_min = request.POST.get('Assessed_Improvement_Value_min', None)
        Assessed_Improvement_Value_max = request.POST.get('Assessed_Improvement_Value_max', None)
        user_criteria.Assessed_Improvement_Value_min = Assessed_Improvement_Value_min if Assessed_Improvement_Value_min else None
        user_criteria.Assessed_Improvement_Value_max = Assessed_Improvement_Value_max if Assessed_Improvement_Value_max else None
        
        # 更新市场价值范围
        Market_Land_Value_min = request.POST.get('Market_Land_Value_min', None)
        Market_Land_Value_max = request.POST.get('Market_Land_Value_max', None)
        user_criteria.Market_Land_Value_min = Market_Land_Value_min if Market_Land_Value_min else None
        user_criteria.Market_Land_Value_max = Market_Land_Value_max if Market_Land_Value_max else None

        # 更新市场改善价值范围
        Market_Improvement_Value_min = request.POST.get('Market_Improvement_Value_min', None)
        Market_Improvement_Value_max = request.POST.get('Market_Improvement_Value_max', None)
        user_criteria.Market_Improvement_Value_min = Market_Improvement_Value_min if Market_Improvement_Value_min else None
        user_criteria.Market_Improvement_Value_max = Market_Improvement_Value_max if Market_Improvement_Value_max else None

        # 更新总市场价值范围
        Total_Market_Value_min = request.POST.get('Total_Market_Value_min', None)
        Total_Market_Value_max = request.POST.get('Total_Market_Value_max', None)
        user_criteria.Total_Market_Value_min = Total_Market_Value_min if Total_Market_Value_min else None
        user_criteria.Total_Market_Value_max = Total_Market_Value_max if Total_Market_Value_max else None

        # 更新面值范围
        face_value_min = request.POST.get('face_value_min', None)
        face_value_max = request.POST.get('face_value_max', None)
        user_criteria.face_value_min = face_value_min if face_value_min else None
        user_criteria.face_value_max = face_value_max if face_value_max else None

        # 更新选中的州
        state_ids = request.POST.getlist('states')  # 获取选中的州 ID
        if state_ids:
            selected_states = States.objects.filter(id__in=state_ids)
            user_criteria.states.set(selected_states)  # 更新多对多关系
        else:
            user_criteria.states.clear()  # 如果没有选择任何州，清空关联

        # 保存用户偏好
        user_criteria.save()

        # 添加成功消息
        messages.success(request, "Preferences updated successfully!")
        return redirect("criterion")  # 重定向到当前页面

    return render(request, "criterion.html", {
        "user_criteria": user_criteria,
        "all_states": all_states,
    })