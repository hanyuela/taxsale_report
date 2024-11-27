新建数据表后需要将49个州和DC加入数据表criterion_states
1. 打开终端，运行以下命令启动 Django Shell：
python manage.py shell
2. 在 Django Shell 中运行以下代码：
from criterion.models import States
States.populate_states()
