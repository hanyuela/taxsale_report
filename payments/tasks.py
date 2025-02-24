from huey.contrib.djhuey import periodic_task, task
from huey import crontab
from authentication.models import UserProfile
from django.utils.timezone import make_aware
from datetime import datetime
from payments.views import get_next_payment_date,Payment_history
from django.db.models import Sum
from django.utils import timezone

@periodic_task(crontab(hour='*/12'))
def check_membership_payments():
    today = make_aware(datetime.now())  # 获取当前日期并转换为带时区的时间

    users = UserProfile.objects.all()
    for user_profile in users:
        user = user_profile.user  # 获取 User 实例

        # 如果用户已经取消了下一次订阅
        if user_profile.is_cancelled:
            user_profile.member = 0  # 设置为非付费用户
            user_profile.is_cancelled = 0  # 重置 is_cancelled 字段
            user_profile.save()
            continue  # 跳过扣款逻辑

        # 获取下一个付款日期
        next_payment_date = get_next_payment_date(user_profile.member_start, monthly=True)
        
        # 确保 next_payment_date 是 naive datetime，如果是带时区的，需要去除时区
        if next_payment_date.tzinfo is not None:
            next_payment_date = next_payment_date.replace(tzinfo=None)
        
        next_payment_date = make_aware(next_payment_date)  # 将 naive datetime 转换为带时区的 datetime

        # 检查付款日期
        if today >= next_payment_date:
            # 根据用户会员类型来设定扣款金额
            if user_profile.member == 1:
                payment_amount = 5
            elif user_profile.member == 2:
                payment_amount = 50
            else:
                payment_amount = 0  # 如果不是会员1或2，则不扣款

            if payment_amount > 0:
                # 计算用户的余额
                remaining_balance = Payment_history.objects.filter(user=user).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

                if remaining_balance >= payment_amount:  # 如果余额足够
                    # 扣款操作
                    # 更新会员开始时间为当前时间
                    user_profile.member_start = make_aware(datetime.now()).replace(microsecond=0)  # 设置为当前时间，不带微秒
                    user_profile.save()

                    # 记录付款历史
                    Payment_history.objects.create(
                        user=user,
                        amount=-payment_amount,
                        time=datetime.now().time(),
                        date=datetime.now().date(),
                        method="balance",  # 使用余额扣款
                        type="membership_fee",  # 记录类型
                    )
                else:
                    # 余额不足，修改会员状态为未支付
                    user_profile.member = 0  # 设置为未支付
                    user_profile.save()