from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm
from django.contrib.auth.models import User  # 导入 User 模型
from django.contrib import messages  # 导入 messages 模块
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from criterion.models import Criterion, States
from .models import UserProfile
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import smtplib
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import transaction
from property.models import Property, Auction
# 注册页面
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'sign-up-wizard.html', {'form': form})

def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("index")
        else:
            messages.error(request, "Invalid email or password, please try again.")
            return redirect("login")
    
    return render(request, "login.html")



def logout(request):
    django_logout(request)
    messages.success(request, "You have successfully exited")
    return redirect("index")  # 重定向到 index 视图，确保该视图渲染 base.html

@login_required
def index(request):
    if request.user.is_authenticated:
        return render(request, 'index.html')  # 用户已登录，渲染 index.html
    else:
        return redirect('login')  # 用户未登录，重定向到登录页面
    

# 编辑个人资料页面
@login_required
def edit_profile(request):
    return render(request, 'edit-profile.html')

# 数据表页面
@login_required
def datatable(request):
    return render(request, 'datatable.html')



# 错误页面
def error_503(request):
    return render(request, 'error-503.html')


def signup_wizard(request):
    if request.method == 'POST':
        # 获取用户提交的表单数据
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        # 获取其他字段
        auction_type = request.POST.get('auction_type', '').strip()  # 获取 auction_type
        is_online = request.POST.get('is_online', '').strip()  # 获取 is_online
        investment_purpose = request.POST.get('investment_purpose', '').strip()
        property_types = request.POST.getlist('property_type')  # 获取选择字段列表
        market_value_min = request.POST.get('market_value_min', '').strip()
        market_value_max = request.POST.get('market_value_max', '').strip()
        face_value_min = request.POST.get('face_value_min', '').strip()
        face_value_max = request.POST.get('face_value_max', '').strip()
        selected_states = request.POST.getlist('states')  # 前端传递的州缩写

        # 初始化上下文以保留已填写数据
        context = {
            'email': email,
            'auction_type': auction_type,
            'is_online': is_online,
            'investment_purpose': investment_purpose,
            'property_type': property_types,  # 保留选择值
            'market_value_min': market_value_min,
            'market_value_max': market_value_max,
            'face_value_min': face_value_min,
            'face_value_max': face_value_max,
            'states': selected_states,
            'first_name': request.POST.get('first_name', '').strip(),
            'last_name': request.POST.get('last_name', '').strip(),
            'phone_number': request.POST.get('phone_number', '').strip(),
            'investment_amount': request.POST.get('investment_amount', '').strip(),
        }

        # 验证用户输入
        if not email:
            messages.error(request, "Email is required.")
            return render(request, 'sign-up-wizard.html', context)

        if not password:
            messages.error(request, "Password is required.")
            return render(request, 'sign-up-wizard.html', context)

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'sign-up-wizard.html', context)

        if User.objects.filter(username=email).exists():
            messages.error(request, "This email is already registered.")
            return render(request, 'sign-up-wizard.html', context)

        try:
            with transaction.atomic():
                # 创建用户
                user = User.objects.create_user(username=email, email=email, password=password)
                user.save()

                # 保存 UserProfile 信息
                UserProfile.objects.create(
                    user=user,
                    first_name=request.POST.get('first_name', '').strip(),
                    last_name=request.POST.get('last_name', '').strip(),
                    phone_number=request.POST.get('phone_number', '').strip(),
                    investment_amount=request.POST.get('investment_amount', '').strip() or None,
                    goal=investment_purpose,
                )

                # 保存 Criterion 信息
                property_types_str = ",".join(property_types)  # 将列表转换为存储格式

                criterion = Criterion.objects.create(
                    user=user,
                    auction_type=auction_type,  # 存储 auction_type
                    is_online=is_online,  # 存储 is_online
                    
                    property_type=property_types_str,  # 存储选择字段的值
                    market_value_min=market_value_min or None,
                    market_value_max=market_value_max or None,
                    face_value_min=face_value_min or None,
                    face_value_max=face_value_max or None,
                )

                # 获取选中的 States
                if selected_states:
                    states = States.objects.filter(abbreviation__in=selected_states)
                    criterion.states.add(*states)

                criterion.save()

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return render(request, 'sign-up-wizard.html', context)

        # 自动登录用户
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')

    # GET 请求：渲染表单页面并提供所有州数据
    states = States.objects.all()
    return render(request, 'sign-up-wizard.html', {'states': states})


