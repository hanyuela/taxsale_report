新建数据表后需要将49个州和DC加入数据表criterion_states
1. 打开终端，运行以下命令启动 Django Shell：
python manage.py shell
2. 在 Django Shell 中运行以下代码：
from criterion.models import States
States.populate_states()


设置Superuser
1. 创建账号
python manage.py createsuperuser
username TaxsaleSoyhome
email  taxsalesoyhome@gmail.com
password  Soyhome@us2021!
2. 进入管理员后台
http://127.0.0.1:8000/adminsoyhome/

