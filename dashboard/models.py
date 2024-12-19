from django.db import models

class Task(models.Model):
    # content 字段，最多 500 个字符
    content = models.TextField(max_length=500)
    
    # label 字段，四个选项
    IN_PROGRESS = 'In Progress'
    PENDING = 'Pending'
    DONE = 'Done'
    ARCHIVED = 'Archived'
    LABEL_CHOICES = [
        (IN_PROGRESS, 'In Progress'),
        (PENDING, 'Pending'),
        (DONE, 'Done'),
        (ARCHIVED, 'Archived'),
    ]
    label = models.CharField(
        max_length=11,  # 设置为 11，适应最长选项
        choices=LABEL_CHOICES, 
        default=PENDING
    )
    
    # created 字段，记录任务创建的日期
    created = models.DateField(auto_now_add=True)
    
    # deadline 字段，用户选择的截至日期
    deadline = models.DateField()

    def __str__(self):
        return f"任务 {self.id} - {self.content[:30]}..."  # 显示内容的前 30 个字符
