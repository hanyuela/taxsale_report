from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from payments.models import Payment_method, Payment_history, BillingAddress
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
import json
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Payment_history, Payment_method, BillingAddress  # 导入 BillingAddress 模型
from django.db.models import Sum
from django.conf import settings

@login_required
def payments(request):
    """
    显示支付中心
    """
    user = request.user

    # 查询用户的付款记录和支付方式
    payment_history = Payment_history.objects.filter(user=user).order_by('-date', '-time')
    payment_methods = Payment_method.objects.filter(user=user)

    # 查询用户的账单地址
    billing_addresses = BillingAddress.objects.filter(user=user)

    # 计算用户的 remaining_balance（总余额）
    remaining_balance = Payment_history.objects.filter(user=user).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

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
        "billing_addresses": billing_addresses,  # 将账单地址传递到模板
        "remaining_balance": remaining_balance,  # 将余额传递到模板
        "subscription": subscription,
        "stripe_publishable_key": settings.STRIPE_TEST_PUBLISHABLE_KEY,
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




stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

@csrf_exempt
@login_required
def save_payment_method(request):
    """
    接收前端发送的 PaymentMethod ID 并保存
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            payment_method_id = data.get("payment_method_id")

            if not payment_method_id:
                return JsonResponse({"success": False, "error": "No PaymentMethod ID provided"})

            # 验证 PaymentMethod 是否存在于 Stripe
            try:
                payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
            except stripe.error.InvalidRequestError:
                return JsonResponse({"success": False, "error": "Invalid PaymentMethod ID"})

            # 保存到数据库
            Payment_method.objects.create(
                user=request.user,
                method="stripe",  # 标记支付方式类型为 Stripe
                stripe_payment_method_id=payment_method_id,
            )

            return JsonResponse({"success": True, "message": "Payment method saved successfully!"})

        except stripe.error.StripeError as e:
            # 捕获 Stripe API 错误
            return JsonResponse({"success": False, "error": f"Stripe error: {e.user_message}"})
        except Exception as e:
            # 捕获其他异常
            return JsonResponse({"success": False, "error": f"An error occurred: {str(e)}"})

    return JsonResponse({"success": False, "error": "Invalid request method"})

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


@csrf_exempt
@login_required
def process_payment(request):
    """
    处理模拟支付操作
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            payment_method_id = data.get("payment_method_id")
            billing_address_id = data.get("billing_address_id")
            amount = data.get("amount")  # 用户充值的金额

            # 校验数据完整性
            if not payment_method_id or not billing_address_id or not amount:
                return JsonResponse({"success": False, "error": "Missing required fields"})

            # 校验支付方式是否属于当前用户
            try:
                # 假设payment_method_id是支付方式的标识符（如credit_card, paypal等）
                payment_method = Payment_method.objects.get(user=request.user, method=payment_method_id)
            except Payment_method.DoesNotExist:
                return JsonResponse({"success": False, "error": "Invalid payment method"})

            # 校验账单地址是否属于当前用户
            try:
                billing_address = BillingAddress.objects.get(user=request.user, id=billing_address_id)
            except BillingAddress.DoesNotExist:
                return JsonResponse({"success": False, "error": "Invalid billing address"})

            # 模拟支付成功，向 Payment_history 添加记录
            Payment_history.objects.create(
                user=request.user,
                amount=amount,  # 用户充值金额
                payment_method=payment_method.method,  # 支付方式
                billing_address=billing_address,  # 使用的账单地址
                status="success",  # 支付状态（可自定义）
            )

            # 重新计算用户的 remaining_balance
            remaining_balance = Payment_history.objects.filter(user=request.user).aggregate(
                total_amount=Sum('amount')
            )['total_amount'] or 0

            return JsonResponse({
                "success": True,
                "message": "Payment processed successfully!",
                "new_balance": remaining_balance,  # 返回新的总余额
            })

        except Exception as e:
            return JsonResponse({"success": False, "error": f"An error occurred: {str(e)}"})

    return JsonResponse({"success": False, "error": "Invalid request method"})
