# -*- coding: utf-8 -*-
"""
MySQL 数据库互导程序配置文件
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
PAGE_SIZE = 500  # 每页导入的记录数（增加到500以提高效率）

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
