# -*- coding: utf-8 -*-
"""
数据库配置向导
帮助用户设置正确的数据库连接信息
"""

import mysql.connector
from mysql.connector import Error

def test_mysql_connection(host, port, user, password, database=None):
    """测试MySQL连接"""
    try:
        config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'charset': 'utf8mb4'
        }
        
        if database:
            config['database'] = database
            
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            cursor.close()
            connection.close()
            return True, f"连接成功! MySQL版本: {version[0]}"
        else:
            return False, "连接失败"
            
    except Error as e:
        return False, str(e)

def get_user_input():
    """获取用户输入的数据库配置"""
    print("MySQL 数据库配置向导")
    print("=" * 50)
    
    # 获取基本连接信息
    host = input("请输入MySQL主机地址 (默认: localhost): ").strip() or "localhost"
    port = input("请输入MySQL端口 (默认: 3306): ").strip() or "3306"
    user = input("请输入MySQL用户名 (默认: root): ").strip() or "root"
    password = input("请输入MySQL密码: ").strip()
    
    try:
        port = int(port)
    except ValueError:
        print("端口必须是数字，使用默认端口3306")
        port = 3306
    
    return host, port, user, password

def list_databases(host, port, user, password):
    """列出可用的数据库"""
    try:
        config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'charset': 'utf8mb4'
        }
        
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall() if db[0] not in ['information_schema', 'mysql', 'performance_schema', 'sys']]
        cursor.close()
        connection.close()
        return databases
    except Error as e:
        print(f"获取数据库列表失败: {e}")
        return []

def main():
    print("欢迎使用MySQL数据库配置向导!")
    print("这个工具将帮助您设置正确的数据库连接信息。")
    print()
    
    # 获取连接信息
    host, port, user, password = get_user_input()
    
    # 测试基本连接
    print(f"\n正在测试连接到 {host}:{port}...")
    success, message = test_mysql_connection(host, port, user, password)
    
    if not success:
        print(f"连接失败: {message}")
        print("\n请检查:")
        print("1. MySQL服务是否启动")
        print("2. 主机地址和端口是否正确")
        print("3. 用户名和密码是否正确")
        print("4. 防火墙设置")
        return
    
    print(f"连接成功: {message}")
    
    # 获取数据库列表
    print("\n正在获取数据库列表...")
    databases = list_databases(host, port, user, password)
    
    if not databases:
        print("没有找到可用的数据库，请先创建数据库")
        return
    
    print(f"\n找到 {len(databases)} 个数据库:")
    for i, db in enumerate(databases, 1):
        print(f"  {i}. {db}")
    
    # 选择源数据库
    print("\n选择源数据库:")
    while True:
        try:
            choice = input(f"请输入数字 (1-{len(databases)}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(databases):
                source_db = databases[int(choice) - 1]
                break
            else:
                print("请输入有效的数字")
        except KeyboardInterrupt:
            return
    
    # 选择目标数据库
    print("\n选择目标数据库:")
    while True:
        try:
            choice = input(f"请输入数字 (1-{len(databases)}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(databases):
                target_db = databases[int(choice) - 1]
                break
            else:
                print("请输入有效的数字")
        except KeyboardInterrupt:
            return
    
    # 生成配置文件
    config_content = f'''# -*- coding: utf-8 -*-
"""
MySQL 数据库互导程序配置文件
"""

# 源数据库配置
SOURCE_DB = {{
    'host': '{host}',
    'port': {port},
    'user': '{user}',
    'password': '{password}',
    'database': '{source_db}',
    'charset': 'utf8mb4'
}}

# 目标数据库配置
TARGET_DB = {{
    'host': '{host}',
    'port': {port},
    'user': '{user}',
    'password': '{password}',
    'database': '{target_db}',
    'charset': 'utf8mb4'
}}

# 分页导入设置
PAGE_SIZE = 100  # 每页导入的记录数

# 日志文件配置
LOG_FILE = 'logs/import.log'

# Flask配置
DEBUG = True
SECRET_KEY = 'your-secret-key-here'

# 导入模式
IMPORT_MODES = {{
    'overwrite': '覆盖模式 (REPLACE INTO)',
    'insert': '仅新增模式 (INSERT IGNORE)'
}}'''
    
    # 保存配置文件
    try:
        with open('config.py', 'w', encoding='utf-8') as f:
            f.write(config_content)
        print(f"\n配置文件已保存到 config.py")
        print(f"源数据库: {source_db}")
        print(f"目标数据库: {target_db}")
        print("\n现在可以运行主程序了: python app.py")
    except Exception as e:
        print(f"保存配置文件失败: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n配置已取消")
    except Exception as e:
        print(f"\n发生错误: {e}")

