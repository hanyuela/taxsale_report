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
import uuid
from .models import UserProfile
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import smtplib
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

# 登录页面
def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        # 注销当前已登录的用户（如果有）
        if request.user.is_authenticated:
            logout(request)

        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, "登录成功！")
            return redirect("index")  # 假设 'index' 是您的首页 URL 名称
        else:
            messages.error(request, "邮箱或密码错误，请重试。")
            return redirect("login")
    
    return render(request, "login.html")

def logout(request):
    django_logout(request)
    messages.success(request, "您已成功退出")
    return redirect("login")  # 假设 'login_view' 是您的登录视图的 URL 名称

# 首页
def index(request):
    return render(request, 'index.html')

# 编辑个人资料页面
def edit_profile(request):
    return render(request, 'edit-profile.html')

# 数据表页面
def datatable(request):
    return render(request, 'datatable.html')

# 忘记密码页面
def forget_password(request):
    return render(request, 'forget-password.html')

# 错误页面
def error_503(request):
    return render(request, 'error-503.html')

def signup_wizard(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        # 创建用户并存入数据库
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'sign-up-wizard.html')
        
        user = User.objects.create_user(username=email, email=email, password=password)
        user.save()
        
        # 自动登录用户
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')  # 重定向到主页

    return render(request, 'sign-up-wizard.html')

def template_index(request):
    return render(request, 'template/index.html')  # 渲染 template/index.html

def forget_password(request):
    if request.method == "POST":
        email = request.POST.get('email')  # 获取用户输入的电子邮件
        new_password = request.POST.get('new_password')  # 获取用户输入的新密码

        # 检查电子邮件和新密码的有效性
        if not email or not new_password:
            messages.error(request, 'Please enter a valid email and password.')
            return redirect('forget-password')

        try:
            user = User.objects.get(email=email)  # 获取用户
            user.set_password(new_password)  # 更新用户密码
            user.save()  # 保存更新
            
            # 生成一个唯一的令牌并保存到用户的 UserProfile 中
            token = uuid.uuid4()
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.password_reset_token = token
            user_profile.save()

            # 构建确认链接
            subject = "Soyhome.app - Password Reset Confirmation"
            body = f"Hello, please click on the following link to confirm your password reset: {request.scheme}://{request.get_host()}/confirm-password-reset/{user.id}/{token}/"

            # 构建 MIME 邮件
            sender_email = settings.EMAIL_HOST_USER
            receiver_email = user.email
            msg = MIMEText(body, 'plain', 'utf-8')
            msg['From'] = formataddr((str(Header("Soyhome.app", 'utf-8')), sender_email))
            msg['To'] = receiver_email
            msg['Subject'] = Header(subject, 'utf-8')

            # 使用 SMTP 发送邮件
            try:
                smtp_server = settings.EMAIL_HOST
                smtp_port = settings.EMAIL_PORT
                smtp_user = settings.EMAIL_HOST_USER
                smtp_password = settings.EMAIL_HOST_PASSWORD

                with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                    server.login(smtp_user, smtp_password)
                    server.sendmail(sender_email, [receiver_email], msg.as_string())
                
                messages.success(request, 'A confirmation email has been sent to your email address.')
                return redirect('/login/')  # 重定向到登录页面
            except Exception as e:
                messages.error(request, f'An error occurred while sending the message: {e}')
                return redirect('forget-password')

        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
            return redirect('forget-password')

    # GET 请求，渲染忘记密码页面
    return render(request, 'forget-password.html')  # 渲染忘记密码模板



def confirm_password_reset(request, user_id, token):
    try:
        user = User.objects.get(id=user_id)
        user_profile = UserProfile.objects.get(user=user)

        # 验证令牌是否匹配
        if str(user_profile.password_reset_token) == token:
            # 清除令牌，表示密码已重置
            user_profile.password_reset_token = None
            user_profile.save()
            messages.success(request, 'Your password has been successfully updated.')
        else:
            messages.error(request, 'Password reset link is invalid or expired.')
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        messages.error(request, 'User does not exist.')

    return redirect('/login/')  # 重定向到登录页面

