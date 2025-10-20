# MySQL 数据库互导程序

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-5.7+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**一个功能强大的 MySQL 数据库互导管理系统**

支持字段映射、智能匹配、实时监控、数据备份等功能

[快速开始](#-快速开始) • [功能特性](#-功能特性) • [技术栈](#-技术栈) • [安装指南](#-安装指南) • [使用说明](#-使用说明) • [API文档](#-api文档) • [故障排除](#-故障排除)

</div>

---

## 📖 项目简介

MySQL 数据库互导程序是一个基于 Python Flask 框架开发的 Web 应用程序，专门用于在不同 MySQL 数据库之间进行数据迁移和同步。该系统提供了直观的 Web 界面，支持字段映射、数据预览、实时进度监控、智能字段匹配等功能，是数据库迁移、测试环境数据填充、数据同步等场景的理想解决方案。

### 🎯 应用场景

- **数据库迁移**: 从旧系统迁移到新系统
- **测试环境数据填充**: 将生产数据复制到测试环境
- **数据同步**: 在不同数据库之间同步数据
- **数据清洗**: 在导入过程中进行数据转换和清洗
- **备份恢复**: 数据库备份和恢复操作
- **ETL 任务**: 小型数据提取、转换、加载任务

---

## ✨ 功能特性

### 🔄 核心功能
- **🔄 数据导入导出**: 支持 MySQL 数据库之间的数据迁移
- **🎯 智能字段匹配**: 自动识别相似字段名，支持精确匹配、规则匹配和模糊匹配
- **📊 可视化字段映射**: 直观的字段映射界面，支持手动调整和默认值设置
- **👁️ 数据预览**: 导入前预览源表数据，确认数据格式和内容
- **⚡ 实时进度监控**: 实时显示导入进度、状态和详细日志
- **💾 数据备份**: 导入前自动备份目标表数据
- **📈 导入历史**: 记录所有导入任务的详细信息

### 🛠️ 高级功能
- **🔧 配置管理**: 可视化数据库连接配置和系统参数设置
- **🔍 连接测试**: 实时测试数据库连接状态
- **📄 分页导入**: 支持大数据量分页导入，避免内存溢出
- **🔄 导入模式**: 支持覆盖模式和仅新增模式
- **📝 详细日志**: 完整的导入过程日志记录
- **🎨 响应式界面**: 适配各种屏幕尺寸的现代化界面

### 🔒 安全特性
- **🔐 连接安全**: 支持 SSL 加密连接
- **🛡️ 数据验证**: 导入前验证字段映射和数据完整性
- **💾 自动备份**: 导入前自动创建数据备份
- **📊 权限控制**: 基于数据库用户权限的安全控制

---

## 🛠️ 技术栈

### 后端技术
| 技术 | 版本 | 说明 |
|------|------|------|
| **Python** | 3.10+ | 核心开发语言 |
| **Flask** | 3.0.3 | Web 框架 |
| **mysql-connector-python** | 8.0+ | MySQL 数据库连接器 |
| **Threading** | 内置 | 异步任务处理 |

### 前端技术
| 技术 | 版本 | 说明 |
|------|------|------|
| **HTML5** | - | 页面结构 |
| **CSS3** | - | 样式设计 |
| **JavaScript (ES6+)** | - | 交互逻辑 |
| **Bootstrap** | 5.3+ | UI 框架 |
| **Axios** | 1.6+ | HTTP 客户端 |
| **Font Awesome** | 6.0+ | 图标库 |

### 数据库
| 数据库 | 版本 | 说明 |
|--------|------|------|
| **MySQL** | 5.7+ / 8.0+ | 源数据库和目标数据库 |

### 开发工具
| 工具 | 说明 |
|------|------|
| **Git** | 版本控制 |
| **VS Code** | 推荐开发环境 |
| **Chrome DevTools** | 前端调试 |

---

## 🚀 快速开始

### 环境要求

- **Python**: 3.10 或更高版本
- **MySQL**: 5.7 或更高版本
- **操作系统**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **内存**: 建议 2GB 以上
- **磁盘空间**: 至少 100MB 可用空间

### 一键安装

```bash
# 克隆项目
git clone https://github.com/wave460/MySQL-migration.git
cd MySQL-migration

# 安装依赖
pip install -r requirements.txt

# 配置数据库（编辑 config.py）
# 启动应用
python app.py
```

### 访问应用

打开浏览器访问：http://localhost:5000

---

## 📦 安装指南

### 1. 环境准备

#### Windows 系统
```bash
# 安装 Python 3.10+
# 下载地址: https://www.python.org/downloads/

# 安装 MySQL
# 下载地址: https://dev.mysql.com/downloads/mysql/

# 验证安装
python --version
mysql --version
```

#### Linux 系统 (Ubuntu/Debian)
```bash
# 更新包管理器
sudo apt update

# 安装 Python 3.10+
sudo apt install python3.10 python3.10-pip python3.10-venv

# 安装 MySQL
sudo apt install mysql-server mysql-client

# 验证安装
python3 --version
mysql --version
```

#### macOS 系统
```bash
# 使用 Homebrew 安装
brew install python@3.10 mysql

# 验证安装
python3 --version
mysql --version
```

### 2. 项目安装

```bash
# 1. 克隆项目
git clone https://github.com/wave460/MySQL-migration.git
cd mysql-data-migration

# 2. 创建虚拟环境（推荐）
python -m venv venv

# 3. 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt
```

### 3. 数据库配置

编辑 `config.py` 文件：

```python
# 源数据库配置
SOURCE_DB = {
    'host': 'localhost',        # 数据库主机地址
    'port': 3306,              # 端口号
    'user': 'root',            # 用户名
    'password': 'your_password', # 密码
    'database': 'source_db',   # 数据库名
    'charset': 'utf8mb4'       # 字符集
}

# 目标数据库配置
TARGET_DB = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'your_password',
    'database': 'target_db',
    'charset': 'utf8mb4'
}

# 系统配置
PAGE_SIZE = 500                # 每页导入记录数
LOG_FILE = 'logs/import.log'   # 日志文件路径
DEBUG = False                  # 调试模式
SECRET_KEY = 'your-secret-key' # Flask 密钥
```

### 4. 启动应用

```bash
# 方法1: 直接运行
python app.py

# 方法2: 使用启动脚本
# Windows
start.bat

# Linux/macOS
chmod +x start.sh
./start.sh

# 方法3: 生产环境部署
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 📖 使用说明

### 基本使用流程

#### 1. 选择数据表
1. 访问 http://localhost:5000
2. 点击"刷新"按钮加载数据库表列表
3. 分别选择源表和目标表

#### 2. 预览数据（可选）
1. 点击"预览数据"按钮
2. 查看源表的前10条记录
3. 确认数据格式和内容

#### 3. 字段映射
1. 点击"加载字段映射"按钮
2. 系统自动进行智能字段匹配
3. 手动调整字段映射关系
4. 为未映射字段设置默认值

#### 4. 选择导入模式
- **覆盖模式**: 使用 `REPLACE INTO`，覆盖重复数据
- **仅新增模式**: 使用 `INSERT IGNORE`，只插入新数据

#### 5. 数据备份（推荐）
1. 点击"备份数据"按钮
2. 系统创建目标表的完整备份

#### 6. 开始导入
1. 点击"开始导入"按钮
2. 实时监控导入进度
3. 查看详细日志信息

### 高级功能使用

#### 智能字段匹配
系统提供三种匹配策略：

1. **精确匹配**: 字段名完全相同
2. **规则匹配**: 基于预定义规则的匹配
3. **模糊匹配**: 使用相似度算法匹配

```javascript
// 匹配规则示例
field_mapping_rules = {
    'id': ['itemid', 'aid', 'uid', 'userid'],
    'title': ['title', 'subject', 'name', 'caption'],
    'content': ['content', 'body', 'text', 'description'],
    'time': ['time', 'date', 'addtime', 'createtime']
}
```

#### 配置管理
访问配置管理页面进行系统设置：

1. **数据库连接配置**
2. **系统参数调整**
3. **连接状态测试**
4. **配置保存和重置**

#### 导入历史
查看所有导入任务的详细信息：

- 导入时间
- 源表和目标表
- 导入模式
- 成功/失败状态
- 导入记录数
- 耗时统计

---

## 🔌 API 文档

### 核心接口

#### 获取数据库表列表
```http
POST /get_tables
Content-Type: application/json

{
    "db_type": "source" | "target"
}
```

**响应示例**:
```json
{
    "success": true,
    "tables": ["table1", "table2", "table3"]
}
```

#### 获取字段信息
```http
POST /get_fields
Content-Type: application/json

{
    "source_table": "source_table_name",
    "target_table": "target_table_name"
}
```

**响应示例**:
```json
{
    "success": true,
    "source_fields": ["field1", "field2"],
    "target_fields": ["field1", "field2"],
    "auto_matched_fields": {
        "field1": "field1",
        "field2": "field2"
    }
}
```

#### 开始数据导入
```http
POST /start_import
Content-Type: application/json

{
    "source_table": "source_table",
    "target_table": "target_table",
    "field_mapping": {
        "target_field": "source_field"
    },
    "default_values": {
        "field": "default_value"
    },
    "import_mode": "insert" | "overwrite",
    "page_size": 500
}
```

#### 获取导入日志
```http
GET /get_log
```

**响应示例**:
```json
{
    "success": true,
    "log": "导入日志内容..."
}
```

### 配置管理接口

#### 更新配置
```http
POST /update_config
Content-Type: application/json

{
    "source_db": {...},
    "target_db": {...},
    "page_size": 500
}
```

#### 测试连接
```http
POST /test_connection
Content-Type: application/json

{
    "db_config": {...}
}
```

---

## 🔧 故障排除

### 常见问题及解决方案

#### 1. 数据库连接失败

**问题**: 无法连接到数据库
**解决方案**:
```bash
# 检查数据库服务状态
# Windows
net start mysql

# Linux
sudo systemctl status mysql
sudo systemctl start mysql

# 测试连接
mysql -h localhost -u root -p
```

**检查项目**:
- 数据库服务是否启动
- 连接参数是否正确
- 网络连接是否正常
- 防火墙设置

#### 2. 字段映射错误

**问题**: 字段不存在或类型不匹配
**解决方案**:
```sql
-- 检查表结构
DESCRIBE table_name;
SHOW CREATE TABLE table_name;

-- 检查字段类型
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'your_table';
```

#### 3. 导入性能问题

**问题**: 导入速度慢或超时
**解决方案**:
```python
# 调整分页大小
PAGE_SIZE = 1000  # 增加分页大小

# 优化数据库连接
connection_timeout = 60
autocommit = True
```

#### 4. 内存不足

**问题**: 导入大表时内存溢出
**解决方案**:
- 减小 `PAGE_SIZE` 参数
- 增加系统内存
- 使用 SSD 硬盘
- 优化数据库配置

### 日志分析

#### 查看导入日志
```bash
# 实时查看日志
tail -f logs/import.log

# 查看错误日志
grep -i error logs/import.log

# 查看特定时间段的日志
grep "2024-01-01" logs/import.log
```

#### 常见错误信息

| 错误代码 | 错误信息 | 解决方案 |
|---------|---------|---------|
| 1045 | Access denied | 检查用户名和密码 |
| 2003 | Can't connect to MySQL server | 检查数据库服务状态 |
| 1054 | Unknown column | 检查字段映射 |
| 1364 | Field doesn't have a default value | 设置默认值 |

---

## 🔒 安全考虑

### 数据安全
- **备份策略**: 导入前自动备份目标表
- **权限控制**: 基于数据库用户权限
- **数据验证**: 导入前验证数据完整性
- **日志记录**: 完整的操作日志

### 网络安全
- **SSL 连接**: 支持加密数据库连接
- **访问控制**: 限制应用访问范围
- **防火墙**: 配置适当的防火墙规则

### 最佳实践
1. **测试环境验证**: 在生产环境使用前先在测试环境验证
2. **定期备份**: 定期备份重要数据
3. **权限最小化**: 使用最小必要权限
4. **监控日志**: 定期检查操作日志

---

## 🚀 性能优化

### 数据库优化
```sql
-- 创建索引
CREATE INDEX idx_field ON table_name(field_name);

-- 优化查询
EXPLAIN SELECT * FROM table_name WHERE condition;

-- 调整 MySQL 配置
[mysqld]
innodb_buffer_pool_size = 1G
max_connections = 200
```

### 应用优化
```python
# 调整分页大小
PAGE_SIZE = 1000  # 根据服务器性能调整

# 连接池配置
connection_pool_size = 10
connection_timeout = 60
```

### 系统优化
- **SSD 硬盘**: 使用 SSD 提高 I/O 性能
- **内存配置**: 增加系统内存
- **网络优化**: 确保网络连接稳定
- **并发控制**: 避免同时进行多个导入任务

---

## 📊 监控和维护

### 系统监控
- **CPU 使用率**: 监控 CPU 使用情况
- **内存使用率**: 监控内存使用情况
- **磁盘空间**: 监控磁盘空间使用
- **网络连接**: 监控网络连接状态

### 日志管理
```bash
# 日志轮转
logrotate /etc/logrotate.d/mysql-migration

# 清理旧日志
find logs/ -name "*.log" -mtime +30 -delete
```

### 定期维护
1. **清理备份表**: 定期清理不需要的备份表
2. **更新依赖**: 定期更新 Python 包
3. **安全检查**: 定期进行安全审计
4. **性能调优**: 根据使用情况调整配置

---

## 🤝 贡献指南

### 开发环境设置
```bash
# 克隆项目
git clone https://github.com/wave460/MySQL-migration.git
cd mysql-migration

# 创建开发分支
git checkout -b feature/your-feature

# 安装开发依赖
pip install -r requirements-dev.txt
```

### 代码规范
- 遵循 PEP 8 Python 代码规范
- 使用有意义的变量和函数名
- 添加适当的注释和文档字符串
- 编写单元测试

### 提交规范
```bash
# 提交信息格式
git commit -m "feat: 添加新功能"
git commit -m "fix: 修复bug"
git commit -m "docs: 更新文档"
git commit -m "style: 代码格式调整"
```

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 🆘 技术支持

### 获取帮助
- **文档**: 查看本文档和 [使用说明](使用说明.md)
- **Issues**: 在 GitHub 上提交问题
- **讨论**: 参与 GitHub Discussions
- **邮件**: 发送邮件到 support@example.com

### 联系方式
- **技术支持**: [一码工坊](http://www.wangyiyi.net)
- **项目主页**:https://github.com/wave460/MySQL-migration.git
- **问题反馈**: https://github.com/wave460/MySQL-migration/issues

---

## 📈 版本历史

### v2.0.0 (2024-01-01)
- ✨ 新增智能字段匹配功能
- ✨ 新增数据预览功能
- ✨ 新增实时进度监控
- ✨ 新增配置管理界面
- ✨ 新增导入历史记录
- ✨ 新增数据备份功能
- 🔧 优化用户界面设计
- 🔧 提升导入性能
- 🐛 修复多个已知问题

### v1.0.0 (2023-12-01)
- 🎉 初始版本发布
- ✨ 基本数据导入功能
- ✨ 字段映射功能
- ✨ Web 界面

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我们一个 Star！**

Made with ❤️ by [一码工坊](http://www.wangyiyi.net)

</div>
