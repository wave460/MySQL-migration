# -*- coding: utf-8 -*-
"""
MySQL 数据库互导程序 - Flask 后端主程序
"""

import os
import json
import threading
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify
import mysql.connector
from mysql.connector import Error
from config import SOURCE_DB, TARGET_DB, PAGE_SIZE, LOG_FILE, DEBUG, SECRET_KEY, IMPORT_MODES

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = DEBUG

# 确保日志目录存在
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# 导入历史记录文件
HISTORY_FILE = 'logs/import_history.json'

def get_db_connection(db_config):
    """获取数据库连接"""
    try:
        print(f"尝试连接数据库: {db_config['host']}:{db_config['port']} - {db_config['database']}")
        
        # 添加连接超时和重试机制
        connection_config = db_config.copy()
        connection_config.update({
            'connection_timeout': 60,  # 连接超时60秒
            'autocommit': False,       # 手动控制事务
            'use_unicode': True,
            'charset': 'utf8mb4',
            'sql_mode': 'TRADITIONAL',
            'init_command': "SET SESSION wait_timeout=28800, interactive_timeout=28800"  # 8小时超时
        })
        
        connection = mysql.connector.connect(**connection_config)
        
        # 设置会话参数
        cursor = connection.cursor()
        cursor.execute("SET SESSION wait_timeout = 28800")  # 8小时
        cursor.execute("SET SESSION interactive_timeout = 28800")  # 8小时
        cursor.execute("SET SESSION net_read_timeout = 600")  # 10分钟读取超时
        cursor.execute("SET SESSION net_write_timeout = 600")  # 10分钟写入超时
        cursor.close()
        
        print(f"数据库连接成功: {db_config['database']}")
        return connection
    except Error as e:
        print(f"数据库连接错误: {e}")
        print(f"连接配置: host={db_config['host']}, port={db_config['port']}, user={db_config['user']}, database={db_config['database']}")
        return None

def get_tables(connection):
    """获取数据库中的所有表"""
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        cursor.close()
        return tables
    except Error as e:
        print(f"获取表列表错误: {e}")
        return []

