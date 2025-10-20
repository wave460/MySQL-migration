# -*- coding: utf-8 -*-
"""
MySQL 数据库互导程序配置文件
请根据您的实际MySQL环境修改以下配置
"""

# 源数据库配置
SOURCE_DB = {
    'host': 'localhost',        # MySQL主机地址
    'port': 3306,              # MySQL端口
    'user': 'root',            # MySQL用户名
    'password': '',            # MySQL密码 - 请修改为您的实际密码
    'database': 'test',        # 源数据库名 - 请修改为您的实际数据库名
    'charset': 'utf8mb4'
}

# 目标数据库配置
TARGET_DB = {
    'host': 'localhost',        # MySQL主机地址
    'port': 3306,              # MySQL端口
    'user': 'root',            # MySQL用户名
    'password': '',            # MySQL密码 - 请修改为您的实际密码
    'database': 'test',        # 目标数据库名 - 请修改为您的实际数据库名
    'charset': 'utf8mb4'
}

# 分页导入设置
PAGE_SIZE = 100  # 每页导入的记录数

# 日志文件配置
LOG_FILE = 'logs/import.log'

# Flask配置
DEBUG = True
SECRET_KEY = 'your-secret-key-here'

# 导入模式
IMPORT_MODES = {
    'overwrite': '覆盖模式 (REPLACE INTO)',
    'insert': '仅新增模式 (INSERT IGNORE)'
}

# 常见配置示例:
# 1. 如果MySQL没有密码:
#    'password': '',
#
# 2. 如果MySQL密码是 '123456':
#    'password': '123456',
#
# 3. 如果MySQL运行在不同端口 (如3307):
#    'port': 3307,
#
# 4. 如果MySQL运行在远程服务器:
#    'host': '192.168.1.100',
#
# 5. 如果使用不同的数据库:
#    'database': 'your_database_name',

