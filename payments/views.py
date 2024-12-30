from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from payments.models import Payment_methd, Payment_history
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
import json

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
    payment_methods = Payment_methd.objects.filter(user=user)

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
@login_required
def add_funds(request):
    """
    添加资金（保存到 Payment_history）
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = data.get('amount')
            payment_method_id = data.get('payment_method_id')

            if not amount or float(amount) <= 0:
                return JsonResponse({'status': 'error', 'message': 'Invalid amount'})

            # 获取支付方式
            payment_method = Payment_methd.objects.get(id=payment_method_id, user=request.user)

            # 保存到 Payment_history
            Payment_history.objects.create(
                user=request.user,
                amount=amount,
                time=now().time(),
                date=now().date(),
                method=payment_method.method,
                type='add_funds',
            )
            return JsonResponse({'status': 'success', 'message': 'Funds added successfully!'})

        except Payment_methd.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid payment method'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def cancel_subscription(request):
    """
    取消用户的订阅
    """
    if request.method == 'POST':
        try:
            # 取消用户订阅逻辑（具体实现需要依赖业务）
            # 示例代码（假设有一个订阅模型，或直接通过 Stripe 管理订阅）
            subscription_id = "user_subscription_id"  # 示例，需从数据库中获取
            stripe.Subscription.delete(subscription_id)

            return JsonResponse({'status': 'success', 'message': 'Subscription canceled.'})
        except stripe.error.StripeError as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


@login_required
def apply_coupon(request):
    """
    应用优惠券
    """
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        try:
            # 示例代码：验证优惠券逻辑
            # 此处假设从数据库中查找优惠券
            if coupon_code == "DISCOUNT50":  # 示例优惠券代码
                discount = 50  # 假设优惠50
                return JsonResponse({'status': 'success', 'discount': discount, 'message': 'Coupon applied successfully!'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid coupon code.'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