@csrf_exempt  # 允许不经过 CSRF 验证，前端已提供 CSRF token
def check_email(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()
            exists = User.objects.filter(username=email).exists()
            return JsonResponse({'exists': exists})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

# 处理第一步：请求重置密码链接
def request_password_reset(request):
    if request.method == 'POST':
        email = request.POST['email']
        
        # 检查邮箱是否在数据库中
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # 如果没有找到该邮箱，返回错误消息
            messages.error(request, 'Email address does not exist in our system.')
            return redirect('request_password_reset')
        
       # 生成重置链接
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = request.build_absolute_uri(f"/reset/{uid}/{token}/")
        
        # 使用SMTP发送邮件
        subject = 'Password Reset Request'
        body = f'Click the link to reset your password: {reset_link}'

        # 构建 MIME 邮件
        sender_email = settings.EMAIL_HOST_USER
        receiver_email = email
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['From'] = formataddr((str(Header("Soyhome.app", 'utf-8')), sender_email))
        msg['To'] = receiver_email
        msg['Subject'] = Header(subject, 'utf-8')

        try:
            smtp_server = settings.EMAIL_HOST
            smtp_port = settings.EMAIL_PORT
            smtp_user = settings.EMAIL_HOST_USER
            smtp_password = settings.EMAIL_HOST_PASSWORD

            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(smtp_user, smtp_password)
                server.sendmail(sender_email, [receiver_email], msg.as_string())
            
            messages.success(request, 'Password reset link has been sent to your email.')
            return redirect('request_password_reset')
        except Exception as e:
            messages.error(request, f'An error occurred while sending the message: {e}')
            return redirect('request_password_reset')
    
    return render(request, 'request_password_reset.html')


def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST['new_password']
            confirm_password = request.POST['confirm_password']
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Your password has been reset successfully.')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match.')
        return render(request, 'forget-password.html', {'uidb64': uidb64, 'token': token})
    else:
        messages.error(request, 'Invalid or expired reset link.')
        return redirect('request_password_reset')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')



@login_required
def footer_light(request):
    return render(request, 'footer-light.html')
@login_required

def holdings(request):
    return render(request, 'holdings.html')



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

        # 更新 Auction Type（单选）
        auction_type = request.POST.get('auction_type')
        if auction_type:
            user_criteria.auction_type = auction_type

        # 更新 Auction Mode（单选）
        auction_mode = request.POST.get('is_online')
        if auction_mode:
            user_criteria.is_online = auction_mode

        # 更新市场价值范围
        market_value_min = request.POST.get('market_value_min', None)
        market_value_max = request.POST.get('market_value_max', None)
        user_criteria.market_value_min = market_value_min if market_value_min else None
        user_criteria.market_value_max = market_value_max if market_value_max else None

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

@login_required
def datatable(request):
    # 获取当前用户的筛选条件
    user_criteria = Criterion.objects.filter(user=request.user).first()

    # 初始查询集
    properties = Property.objects.all()
    auctions = Auction.objects.all()

    # 筛选条件
    if user_criteria:
        # 1. 按 `property_type` 筛选（针对 Property 表的 property_class 字段）
        if user_criteria.property_type:
            properties = properties.filter(property_class__in=user_criteria.property_type)

        # 2. 按 `auction_type` 筛选（针对 Auction 表的 auction_type 字段）
        if user_criteria.auction_type:
            auctions = auctions.filter(auction_type=user_criteria.auction_type)

        # 3. 按 `is_online` 筛选（针对 Auction 表的 is_online 字段）
        if user_criteria.is_online:
            auctions = auctions.filter(is_online=user_criteria.is_online)

        # 4. 按市场价值范围筛选（针对 Property 表的 market_value 字段）
        if user_criteria.market_value_min:
            properties = properties.filter(market_value__gte=user_criteria.market_value_min)
        if user_criteria.market_value_max:
            properties = properties.filter(market_value__lte=user_criteria.market_value_max)

        # 5. 按面值范围筛选（针对 Auction 表的 face_value 字段）
        if user_criteria.face_value_min:
            auctions = auctions.filter(face_value__gte=user_criteria.face_value_min)
        if user_criteria.face_value_max:
            auctions = auctions.filter(face_value__lte=user_criteria.face_value_max)

        # 6. 按选中州筛选（针对 Property 表的 state 字段）
        if user_criteria.states.exists():
            state_names = user_criteria.states.values_list('state', flat=True)
            properties = properties.filter(state__in=state_names)

    # 将 Auction 和 Property 结果进行关联
    auctioned_properties = properties.filter(auction__in=auctions)

    # 返回筛选结果到前端
    return render(request, "property_filter.html", {
        "properties": auctioned_properties,
        "user_criteria": user_criteria,
    })

@login_required
def report(request):
    return render(request, 'report.html')