def auto_match_fields(source_fields, target_fields):
    """智能字段匹配 - 改进版"""
    import difflib
    
    # 字段名映射规则 - 更精确的映射
    field_mapping_rules = {
        # ID类字段
        'id': ['itemid', 'aid', 'uid', 'userid'],
        'itemid': ['id', 'aid', 'uid', 'userid'],
        
        # 标题类字段
        'title': ['title', 'subject', 'name', 'caption'],
        
        # 内容类字段
        'content': ['content', 'body', 'text', 'description', 'introduce'],
        'description': ['introduce', 'content', 'body', 'text'],
        'introduce': ['description', 'content', 'body', 'text'],
        
        # 作者类字段
        'author': ['author', 'writer', 'creator', 'user'],
        
        # 时间类字段
        'time': ['time', 'date', 'addtime', 'createtime', 'inputtime', 'updatetime', 'edittime'],
        'addtime': ['inputtime', 'createtime', 'addtime'],
        'inputtime': ['addtime', 'createtime', 'inputtime'],
        'updatetime': ['edittime', 'updatetime'],
        'edittime': ['updatetime', 'edittime'],
        
        # 状态类字段
        'status': ['status', 'state', 'flag'],
        
        # 分类类字段
        'catid': ['catid', 'category', 'type', 'class'],
        'category': ['catid', 'category', 'type', 'class'],
        
        # URL类字段
        'url': ['linkurl', 'url', 'link'],
        'linkurl': ['url', 'linkurl', 'link'],
        'link': ['linkurl', 'url', 'link'],
        
        # 图片类字段
        'thumb': ['thumb', 'image', 'img', 'photo', 'pic'],
        'image': ['thumb', 'image', 'img', 'photo', 'pic'],
        
        # 关键词类字段
        'keyword': ['keyword', 'tag'],
        'keywords': ['keyword', 'tag'],
        'tag': ['keyword', 'tag'],
        
        # 点击数类字段
        'hits': ['hits', 'views', 'count', 'click'],
        
        # IP类字段
        'ip': ['ip', 'ipaddress', 'inputip'],
        'inputip': ['ip', 'ipaddress', 'inputip'],
        
        # 排序类字段
        'order': ['order', 'sort', 'displayorder', 'sortorder'],
        'displayorder': ['order', 'sort', 'displayorder', 'sortorder'],
        
        # 表ID类字段
        'tableid': ['tableid', 'areaid'],
        'areaid': ['tableid', 'areaid'],
        
        # 链接类字段
        'link_id': ['islink', 'link_id'],
        'islink': ['link_id', 'islink'],
    }
    
    matched_fields = {}
    used_source_fields = set()
    used_target_fields = set()
    
    print(f"开始智能匹配:")
    print(f"源字段: {source_fields}")
    print(f"目标字段: {target_fields}")
    
    # 第一轮：精确匹配
    for target_field in target_fields:
        if target_field in source_fields:
            matched_fields[target_field] = target_field
            used_source_fields.add(target_field)
            used_target_fields.add(target_field)
            print(f"精确匹配: {target_field} -> {target_field}")
    
    # 第二轮：规则匹配
    for target_field in target_fields:
        if target_field in used_target_fields:
            continue
            
        # 查找匹配规则
        if target_field in field_mapping_rules:
            rule_values = field_mapping_rules[target_field]
            # 在源字段中查找匹配的字段
            for source_field in source_fields:
                if source_field in used_source_fields:
                    continue
                if source_field in rule_values:
                    matched_fields[target_field] = source_field
                    used_source_fields.add(source_field)
                    used_target_fields.add(target_field)
                    print(f"规则匹配: {target_field} -> {source_field}")
                    break
    
    # 第三轮：模糊匹配（相似度匹配）
    for target_field in target_fields:
        if target_field in used_target_fields:
            continue
            
        best_match = None
        best_ratio = 0
        
        for source_field in source_fields:
            if source_field in used_source_fields:
                continue
                
            # 计算相似度
            ratio = difflib.SequenceMatcher(None, target_field.lower(), source_field.lower()).ratio()
            
            # 如果相似度超过0.7，认为是匹配的（提高阈值）
            if ratio > 0.7 and ratio > best_ratio:
                best_match = source_field
                best_ratio = ratio
        
        if best_match:
            matched_fields[target_field] = best_match
            used_source_fields.add(best_match)
            used_target_fields.add(target_field)
            print(f"模糊匹配: {target_field} -> {best_match} (相似度: {best_ratio:.2f})")
    
    print(f"最终匹配结果: {matched_fields}")
    return matched_fields

def get_table_fields(connection, table_name):
    """获取表的字段信息"""
    try:
        cursor = connection.cursor()
        cursor.execute(f"DESCRIBE `{table_name}`")
        fields = []
        for field in cursor.fetchall():
            fields.append({
                'name': field[0],
                'type': field[1],
                'null': field[2],
                'key': field[3],
                'default': field[4],
                'extra': field[5]
            })
        cursor.close()
        return fields
    except Error as e:
        print(f"获取字段信息错误: {e}")
        return []

