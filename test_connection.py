# -*- coding: utf-8 -*-
"""
数据库连接测试脚本
用于诊断数据库连接问题
"""

import mysql.connector
from mysql.connector import Error
from config import SOURCE_DB, TARGET_DB

def test_connection(db_config, db_name):
    """测试数据库连接"""
    print(f"\n=== 测试 {db_name} 数据库连接 ===")
    print(f"配置信息:")
    print(f"  主机: {db_config['host']}")
    print(f"  端口: {db_config['port']}")
    print(f"  用户: {db_config['user']}")
    print(f"  数据库: {db_config['database']}")
    print(f"  字符集: {db_config['charset']}")
    
    try:
        print(f"\n正在连接 {db_name} 数据库...")
        connection = mysql.connector.connect(**db_config)
        
        if connection.is_connected():
            print(f"OK {db_name} 数据库连接成功!")
            
            # 获取数据库信息
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"  MySQL版本: {version[0]}")
            
            # 获取表列表
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"  表数量: {len(tables)}")
            
            if tables:
                print(f"  表列表:")
                for table in tables[:10]:  # 只显示前10个表
                    print(f"    - {table[0]}")
                if len(tables) > 10:
                    print(f"    ... 还有 {len(tables) - 10} 个表")
            else:
                print(f"  警告: 数据库中没有表")
            
            cursor.close()
            connection.close()
            print(f"OK {db_name} 数据库连接已关闭")
            return True
            
    except Error as e:
        print(f"X {db_name} 数据库连接失败!")
        print(f"错误信息: {e}")
        
        # 提供解决建议
        if "Access denied" in str(e):
            print("\n解决建议:")
            print("  1. 检查用户名和密码是否正确")
            print("  2. 确认用户是否有访问该数据库的权限")
        elif "Can't connect" in str(e):
            print("\n解决建议:")
            print("  1. 检查MySQL服务是否启动")
            print("  2. 检查主机地址和端口是否正确")
            print("  3. 检查防火墙设置")
        elif "Unknown database" in str(e):
            print("\n解决建议:")
            print("  1. 检查数据库名是否正确")
            print("  2. 确认数据库是否存在")
            print("  3. 创建数据库或修改配置")
        
        return False

def main():
    print("MySQL 数据库连接测试工具")
    print("=" * 50)
    
    # 测试源数据库
    source_ok = test_connection(SOURCE_DB, "源数据库")
    
    # 测试目标数据库
    target_ok = test_connection(TARGET_DB, "目标数据库")
    
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"源数据库: {'正常' if source_ok else '异常'}")
    print(f"目标数据库: {'正常' if target_ok else '异常'}")
    
    if not source_ok or not target_ok:
        print("\n警告: 请修复数据库连接问题后再运行主程序")
        print("可以编辑 config.py 文件修改数据库配置")
    else:
        print("\n成功: 所有数据库连接正常，可以运行主程序了!")

if __name__ == "__main__":
    main()
