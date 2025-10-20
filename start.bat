# MySQL 数据库互导程序启动脚本

echo "正在启动 MySQL 数据库互导程序..."
echo "请确保已安装 Python 3.10+ 和 MySQL 数据库"
echo ""

# 检查 Python 版本
python --version

# 安装依赖
echo "正在安装依赖包..."
pip install -r requirements.txt

# 启动应用
echo "正在启动 Flask 应用..."
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务"
echo ""

python app.py

