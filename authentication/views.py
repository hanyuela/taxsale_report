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
from django.shortcuts import render, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
import os
from django.core.files.storage import FileSystemStorage
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
    return render(request, 'profile.html')


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
        auction_types = request.POST.getlist('auction_type')  # 获取 auction_type 的多选列表
        is_online_modes = request.POST.getlist('is_online')  # 获取 is_online 的多选列表
        investment_purpose = request.POST.get('investment_purpose', '').strip()
        property_types = request.POST.getlist('property_type')  # 获取选择字段列表
        Total_Market_Value_min = request.POST.get('Total_Market_Value_min')
        Total_Market_Value_max = request.POST.get('Total_Market_Value_max')
        selected_states = request.POST.getlist('states')  # 前端传递的州缩写

        # 初始化上下文以保留已填写数据
        context = {
            'email': email,
            'auction_type': auction_types,  # 保留 auction_type 的多选值
            'is_online': is_online_modes,  # 保留 is_online 的多选值
            'investment_purpose': investment_purpose,
            'property_type': property_types,  # 保留选择值
            'Total_Market_Value_min':Total_Market_Value_min,
            'Total_Market_Value_max':Total_Market_Value_max,
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
                criterion = Criterion.objects.create(
                    user=user,

                    Total_Market_Value_min =Total_Market_Value_min or None,
                    Total_Market_Value_max =Total_Market_Value_max or None
                )

                # 保存 Auction Type 信息
                if auction_types:
                    criterion.auction_type = auction_types  # 多选存储为列表形式
                else:
                    criterion.auction_type = []  # 如果未选择，清空列表

                # 保存 Auction Mode 信息
                if is_online_modes:
                    criterion.is_online = is_online_modes  # 多选存储为列表形式
                else:
                    criterion.is_online = []  # 如果未选择，清空列表

                # 保存 Property Type 信息
                if property_types:
                    criterion.property_type = property_types  # 多选存储为列表形式
                else:
                    criterion.property_type = []  # 如果未选择，清空列表

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
def footer_light(request):
    return render(request, 'footer-light.html')


@login_required
def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)  # 获取当前登录用户的个人资料

    if request.method == "POST":
        # 更新用户资料
        user_profile.first_name = request.POST.get('first_name', user_profile.first_name)
        user_profile.last_name = request.POST.get('last_name', user_profile.last_name)
        user_profile.phone_number = request.POST.get('phone_number', user_profile.phone_number)
        user_profile.investment_amount = request.POST.get('investment_amount', user_profile.investment_amount)
        user_profile.goal = request.POST.get('goal', user_profile.goal)

        # 保存更新后的数据
        user_profile.save()

        return redirect('profile')  # 重定向回当前页面，显示更新后的数据

    return render(request, 'profile.html', {'user_profile': user_profile})


@login_required
def profile_update(request):
    # 获取当前登录用户的 UserProfile
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        # 获取表单数据
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        # 获取表单数据
        investment_amount = request.POST.get('investment_amount', None)

        # 将空字符串转换为 None
        if investment_amount == '':
            investment_amount = None
        
        goal = request.POST.get('goal')
        default = request.POST.get('default') == 'on'  # 如果复选框被选中，则为True，否则为False

        # 更新 UserProfile 对象
        user_profile.first_name = first_name
        user_profile.last_name = last_name
        user_profile.phone_number = phone_number
        user_profile.investment_amount = investment_amount
        user_profile.goal = goal
        user_profile.default = default
        user_profile.save()  # 保存更新后的数据

        return redirect('profile')  # 更新后重定向到个人资料页面

    # 如果是 GET 请求，则渲染当前用户的资料
    return render(request, 'profile_update.html', {'user_profile': user_profile})


@login_required
def update_email_request(request):
    if request.method == "POST" and 'update-email' in request.POST:
        new_email = request.POST.get("new_email")
        user = request.user

        # 1. 验证邮箱是否已存在（检查 username 字段）
        if User.objects.filter(username=new_email).exists():
            messages.error(request, "The new email you entered is already registered.")
            return redirect("profile")

        # 2. 生成验证链接
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(str(user.pk).encode())
        verification_link = (
            f"{request.scheme}://{request.get_host()}/verify-new-email/{uid}/{token}/?email={new_email}"
        )

        # 3. 构建邮件内容
        subject = "Soyhome.app - New Email Verification"
        body = (
            f"Hello {user.username},\n\n"
            f"Please click the link below to verify your new email address:\n\n"
            f"{verification_link}\n\n"
            "Best regards,\nSoyhome.app Team"
        )
        sender_email = settings.EMAIL_HOST_USER
        sender_name = "Soyhome.app"

        # 4. 发送验证邮件
        try:
            msg = MIMEText(body, 'plain', 'utf-8')
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = formataddr((str(Header(sender_name, 'utf-8')), sender_email))
            msg['To'] = new_email

            connection = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
            connection.login(sender_email, settings.EMAIL_HOST_PASSWORD)
            connection.sendmail(sender_email, [new_email], msg.as_string())
            connection.quit()

            messages.success(request, "A verification email has been sent to your new email address.")
        except Exception as e:
            messages.error(request, f"An error occurred while sending the email: {e}")

        return redirect("profile")

    return render(request, "profile.html")


def verify_new_email(request, uid, token):
    new_email = request.GET.get("email")
    try:
        # 1. 解码用户 ID 并获取用户
        user_id = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=user_id)

        # 2. 验证 Token 是否有效
        if default_token_generator.check_token(user, token):
            if not request.user.is_authenticated:
                # 如果未登录，自动登录用户
                login(request, user)

            # 3. 更新 username 而不是 email
            user.username = new_email
            user.save()

            messages.success(request, "Your email has been successfully verified and updated.")
            return redirect("profile")
        else:
            messages.error(request, "Invalid or expired verification link.")
            return redirect("login")

    except (User.DoesNotExist, ValueError, TypeError):
        messages.error(request, "Invalid verification link.")
        return redirect("login")
    

@login_required
def change_password(request):
    if request.method == "POST":
        password = request.POST.get("password")
        repeat_password = request.POST.get("repeat_password")
        user = request.user

        # 验证两次密码是否一致
        if password != repeat_password:
            messages.error(request, "Passwords do not match.")
            return redirect("profile")

        # 更新密码
        user.set_password(password)
        user.save()

        # 保持用户登录状态
        update_session_auth_hash(request, user)
        messages.success(request, "Your password has been successfully updated.")
        return redirect("profile")

    return redirect("profile")


@login_required
def update_avatar(request):
    if request.method == 'POST' and request.FILES.get('avatar'):
        avatar = request.FILES['avatar']

        # 设置文件存储路径
        fs = FileSystemStorage(location=os.path.join(settings.BASE_DIR, 'static/images/avatars'))
        filename = fs.save(avatar.name, avatar)  # 保存文件并获取文件名
        file_url = f'/static/images/avatars/{filename}'  # 拼接文件的相对路径

        # 获取或创建用户档案
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        # 将文件路径存入数据库
        profile.avatar_path = file_url
        profile.save()  # 保存更改

        # 返回 JSON 响应
        return JsonResponse({'success': True, 'avatar_url': file_url})

    # 如果请求不是文件上传，返回失败
    return JsonResponse({'success': False, 'error': 'No avatar uploaded'})
