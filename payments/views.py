from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from payments.models import Payment_method, Payment_history, BillingAddress
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
import json
from datetime import datetime
# 设置 Stripe 密钥
stripe.api_key = "your_stripe_secret_key"  # 在 settings.py 中配置更佳

@login_required
def payments(request):
    """
    显示支付中心
    """
    user = request.user

    # 查询用户的付款记录和支付方式
    payment_history = Payment_history.objects.filter(user=user).order_by('-date', '-time')
    payment_methods = Payment_method.objects.filter(user=user)

    # 示例的订阅信息
    subscription = {
        "member_since": "11/22/2024",  # 示例数据
        "payment_interval": "Monthly",  # 示例数据
        "next_payment_on": "12/21/2024",  # 示例数据
        "next_payment_amount": 5.00  # 示例数据
    }

    # 渲染数据到前端模板
    context = {
        "payment_history": payment_history,
        "payment_methods": payment_methods,
        "subscription": subscription,
    }
    return render(request, 'payments.html', context)

@csrf_exempt
def save_payment_details(request):
    if request.method == 'POST':
        # 获取支付方式相关字段
        payment_type = request.POST.get('payment_type')
        payment_amount = request.POST.get('payment_amount')
        payment_time = request.POST.get('payment_time')
        payment_date = request.POST.get('payment_date')
        payment_method = request.POST.get('payment_method')
        
        # 获取支付方式信息
        stripe_payment_method_id = request.POST.get('stripe_payment_method_id', '')
        
        # 获取账单地址相关字段
        full_name = request.POST.get('full_name')
        business_name = request.POST.get('business_name', '')
        address = request.POST.get('address')
        address_line_2 = request.POST.get('address_line_2', '')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        country_region = request.POST.get('country_region', 'United States')

        try:
            # 保存 Payment_history 记录
            payment = Payment_history.objects.create(
                user=request.user,
                amount=payment_amount,
                time=datetime.strptime(payment_time, '%H:%M').time(),
                date=datetime.strptime(payment_date, '%Y-%m-%d').date(),
                method=payment_method,
                type=payment_type
            )

            # 保存 Payment_method 记录
            if payment_method == 'stripe':
                Payment_method.objects.create(
                    user=request.user,
                    method=payment_method,
                    stripe_payment_method_id=stripe_payment_method_id
                )
            else:
                Payment_method.objects.create(
                    user=request.user,
                    method=payment_method
                )

            # 保存 BillingAddress 记录
            BillingAddress.objects.create(
                user=request.user,
                full_name=full_name,
                business_name=business_name,
                address=address,
                address_line_2=address_line_2,
                city=city,
                state=state,
                zip_code=zip_code,
                country_region=country_region
            )

            return JsonResponse({'success': True, 'message': 'Payment details saved successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


# 配置 Stripe 密钥
stripe.api_key = "your_secret_key"  # 替换为您的 Stripe Secret Key

@csrf_exempt
def save_payment_method(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # 使用 Stripe API 创建支付方式
            stripe_payment_method = stripe.PaymentMethod.create(
                type="card",
                card={
                    "number": data.get("card_number"),
                    "exp_month": data.get("expiry_date").split('/')[0],
                    "exp_year": "20" + data.get("expiry_date").split('/')[1],
                    "cvc": data.get("cvv"),
                },
            )

            # 保存到数据库
            Payment_method.objects.create(
                user=request.user,
                method="credit_card",
                stripe_payment_method_id=stripe_payment_method.id,
            )

            return JsonResponse({"success": True, "message": "Payment method saved successfully!"})
        except stripe.error.CardError as e:
            # 处理 Stripe 卡片错误
            return JsonResponse({"success": False, "message": f"Card error: {e.user_message}"})
        except stripe.error.StripeError as e:
            # 处理其他 Stripe API 错误
            return JsonResponse({"success": False, "message": f"Stripe error: {str(e)}"})
        except Exception as e:
            # 处理其他异常
            return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})

    return JsonResponse({"success": False, "message": "Invalid request method."})

@csrf_exempt
def save_billing_address(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # 保存到数据库
            BillingAddress.objects.create(
                user=request.user,
                full_name=data.get("full_name"),
                business_name=data.get("business_name", ""),
                address=data.get("address"),
                address_line_2=data.get("address_line_2", ""),
                city=data.get("city"),
                state=data.get("state"),
                zip_code=data.get("zip_code"),
                country_region=data.get("country_region", "United States"),
            )

            return JsonResponse({"success": True, "message": "Billing address saved successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