def write_log(message):
    """写入日志文件"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}\n"
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_message)
    except Exception as e:
        print(f"写入日志错误: {e}")

def save_import_history(source_table, target_table, field_mapping, import_mode, status, records_count, duration):
    """保存导入历史记录"""
    try:
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'source_table': source_table,
            'target_table': target_table,
            'field_mapping': field_mapping,
            'import_mode': import_mode,
            'status': status,
            'records_count': records_count,
            'duration': duration
        }
        
        # 读取现有历史记录
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        # 添加新记录
        history.insert(0, history_entry)  # 最新的记录在前面
        
        # 只保留最近50条记录
        history = history[:50]
        
        # 保存历史记录
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"保存导入历史错误: {e}")

def get_import_history():
    """获取导入历史记录"""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"读取导入历史错误: {e}")
        return []

def import_data_thread(source_table, target_table, field_mapping, default_values, import_mode, page_size=None):
    """数据导入线程"""
    start_time = time.time()
    write_log("开始数据导入...")
    
    # 使用传入的页面大小，如果没有则使用默认值
    actual_page_size = page_size if page_size else PAGE_SIZE
    write_log(f"使用页面大小: {actual_page_size} 条记录")
    
    print(f"导入线程启动: source={source_table}, target={target_table}")
    print(f"字段映射: {field_mapping}")
    print(f"默认值: {default_values}")
    print(f"页面大小: {actual_page_size}")
    
    # 连接源数据库和目标数据库
    source_conn = get_db_connection(SOURCE_DB)
    target_conn = get_db_connection(TARGET_DB)
    
    if not source_conn or not target_conn:
        write_log("数据库连接失败")
        duration = time.time() - start_time
        save_import_history(source_table, target_table, field_mapping, import_mode, '失败', 0, duration)
        return
    
    try:
        # 获取源表总记录数
        source_cursor = source_conn.cursor()
        source_cursor.execute(f"SELECT COUNT(*) FROM `{source_table}`")
        total_records = source_cursor.fetchone()[0]
        write_log(f"源表 {source_table} 总记录数: {total_records}")
        
        # 计算总页数
        total_pages = (total_records + actual_page_size - 1) // actual_page_size
        write_log(f"将分 {total_pages} 页导入，每页 {actual_page_size} 条记录")
        
        # 准备目标表字段 - 包括映射字段和默认值字段
        target_fields = list(field_mapping.keys()) + list(default_values.keys())
        # 去重并保持顺序
        target_fields = list(dict.fromkeys(target_fields))
        target_fields_str = ', '.join([f"`{field}`" for field in target_fields])
        
        print(f"目标字段列表: {target_fields}")
        print(f"映射字段: {list(field_mapping.keys())}")
        print(f"默认值字段: {list(default_values.keys())}")
        
        # 准备SQL语句
        if import_mode == 'overwrite':
            sql_template = f"REPLACE INTO `{target_table}` ({target_fields_str}) VALUES ({', '.join(['%s'] * len(target_fields))})"
        else:
            sql_template = f"INSERT IGNORE INTO `{target_table}` ({target_fields_str}) VALUES ({', '.join(['%s'] * len(target_fields))})"
        
        target_cursor = target_conn.cursor()
        imported_records = 0
        
        # 分页导入数据
        for page in range(total_pages):
            offset = page * actual_page_size
            progress_percent = int((page / total_pages) * 100)
            write_log(f"正在导入第 {page + 1}/{total_pages} 页... (进度: {progress_percent}%)")
            
            # 移除健康检查，避免与主查询冲突
            # 如果需要检查连接，可以在重试机制中处理
            
            # 重试机制
            max_retries = 3
            for retry in range(max_retries):
                try:
                    # 查询源表数据
                    source_cursor.execute(f"SELECT * FROM `{source_table}` LIMIT {actual_page_size} OFFSET {offset}")
                    source_data = source_cursor.fetchall()
                    break  # 成功则跳出重试循环
                except Error as e:
                    if retry < max_retries - 1:
                        write_log(f"第 {page + 1} 页查询失败，重试 {retry + 1}/{max_retries}: {e}")
                        time.sleep(2)  # 等待2秒后重试
                        continue
                    else:
                        raise e  # 最后一次重试失败，抛出异常
            
            # 获取源表字段名
            source_fields = [desc[0] for desc in source_cursor.description]
            
            # 转换数据
            converted_data = []
            for row in source_data:
                converted_row = []
                for target_field in target_fields:
                    source_field = field_mapping.get(target_field)
                    if source_field and source_field in source_fields:
                        # 从源表获取数据
                        source_index = source_fields.index(source_field)
                        converted_row.append(row[source_index])
                    else:
                        # 使用默认值
                        default_value = default_values.get(target_field, '')
                        
                        # 如果默认值为空字符串，尝试转换为None（让数据库使用字段默认值）
                        if default_value == '':
                            converted_row.append(None)
                        else:
                            # 尝试转换默认值的类型
                            try:
                                # 如果是数字字符串，转换为数字
                                if default_value.isdigit():
                                    converted_value = int(default_value)
                                    converted_row.append(converted_value)
                                elif default_value.replace('.', '').isdigit():
                                    converted_value = float(default_value)
                                    converted_row.append(converted_value)
                                else:
                                    converted_row.append(default_value)
                            except Exception as e:
                                converted_row.append(default_value)
                converted_data.append(converted_row)
            
            # 批量插入目标表 - 添加重试机制
            if converted_data:
                insert_success = False
                for retry in range(max_retries):
                    try:
                        target_cursor.executemany(sql_template, converted_data)
                        target_conn.commit()
                        imported_records += len(converted_data)
                        write_log(f"第 {page + 1} 页导入完成，共 {len(converted_data)} 条记录，累计导入 {imported_records}/{total_records} 条")
                        insert_success = True
                        break  # 成功则跳出重试循环
                    except Error as e:
                        if retry < max_retries - 1:
                            write_log(f"第 {page + 1} 页插入失败，重试 {retry + 1}/{max_retries}: {e}")
                            target_conn.rollback()  # 回滚事务
                            time.sleep(2)  # 等待2秒后重试
                            continue
                        else:
                            write_log(f"第 {page + 1} 页插入最终失败: {e}")
                            raise e  # 最后一次重试失败，抛出异常
                
                if not insert_success:
                    write_log(f"第 {page + 1} 页导入失败，跳过此页")
                    continue
        
        write_log(f"数据导入完成！总共导入 {imported_records} 条记录")
        
        # 保存成功的历史记录
        duration = time.time() - start_time
        save_import_history(source_table, target_table, field_mapping, import_mode, '成功', imported_records, duration)
        
    except Error as e:
        write_log(f"导入过程中发生错误: {e}")
        # 保存失败的历史记录
        duration = time.time() - start_time
        save_import_history(source_table, target_table, field_mapping, import_mode, '失败', 0, duration)
    finally:
        if source_conn:
            source_conn.close()
        if target_conn:
            target_conn.close()

@app.route('/')
def index():
    """首页"""
    return render_template('simple.html', import_modes=IMPORT_MODES)

@app.route('/original')
def original_page():
    """原始页面"""
    return render_template('index.html', import_modes=IMPORT_MODES)

@app.route('/test')
def test_page():
    """测试页面"""
    return render_template('test.html')

@app.route('/button_test')
def button_test_page():
    """按钮测试页面"""
    return render_template('button_test.html')

@app.route('/button_debug')
def button_debug_page():
    """按钮调试页面"""
    return render_template('button_debug.html')

@app.route('/config')
def config_page():
    """配置管理页面"""
    return render_template('config.html', 
                         source_db=SOURCE_DB, 
                         target_db=TARGET_DB, 
                         page_size=PAGE_SIZE)

@app.route('/history')
def history_page():
    """导入历史页面"""
    history = get_import_history()
    return render_template('history.html', history=history)

@app.route('/get_history', methods=['GET'])
def get_history_api():
    """获取导入历史记录API"""
    try:
        history = get_import_history()
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/update_config', methods=['POST'])
def update_config():
    """更新配置"""
    try:
        data = request.get_json()
        
        # 更新源数据库配置
        if 'source_db' in data:
            SOURCE_DB.update(data['source_db'])
        
        # 更新目标数据库配置
        if 'target_db' in data:
            TARGET_DB.update(data['target_db'])
        
        # 更新分页大小
        if 'page_size' in data:
            global PAGE_SIZE
            PAGE_SIZE = int(data['page_size'])
        
        return jsonify({'success': True, 'message': '配置更新成功'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/test_connection', methods=['POST'])
def test_connection():
    """测试数据库连接"""
    try:
        data = request.get_json()
        db_config = data.get('db_config')
        db_type = data.get('db_type')
        
        conn = get_db_connection(db_config)
        if conn:
            conn.close()
            return jsonify({'success': True, 'message': f'{db_type}数据库连接成功'})
        else:
            return jsonify({'success': False, 'message': f'{db_type}数据库连接失败'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/get_tables', methods=['POST'])
def get_tables_api():
    """获取数据库表列表"""
    try:
        data = request.get_json()
        db_type = data.get('db_type')  # 'source' 或 'target'
        
        print(f"收到获取表列表请求: {db_type}")
        
        if db_type == 'source':
            db_config = SOURCE_DB
            conn = get_db_connection(SOURCE_DB)
        else:
            db_config = TARGET_DB
            conn = get_db_connection(TARGET_DB)
        
        if not conn:
            error_msg = f'{db_type}数据库连接失败。请检查配置: host={db_config["host"]}, port={db_config["port"]}, user={db_config["user"]}, database={db_config["database"]}'
            print(error_msg)
            return jsonify({'success': False, 'message': error_msg})
        
        print(f"开始获取{db_type}数据库表列表...")
        tables = get_tables(conn)
        conn.close()
        
        print(f"成功获取{len(tables)}个表: {tables}")
        return jsonify({'success': True, 'tables': tables})
        
    except Exception as e:
        error_msg = f'获取表列表时发生错误: {str(e)}'
        print(error_msg)
        return jsonify({'success': False, 'message': error_msg})

@app.route('/get_fields', methods=['POST'])
def get_fields_api():
    """获取表字段信息"""
    try:
        data = request.get_json()
        source_table = data.get('source_table')
        target_table = data.get('target_table')
        
        print(f"收到字段映射请求: {source_table} -> {target_table}")
        
        if not source_table or not target_table:
            print("错误: 缺少表名参数")
            return jsonify({'success': False, 'message': '请选择源表和目标表'})
        
        # 获取源表字段
        source_conn = get_db_connection(SOURCE_DB)
        if not source_conn:
            print("错误: 源数据库连接失败")
            return jsonify({'success': False, 'message': '源数据库连接失败'})
        
        print(f"开始获取源表字段: {source_table}")
        source_fields = get_table_fields(source_conn, source_table)
        source_conn.close()
        
        # 获取目标表字段
        target_conn = get_db_connection(TARGET_DB)
        if not target_conn:
            print("错误: 目标数据库连接失败")
            return jsonify({'success': False, 'message': '目标数据库连接失败'})
        
        print(f"开始获取目标表字段: {target_table}")
        target_fields = get_table_fields(target_conn, target_table)
        target_conn.close()
        
        # 提取字段名列表
        source_field_names = [field['name'] for field in source_fields]
        target_field_names = [field['name'] for field in target_fields]
        
        print(f"源表字段数量: {len(source_field_names)}")
        print(f"目标表字段数量: {len(target_field_names)}")
        print(f"源表字段: {source_field_names[:5]}...")  # 只显示前5个
        print(f"目标表字段: {target_field_names[:5]}...")  # 只显示前5个

        # 自动匹配字段
        auto_matched_fields = auto_match_fields(source_field_names, target_field_names)
        print(f"自动匹配结果: {auto_matched_fields}")
        
        return jsonify({
            'success': True, 
            'source_fields': source_field_names,
            'target_fields': target_field_names,
            'source_fields_detail': source_fields,
            'target_fields_detail': target_fields,
            'auto_matched_fields': auto_matched_fields
        })
        
    except Exception as e:
        print(f"获取字段信息错误: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/validate_import', methods=['POST'])
def validate_import():
    """验证导入配置"""
    try:
        data = request.get_json()
        source_table = data.get('source_table')
        target_table = data.get('target_table')
        field_mapping = data.get('field_mapping', {})
        
        # 基本验证
        if not source_table or not target_table:
            return jsonify({'success': False, 'message': '请选择源表和目标表'})
        
        if not field_mapping:
            return jsonify({'success': False, 'message': '请至少映射一个字段'})
        
        # 连接数据库验证
        source_conn = get_db_connection(SOURCE_DB)
        target_conn = get_db_connection(TARGET_DB)
        
        if not source_conn:
            return jsonify({'success': False, 'message': '源数据库连接失败'})
        
        if not target_conn:
            return jsonify({'success': False, 'message': '目标数据库连接失败'})
        
        # 验证表是否存在
        source_cursor = source_conn.cursor()
        source_cursor.execute(f"SHOW TABLES LIKE '{source_table}'")
        if not source_cursor.fetchone():
            source_conn.close()
            target_conn.close()
            return jsonify({'success': False, 'message': f'源表 {source_table} 不存在'})
        
        target_cursor = target_conn.cursor()
        target_cursor.execute(f"SHOW TABLES LIKE '{target_table}'")
        if not target_cursor.fetchone():
            source_conn.close()
            target_conn.close()
            return jsonify({'success': False, 'message': f'目标表 {target_table} 不存在'})
        
        # 验证字段映射
        source_fields = get_table_fields(source_conn, source_table)
        target_fields = get_table_fields(target_conn, target_table)
        
        source_field_names = [f['name'] for f in source_fields]
        target_field_names = [f['name'] for f in target_fields]
        
        # 检查映射的字段是否存在
        for target_field, source_field in field_mapping.items():
            if target_field not in target_field_names:
                source_conn.close()
                target_conn.close()
                return jsonify({'success': False, 'message': f'目标字段 {target_field} 不存在'})
            
            if source_field not in source_field_names:
                source_conn.close()
                target_conn.close()
                return jsonify({'success': False, 'message': f'源字段 {source_field} 不存在'})
        
        source_conn.close()
        target_conn.close()
        
        return jsonify({'success': True, 'message': '配置验证通过'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/get_log', methods=['GET'])
def get_log():
    """获取导入日志"""
    try:
        if os.path.exists(LOG_FILE):
            # 尝试不同的编码方式读取文件
            encodings = ['utf-8', 'gbk', 'utf-8-sig']
            log_content = ""
            
            for encoding in encodings:
                try:
                    with open(LOG_FILE, 'r', encoding=encoding) as f:
                        log_content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if not log_content:
                log_content = "日志文件编码错误，无法读取\n"
        else:
            log_content = "日志文件不存在\n"
        
        return jsonify({'success': True, 'log': log_content})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'log': f'读取日志失败: {e}'})

@app.route('/start_import', methods=['POST'])
def start_import():
    """开始数据导入"""
    try:
        data = request.get_json()
        source_table = data.get('source_table')
        target_table = data.get('target_table')
        field_mapping = data.get('field_mapping', {})
        default_values = data.get('default_values', {})
        import_mode = data.get('import_mode', 'insert')
        
        print(f"收到导入请求: source={source_table}, target={target_table}, mode={import_mode}")
        print(f"字段映射: {field_mapping}")
        print(f"默认值: {default_values}")
        print(f"默认值类型检查:")
        for field, value in default_values.items():
            print(f"  {field}: '{value}' (类型: {type(value)})")
        
        # 基本验证
        if not source_table or not target_table:
            print("验证失败: 缺少表名")
            return jsonify({'success': False, 'message': '请选择源表和目标表'})
        
        # 验证字段映射中的目标字段是否存在于目标表中
        target_conn = get_db_connection(TARGET_DB)
        if not target_conn:
            return jsonify({'success': False, 'message': '无法连接目标数据库'})
        
        target_fields = get_table_fields(target_conn, target_table)
        target_conn.close()
        
        if not target_fields:
            return jsonify({'success': False, 'message': f'无法获取目标表 {target_table} 的字段信息'})
        
        target_field_names = [field['name'] for field in target_fields]
        
        # 检查字段映射中的目标字段是否存在于目标表中
        invalid_fields = []
        for target_field in field_mapping.keys():
            if target_field not in target_field_names:
                invalid_fields.append(target_field)
        
        if invalid_fields:
            error_msg = f"字段映射中包含不存在的目标字段: {invalid_fields}。请重新加载字段映射。"
            print(error_msg)
            write_log(error_msg)
            return jsonify({'success': False, 'message': error_msg})
        
        print(f"字段映射验证通过，目标字段: {target_field_names}")
        
        if not field_mapping:
            print("验证失败: 缺少字段映射")
            return jsonify({'success': False, 'message': '请至少映射一个字段'})
        
        print("验证通过，清空日志文件...")
        
        # 清空日志文件
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            f.write('')
        
        print("启动导入线程...")
        
        # 启动导入线程
        thread = threading.Thread(
            target=import_data_thread,
            args=(source_table, target_table, field_mapping, default_values, import_mode, data.get('page_size'))
        )
        thread.daemon = True
        thread.start()
        
        print("导入线程已启动")
        return jsonify({'success': True, 'message': '导入任务已启动'})
        
    except Exception as e:
        print(f"启动导入任务错误: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/preview_data', methods=['POST'])
def preview_data():
    """预览源表数据"""
    try:
        data = request.get_json()
        source_table = data.get('source_table')
        limit = data.get('limit', 10)  # 默认预览10条记录
        
        conn = get_db_connection(SOURCE_DB)
        if not conn:
            return jsonify({'success': False, 'message': '源数据库连接失败'})
        
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM `{source_table}` LIMIT {limit}")
        data = cursor.fetchall()
        
        # 获取字段名
        field_names = [desc[0] for desc in cursor.description]
        
        # 转换数据格式
        preview_data = []
        for row in data:
            row_dict = {}
            for i, field_name in enumerate(field_names):
                row_dict[field_name] = str(row[i]) if row[i] is not None else 'NULL'
            preview_data.append(row_dict)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True, 
            'data': preview_data,
            'fields': field_names,
            'total_previewed': len(preview_data)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/backup', methods=['POST'])
def backup_data():
    """备份目标表数据"""
    try:
        data = request.get_json()
        target_table = data.get('target_table')
        backup_name = data.get('backup_name', f"{target_table}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        if not target_table:
            return jsonify({'success': False, 'message': '请选择要备份的表'})
        
        # 连接目标数据库
        target_conn = get_db_connection(TARGET_DB)
        if not target_conn:
            return jsonify({'success': False, 'message': '目标数据库连接失败'})
        
        # 创建备份表
        backup_table = f"{backup_name}"
        cursor = target_conn.cursor()
        
        # 检查备份表是否已存在
        cursor.execute(f"SHOW TABLES LIKE '{backup_table}'")
        if cursor.fetchone():
            cursor.close()
            target_conn.close()
            return jsonify({'success': False, 'message': f'备份表 {backup_table} 已存在'})
        
        # 创建备份表
        cursor.execute(f"CREATE TABLE `{backup_table}` AS SELECT * FROM `{target_table}`")
        
        # 获取备份记录数
        cursor.execute(f"SELECT COUNT(*) FROM `{backup_table}`")
        backup_count = cursor.fetchone()[0]
        
        cursor.close()
        target_conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'备份成功！备份表: {backup_table}，记录数: {backup_count}',
            'backup_table': backup_table,
            'backup_count': backup_count
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/restore', methods=['POST'])
def restore_data():
    """从备份表恢复数据"""
    try:
        data = request.get_json()
        target_table = data.get('target_table')
        backup_table = data.get('backup_table')
        restore_mode = data.get('restore_mode', 'overwrite')  # overwrite 或 append
        
        if not target_table or not backup_table:
            return jsonify({'success': False, 'message': '请选择目标表和备份表'})
        
        # 连接目标数据库
        target_conn = get_db_connection(TARGET_DB)
        if not target_conn:
            return jsonify({'success': False, 'message': '目标数据库连接失败'})
        
        cursor = target_conn.cursor()
        
        # 检查备份表是否存在
        cursor.execute(f"SHOW TABLES LIKE '{backup_table}'")
        if not cursor.fetchone():
            cursor.close()
            target_conn.close()
            return jsonify({'success': False, 'message': f'备份表 {backup_table} 不存在'})
        
        # 获取备份记录数
        cursor.execute(f"SELECT COUNT(*) FROM `{backup_table}`")
        backup_count = cursor.fetchone()[0]
        
        if restore_mode == 'overwrite':
            # 清空目标表并恢复数据
            cursor.execute(f"TRUNCATE TABLE `{target_table}`")
            cursor.execute(f"INSERT INTO `{target_table}` SELECT * FROM `{backup_table}`")
        else:
            # 追加数据
            cursor.execute(f"INSERT INTO `{target_table}` SELECT * FROM `{backup_table}`")
        
        target_conn.commit()
        cursor.close()
        target_conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'恢复成功！从 {backup_table} 恢复了 {backup_count} 条记录到 {target_table}',
            'restored_count': backup_count
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/get_backup_tables', methods=['GET'])
def get_backup_tables():
    """获取备份表列表"""
    try:
        target_conn = get_db_connection(TARGET_DB)
        if not target_conn:
            return jsonify({'success': False, 'message': '目标数据库连接失败'})
        
        cursor = target_conn.cursor()
        cursor.execute("SHOW TABLES")
        all_tables = [table[0] for table in cursor.fetchall()]
        
        # 过滤出备份表（包含backup关键字）
        backup_tables = [table for table in all_tables if 'backup' in table.lower()]
        
        cursor.close()
        target_conn.close()
        
        return jsonify({'success': True, 'backup_tables': backup_tables})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=DEBUG)
