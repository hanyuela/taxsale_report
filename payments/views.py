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
from .models import Payment_history, Payment_method, BillingAddress, Coupon  # 导入 BillingAddress 模型
from django.db.models import Sum
from django.conf import settings
from authentication.models import UserProfile
from datetime import timedelta
from django.utils import timezone

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

    # 获取用户的订阅信息
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        user_profile = None

    if user_profile:
        if user_profile.member == 0:
            subscription = {
                "member_since": "Canceled",  # 取消订阅
                "payment_interval": "Non-Paid",  # 未付费
                "next_payment_on": "-",
                "next_payment_amount": "-"
            }
        elif user_profile.member == 1:  # 每月订阅
            if user_profile.member_start:  # 确保 member_start 不是 None
                subscription = {
                    "member_since": user_profile.member_start.strftime('%m/%d/%Y'),
                    "payment_interval": "Monthly",
                    "next_payment_on": get_next_payment_date(user_profile.member_start, monthly=True),
                    "next_payment_amount": 5.00  # 你可以根据实际情况调整金额
                }
            else:
                subscription = {
                    "member_since": "Unknown",
                    "payment_interval": "Unknown",
                    "next_payment_on": "-",
                    "next_payment_amount": "-"
                }
        elif user_profile.member == 2:  # 年度订阅
            if user_profile.member_start:  # 确保 member_start 不是 None
                subscription = {
                    "member_since": user_profile.member_start.strftime('%m/%d/%Y'),
                    "payment_interval": "Annually",
                    "next_payment_on": get_next_payment_date(user_profile.member_start, monthly=False),
                    "next_payment_amount": 50.00
                }
            else:
                subscription = {
                    "member_since": "Unknown",
                    "payment_interval": "Unknown",
                    "next_payment_on": "-",
                    "next_payment_amount": "-"
                }
        else:
            subscription = {
                "member_since": "Unknown",
                "payment_interval": "Unknown",
                "next_payment_on": "-",
                "next_payment_amount": "-"
            }
    else:
        subscription = {
            "member_since": "Unknown",
            "payment_interval": "Unknown",
            "next_payment_on": "-",
            "next_payment_amount": "-"
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

def get_next_payment_date(start_date, monthly=True):
    """
    根据开始日期计算下一次付款日期
    :param start_date: 订阅开始日期
    :param monthly: 如果是True，表示按月计算，否则表示按年计算
    :return: 下一次付款日期
    """
    if monthly:
        # 每月同一天支付，如果没有31号，提前调整
        next_payment = start_date.replace(year=start_date.year + (start_date.month == 12), month=(start_date.month % 12) + 1)
        if next_payment.day != start_date.day:
            # 调整为前一个月的最后一天
            next_payment = next_payment.replace(day=1) - timedelta(days=1)
    else:
        # 每年同一天支付
        next_payment = start_date.replace(year=start_date.year + 1)

    return next_payment.strftime('%m/%d/%Y')

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

            # 获取当前用户的 UserProfile
            try:
                user_profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                return JsonResponse({"success": False, "error": "User profile not found."})

            # 检查或创建 Stripe Customer
            if not user_profile.customer_id:
                # 创建 Stripe Customer
                customer = stripe.Customer.create(
                    email=request.user.email,
                    name=f"{request.user.first_name} {request.user.last_name}",
                )
                user_profile.customer_id = customer.id
                user_profile.save()

            # 确保 PaymentMethod 绑定到 Customer
            try:
                stripe.PaymentMethod.attach(
                    payment_method_id,
                    customer=user_profile.customer_id,
                )
            except stripe.error.InvalidRequestError as e:
                return JsonResponse({"success": False, "error": f"Failed to attach PaymentMethod: {e.user_message}"})

            # 设置 PaymentMethod 为默认支付方式
            try:
                stripe.Customer.modify(
                    user_profile.customer_id,
                    invoice_settings={
                        "default_payment_method": payment_method_id,
                    },
                )
            except stripe.error.InvalidRequestError as e:
                return JsonResponse({"success": False, "error": f"Failed to set default PaymentMethod: {e.user_message}"})

            # 创建 PaymentIntent，使用绑定的 PaymentMethod
            try:
                payment_intent = stripe.PaymentIntent.create(
                    amount=amount_in_cents,
                    currency="usd",
                    customer=user_profile.customer_id,  # 使用绑定的 Customer
                    payment_method=payment_method_id,  # 绑定的 PaymentMethod
                    off_session=True,  # 后台支付
                    confirm=True,  # 立即确认支付
                )
            except stripe.error.CardError as e:
                return JsonResponse({"success": False, "error": f"Card error: {e.user_message}"})
            except stripe.error.InvalidRequestError as e:
                return JsonResponse({"success": False, "error": f"Invalid request: {e.user_message}"})
            except stripe.error.StripeError as e:
                return JsonResponse({"success": False, "error": f"Stripe error: {e.user_message}"})

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

        except Exception as e:
            return JsonResponse({"success": False, "error": f"An unexpected error occurred: {str(e)}"})

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

def transactions(request):
    # Get all payment records
    payments = Payment_history.objects.all()

    return render(request, 'transactions.html',{'payments': payments})

def invoice(request):
    # Get all payment records
    
    return render(request, 'invoice.html')

@login_required
def cancel_subscription(request):
    try:
        # 获取当前用户的关联 UserProfile
        user_profile = request.user.profile  # 通过 OneToOne 关联获取 UserProfile
        user_profile.member = 0  # 设置为非付费用户
        user_profile.member_start = None  # 清空会员开始时间
        
        # 调试信息，查看当前数据
        print(f"User profile before saving: {user_profile.member_start}")
        
        user_profile.save()  # 保存更新

        # 调试信息，查看保存后的数据
        print(f"User profile after saving: {user_profile.member_start}")

        # 返回成功的 JSON 响应
        return JsonResponse({'success': True})

    except UserProfile.DoesNotExist:
        # 如果找不到 UserProfile，返回失败的 JSON 响应
        return JsonResponse({'success': False, 'error': 'UserProfile 未找到'})


def apply_coupon(request):
    if request.method == 'POST':
        try:
            # 获取用户输入的优惠券号码
            import json
            data = json.loads(request.body)
            coupon_code = data.get('coupon_code', '').strip()

            # 查找优惠券：有效且未被使用的优惠券
            coupon = Coupon.objects.get(code=coupon_code, is_used=False, expired__gt=timezone.now())

            # 更新优惠券的使用状态
            coupon.is_used = True
            coupon.user = request.user  # 关联当前用户
            coupon.save()

            # 记录付款记录到 Payment_history
            Payment_history.objects.create(
                user=request.user,
                amount=coupon.value,
                time=datetime.now().time(),
                date=datetime.now().date(),
                method="credit_card",  # 假设是信用卡支付
                type="add_funds",  # 添加资金
            )

            # 计算新的余额
            remaining_balance = Payment_history.objects.filter(user=request.user).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
            
            # 返回成功响应
            return JsonResponse({
                'success': True,
                'remaining_balance': remaining_balance
            })

        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid or expired coupon.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    # 如果不是 POST 请求，返回一个错误
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})
