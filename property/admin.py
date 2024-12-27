from django.urls import path
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.management import call_command
from django.contrib import admin
from property.models import Auction, Property, Owner
import os
from datetime import datetime

class AuctionAdmin(admin.ModelAdmin):
    change_list_template = "admin/auction_change_list.html"  # 自定义模板
    list_display = ('auction_tax_year', 'auction_type', 'authority_name')

    def upload_csv(self, request):
        if request.method == "POST":
            # 获取表单中的拍卖信息
            auction_type = request.POST.get('auction_type')
            is_online = request.POST.get('is_online')
            auction_tax_year = request.POST.get('auction_tax_year')
            deposit_deadline = request.POST.get('deposit_deadline')
            auction_start = request.POST.get('auction_start')
            auction_end = request.POST.get('auction_end')
            redemption_period = request.POST.get('redemption_period')
            foreclosure_date = request.POST.get('foreclosure_date')
            authority_name = request.POST.get('authority_name')
            csv_file = request.FILES.get('csv_file')

            if not csv_file:
                self.message_user(request, "请上传 CSV 文件！", level='error')
                return HttpResponseRedirect("../")

            # 保存 CSV 文件到 uploads 文件夹
            upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, csv_file.name)

            with open(file_path, 'wb') as f:
                for chunk in csv_file.chunks():
                    f.write(chunk)

            # 创建 Auction 实例
            try:
                auction = Auction.objects.create(
                    auction_type=auction_type,
                    is_online=is_online,
                    auction_tax_year=auction_tax_year,
                    deposit_deadline=datetime.strptime(deposit_deadline, "%Y-%m-%d") if deposit_deadline else None,
                    auction_start=datetime.strptime(auction_start, "%Y-%m-%d") if auction_start else None,
                    auction_end=datetime.strptime(auction_end, "%Y-%m-%d") if auction_end else None,
                    redemption_period=int(redemption_period) if redemption_period else None,
                    foreclosure_date=datetime.strptime(foreclosure_date, "%Y-%m-%d") if foreclosure_date else None,
                    authority_name=authority_name
                )

                # 调用管理命令，将 Auction ID 传递给 import_csv 命令
                call_command('import_csv', file_path, auction_id=auction.id)
                self.message_user(request, f"CSV 文件已成功导入，并绑定到 Auction (ID: {auction.id})！")
            except Exception as e:
                self.message_user(request, f"导入失败：{str(e)}", level='error')

            return HttpResponseRedirect("../")  # 返回到列表页面

        return render(request, 'admin/upload_csv.html')  # 使用自定义模板

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

