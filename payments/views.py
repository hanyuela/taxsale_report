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
from authentication.models import UserProfile

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



def get_or_create_customer(user):
    """
    为用户获取或创建 Stripe Customer
    """
    profile, created = UserProfile.objects.get_or_create(user=user)
    if not profile.stripe_customer_id:
        # 创建 Stripe Customer
        customer = stripe.Customer.create(
            email=user.email,
            name=user.get_full_name(),
        )
        # 保存 Stripe Customer ID
        profile.stripe_customer_id = customer["id"]
        profile.save()
    return profile.stripe_customer_id

@csrf_exempt
@login_required
def process_payment(request):
    """
    处理支付请求
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # 获取请求数据
            payment_method_id = data.get("payment_method_id")
            billing_address_id = data.get("billing_address_id")
            amount = data.get("amount")

            # 校验数据完整性
            if not payment_method_id or not billing_address_id or not amount:
                return JsonResponse({"success": False, "error": "Missing required fields"})

            # 转换金额为分
            amount_in_cents = int(float(amount) * 100)

            # 获取或创建 Stripe Customer
            customer_id = get_or_create_customer(request.user)

            # 将 PaymentMethod 绑定到 Customer
            try:
                stripe.PaymentMethod.attach(
                    payment_method_id,
                    customer=customer_id,
                )
                # 设置为默认支付方式（可选）
                stripe.Customer.modify(
                    customer_id,
                    invoice_settings={"default_payment_method": payment_method_id},
                )
            except stripe.error.StripeError as e:
                return JsonResponse({"success": False, "error": f"Failed to attach PaymentMethod: {str(e)}"})

            # 创建 PaymentIntent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency="usd",
                customer=customer_id,  # 指定 Customer
                payment_method=payment_method_id,  # 指定绑定的 PaymentMethod
                off_session=True,  # 如果是后台处理支付
                confirm=True,  # 立即确认支付
            )

            # 检查支付状态
            if payment_intent.status == "requires_action":
                # 如果需要用户完成额外验证（例如 3D Secure）
                return JsonResponse({
                    "success": False,
                    "requires_action": True,
                    "client_secret": payment_intent.client_secret,
                })
            elif payment_intent.status == "succeeded":
                # 支付成功，记录到数据库
                Payment_history.objects.create(
                    user=request.user,
                    amount=amount,
                    time=datetime.now().time(),
                    date=datetime.now().date(),
                    method="credit_card",
                    type="add_funds",
                )
                return JsonResponse({"success": True, "message": "Payment succeeded!"})

            # 其他支付失败状态
            return JsonResponse({"success": False, "error": f"Payment failed: {payment_intent.status}"})

        except stripe.error.CardError as e:
            # Stripe 卡片错误（如卡片被拒）
            return JsonResponse({"success": False, "error": f"Card error: {str(e)}"})
        except stripe.error.StripeError as e:
            # Stripe 相关的其他错误
            return JsonResponse({"success": False, "error": f"Stripe error: {str(e)}"})
        except Exception as e:
            # 捕获其他未预见的错误
            return JsonResponse({"success": False, "error": f"An unexpected error occurred: {str(e)}"})

    # 如果请求方法不是 POST
    return JsonResponse({"success": False, "error": "Invalid request method"})


@csrf_exempt
@login_required
def get_payment_method_details(request):
    """
    获取指定 PaymentMethod 的详细信息 (卡号后四位和品牌)
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            payment_method_id = data.get("payment_method_id")

            if not payment_method_id:
                return JsonResponse({"success": False, "error": "Missing payment method ID."})

            # 使用 Stripe API 获取支付方式详细信息
            stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
            payment_method = stripe.PaymentMethod.retrieve(payment_method_id)

            # 提取卡片信息
            card_info = {
                "brand": payment_method["card"]["brand"].capitalize(),
                "last4": payment_method["card"]["last4"],
            }

            return JsonResponse({"success": True, "card_info": card_info})
        except stripe.error.InvalidRequestError as e:
            return JsonResponse({"success": False, "error": str(e)})
        except Exception as e:
            return JsonResponse({"success": False, "error": f"An error occurred: {str(e)}"})

    return JsonResponse({"success": False, "error": "Invalid request method."})


@csrf_exempt
@login_required
def delete_payment_method(request):
    """
    删除数据库中的支付方式记录
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            payment_method_id = data.get("payment_method_id")

            if not payment_method_id:
                return JsonResponse({"success": False, "error": "Missing payment method ID."})

            # 从数据库中查找支付方式
            payment_method = Payment_method.objects.filter(user=request.user, stripe_payment_method_id=payment_method_id).first()
            if not payment_method:
                return JsonResponse({"success": False, "error": "Invalid payment method ID."})

            # 删除支付方式记录
            payment_method.delete()

            return JsonResponse({"success": True, "message": "Payment method deleted successfully."})

        except Exception as e:
            return JsonResponse({"success": False, "error": f"An error occurred: {str(e)}"})

    return JsonResponse({"success": False, "error": "Invalid request method."})

@csrf_exempt
@login_required
def delete_billing_address(request):
    """
    删除用户的账单地址
    """
    if request.method == "POST":
        try:
            # 获取请求数据
            data = json.loads(request.body)
            address_id = data.get("address_id")

            if not address_id:
                return JsonResponse({"success": False, "error": "Missing address ID."})

            # 从数据库中查找地址
            address = BillingAddress.objects.filter(user=request.user, id=address_id).first()
            if not address:
                return JsonResponse({"success": False, "error": "Invalid address ID."})

            # 删除地址
            address.delete()

            return JsonResponse({"success": True, "message": "Address deleted successfully."})

        except Exception as e:
            return JsonResponse({"success": False, "error": f"An error occurred: {str(e)}"})

    return JsonResponse({"success": False, "error": "Invalid request method."})