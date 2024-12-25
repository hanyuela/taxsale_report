from django.urls import path
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.management import call_command
from django.contrib import admin
from property.models import Auction, Property, Owner
import os

class AuctionAdmin(admin.ModelAdmin):
    change_list_template = "admin/auction_change_list.html"  # 指定自定义模板
    list_display = ('auction_tax_year', 'auction_type', 'authority_name')

    def upload_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES['csv_file']
            
            # 保存上传文件到项目的 uploads 文件夹
            upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
            os.makedirs(upload_dir, exist_ok=True)  # 确保目录存在
            file_path = os.path.join(upload_dir, csv_file.name)
            
            with open(file_path, 'wb') as f:
                for chunk in csv_file.chunks():
                    f.write(chunk)

            # 调用管理命令
            try:
                call_command('import_csv', file_path)  # 使用保存的文件路径
                self.message_user(request, "CSV 文件已成功导入！")
            except Exception as e:
                self.message_user(request, f"导入失败：{str(e)}", level='error')

            return HttpResponseRedirect("../")  # 返回到列表页面

        return render(request, 'admin/upload_csv.html')

    def get_urls(self):
        # 定义自定义 URL
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', admin.site.admin_view(self.upload_csv), name='auction_upload_csv'),
        ]
        return custom_urls + urls

admin.site.register(Auction, AuctionAdmin)
admin.site.register(Property)
admin.site.register(Owner)
