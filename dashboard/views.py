from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
from dashboard.models import Task
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
# Create your views here.
@login_required
def dashboard(request):
    # 只显示当前用户的任务
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'tasks': tasks})

@csrf_exempt
@login_required  # 添加登录验证
def add_task(request):
    if request.method == 'POST':
        # 确保只有当前用户可以创建任务
        content = request.POST.get('content')
        deadline = request.POST.get('deadline')

        if content and deadline:
            task = Task.objects.create(
                user=request.user,  # 关联当前用户
                content=content,
                deadline=deadline,
                label='In Progress'
            )
            return JsonResponse({
                'status': 'success',
                'task': {
                    'id': task.id,
                    'content': task.content,
                    'label': task.label,
                    'deadline': task.deadline
                }
            })
        return JsonResponse({'status': 'error', 'message': 'Invalid data'})
    return JsonResponse({'status': 'error', 'message': 'Invalid method'})

@login_required  # 添加登录验证
def update_task_status(request, task_id):
    if request.method == 'POST':
        try:
            # 只允许修改当前用户的任务
            task = get_object_or_404(Task, id=task_id, user=request.user)
            data = json.loads(request.body)
            label = data.get('label', '').strip()

            valid_labels = ['In Progress', 'Pending', 'Done', 'Archived']
            
            if label not in valid_labels:
                return JsonResponse({'status': 'error', 'message': 'Invalid label'})

            task.label = label
            task.save()

            return JsonResponse({'status': 'success', 'task': {
                'id': task.id,
                'content': task.content,
                'label': task.label,
                'deadline': task.deadline
            }})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required  # 添加登录验证
def delete_task(request, task_id):
    if request.method == 'DELETE':
        # 只允许删除当前用户的任务
        task = get_object_or_404(Task, id=task_id, user=request.user)
        task.delete()
        return JsonResponse({'status': 'success'}, status=200)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=400)