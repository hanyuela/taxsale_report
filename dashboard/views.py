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
    # 查询所有任务（如果需要，可以根据某些条件筛选任务）
    tasks = Task.objects.all()  # 获取所有任务，您可以根据需求添加过滤条件

    # 将任务数据传递到模板
    return render(request, 'dashboard.html', {'tasks': tasks})


@csrf_exempt  # 忽略CSRF验证（仅用于示范，实际中请根据需求处理）
def add_task(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        deadline = request.POST.get('deadline')

        if content and deadline:
            task = Task.objects.create(content=content, deadline=deadline, label='In Progress')
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

def update_task_status(request, task_id):
    if request.method == 'POST':
        try:
            task = get_object_or_404(Task, id=task_id)
            data = json.loads(request.body)  # 获取请求的JSON数据
            label = data.get('label', '').strip()  # 获取传递的 label 值并去除空格

            # 设置有效的标签值
            valid_labels = ['In Progress', 'Pending', 'Done', 'Archived']
            
            # 如果 label 不在有效选项中，返回错误
            if label not in valid_labels:
                return JsonResponse({'status': 'error', 'message': 'Invalid label'})

            # 更新任务标签
            task.label = label
            task.save()

            # 返回更新后的任务数据
            return JsonResponse({'status': 'success', 'task': {
                'id': task.id,
                'content': task.content,
                'label': task.label,
                'deadline': task.deadline
            }})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})  

def delete_task(request, task_id):
    if request.method == 'DELETE':
        # 获取任务对象
        task = get_object_or_404(Task, id=task_id)
        task.delete()  # 删除任务
        return JsonResponse({'status': 'success'}, status=200)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=400)