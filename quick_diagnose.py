# -*- coding: utf-8 -*-
"""
MySQL 快速诊断脚本
帮助找到正确的MySQL连接配置
"""

import mysql.connector
from mysql.connector import Error

def test_common_configs():
    """测试常见的MySQL配置"""
    print("MySQL 快速诊断工具")
    print("=" * 50)
    
    # 常见配置列表
    configs = [
        # 配置1: 无密码
        {
            'name': '无密码配置',
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '',
            'database': 'mysql'
        },
        # 配置2: 常见密码
        {
            'name': '密码: root',
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': 'root',
            'database': 'mysql'
        },
        # 配置3: 密码123456
        {
            'name': '密码: 123456',
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '123456',
            'database': 'mysql'
        },
        # 配置4: 密码password
        {
            'name': '密码: password',
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': 'password',
            'database': 'mysql'
        },
        # 配置5: 不同端口
        {
            'name': '端口: 3307',
            'host': 'localhost',
            'port': 3307,
            'user': 'root',
            'password': '',
            'database': 'mysql'
        }
    ]
    
    working_configs = []
    
    for config in configs:
        print(f"\n测试配置: {config['name']}")
        print(f"  主机: {config['host']}:{config['port']}")
        print(f"  用户: {config['user']}")
        print(f"  密码: {'***' if config['password'] else '(无密码)'}")
        
        try:
            connection = mysql.connector.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                database=config['database'],
                charset='utf8mb4'
            )
            
            if connection.is_connected():
                print(f"  连接成功!")
                
                # 获取数据库列表
                cursor = connection.cursor()
                cursor.execute("SHOW DATABASES")
                databases = [db[0] for db in cursor.fetchall() 
                            if db[0] not in ['information_schema', 'mysql', 'performance_schema', 'sys']]
                cursor.close()
                connection.close()
                
                print(f"  可用数据库: {', '.join(databases) if databases else '(无用户数据库)'}")
                
                working_configs.append({
                    'config': config,
                    'databases': databases
                })
            else:
                print(f"  连接失败")
                
        except Error as e:
            print(f"  连接失败: {e}")
    
    # 显示结果
    print("\n" + "=" * 50)
    print("诊断结果:")
    
    if working_configs:
        print(f"找到 {len(working_configs)} 个可用配置:")
        for i, wc in enumerate(working_configs, 1):
            config = wc['config']
            databases = wc['databases']
            print(f"\n{i}. {config['name']}")
            print(f"   主机: {config['host']}:{config['port']}")
            print(f"   用户: {config['user']}")
            print(f"   密码: {'***' if config['password'] else '(无密码)'}")
            print(f"   可用数据库: {', '.join(databases) if databases else '(无用户数据库)'}")
        
        # 生成配置文件
        if working_configs:
            best_config = working_configs[0]['config']
            databases = working_configs[0]['databases']
            
            print(f"\n推荐使用第一个配置生成 config.py:")
            print(f"主机: {best_config['host']}:{best_config['port']}")
            print(f"用户: {best_config['user']}")
            print(f"密码: {'***' if best_config['password'] else '(无密码)'}")
            
            if databases:
                print(f"可用数据库: {', '.join(databases)}")
                print(f"建议选择两个不同的数据库作为源数据库和目标数据库")
            else:
                print("没有找到用户数据库，请先创建数据库")
    else:
        print("没有找到可用的MySQL配置")
        print("\n请检查:")
        print("1. MySQL服务是否启动")
        print("2. 用户名和密码是否正确")
        print("3. 端口是否正确")
        print("4. 防火墙设置")

if __name__ == "__main__":
    test_common_configs()
