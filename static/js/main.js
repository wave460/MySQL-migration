// MySQL 数据库互导程序 - 前端 JavaScript

class DatabaseImporter {
    constructor() {
        this.sourceFields = [];
        this.targetFields = [];
        this.fieldMapping = {};
        this.defaultValues = {};
        this.logInterval = null;
        this.init();
    }

    init() {
        this.bindEvents();
        // 延迟加载表列表，避免页面初始化时卡顿
        setTimeout(() => {
            this.loadTables('source');
        }, 100);
        setTimeout(() => {
            this.loadTables('target');
        }, 200);
    }

    bindEvents() {
        // 使用事件委托，避免DOM元素未加载的问题
        document.addEventListener('click', (e) => {
            const target = e.target.closest('button, a');
            if (!target) return;
            
            const id = target.id;
            
            switch(id) {
                case 'loadSourceTables':
                    e.preventDefault();
                    this.loadTables('source');
                    break;
                case 'loadTargetTables':
                    e.preventDefault();
                    this.loadTables('target');
                    break;
                case 'loadFields':
                    e.preventDefault();
                    this.loadFields();
                    break;
                case 'previewData':
                    e.preventDefault();
                    this.previewData();
                    break;
                case 'startImport':
                    e.preventDefault();
                    this.startImport();
                    break;
                case 'resetMapping':
                    e.preventDefault();
                    this.resetMapping();
                    break;
                case 'backupData':
                    e.preventDefault();
                    this.showBackupModal();
                    break;
                case 'confirmBackup':
                    e.preventDefault();
                    this.performBackup();
                    break;
                case 'clearLog':
                    e.preventDefault();
                    this.clearLog();
                    break;
                case 'refreshLog':
                    e.preventDefault();
                    this.refreshLog();
                    break;
                case 'emergencyReset':
                    e.preventDefault();
                    this.forceCloseAllModals();
                    console.log('紧急恢复：已关闭所有模态框');
                    break;
            }
        });

        // 表选择变化
        document.addEventListener('change', (e) => {
            if (e.target.id === 'sourceTable' || e.target.id === 'targetTable') {
                this.checkFieldsButton();
            }
        });
    }

    async loadTables(dbType) {
        try {
            this.showLoading(`正在加载${dbType === 'source' ? '源' : '目标'}数据库表...`);
            
            // 添加超时机制
            const timeoutPromise = new Promise((_, reject) => {
                setTimeout(() => reject(new Error('请求超时，请检查网络连接')), 30000);
            });
            
            const requestPromise = axios.post('/get_tables', {
                db_type: dbType
            });
            
            const response = await Promise.race([requestPromise, timeoutPromise]);

            if (response.data.success) {
                const selectId = dbType === 'source' ? 'sourceTable' : 'targetTable';
                const select = document.getElementById(selectId);
                
                // 清空现有选项
                select.innerHTML = '<option value="">请选择表...</option>';
                
                // 使用文档片段优化性能
                const fragment = document.createDocumentFragment();
                
                // 添加表选项
                response.data.tables.forEach(table => {
                    const option = document.createElement('option');
                    option.value = table;
                    option.textContent = table;
                    fragment.appendChild(option);
                });
                
                // 一次性添加所有选项
                select.appendChild(fragment);

                this.hideLoading();
                // 不使用模态框，直接显示在页面上
                this.showInlineMessage(`${dbType === 'source' ? '源' : '目标'}数据库表加载成功 (${response.data.tables.length}个表)`, 'success');
                
                // 启用相关按钮
                this.checkFieldsButton();
                
            } else {
                this.hideLoading();
                this.showError(response.data.message);
            }
        } catch (error) {
            this.hideLoading();
            this.showError('加载表列表失败: ' + error.message);
            console.error('加载表列表错误:', error);
        }
    }

    async loadFields() {
        const sourceTable = document.getElementById('sourceTable').value;
        const targetTable = document.getElementById('targetTable').value;

        if (!sourceTable || !targetTable) {
            this.showError('请先选择源表和目标表');
            return;
        }

        try {
            this.showLoading('正在加载字段信息...');

            // 并行加载源表和目标表字段
            const [sourceResponse, targetResponse] = await Promise.all([
                axios.post('/get_fields', {
                    db_type: 'source',
                    table_name: sourceTable
                }),
                axios.post('/get_fields', {
                    db_type: 'target',
                    table_name: targetTable
                })
            ]);

            if (sourceResponse.data.success && targetResponse.data.success) {
                this.sourceFields = sourceResponse.data.fields;
                this.targetFields = targetResponse.data.fields;
                
                this.renderFieldMapping();
                this.hideLoading();
                this.showSuccess('字段信息加载成功');
            } else {
                this.hideLoading();
                this.showError('加载字段信息失败');
            }
        } catch (error) {
            this.hideLoading();
            this.showError('加载字段信息失败: ' + error.message);
        }
    }

    renderFieldMapping() {
        const tbody = document.getElementById('fieldMappingBody');
        tbody.innerHTML = '';

        this.targetFields.forEach(field => {
            const row = document.createElement('tr');
            
            // 目标字段名
            const nameCell = document.createElement('td');
            nameCell.textContent = field.name;
            nameCell.className = 'fw-bold';
            
            // 字段类型
            const typeCell = document.createElement('td');
            typeCell.textContent = field.type;
            typeCell.className = 'text-muted small';
            
            // 源字段选择
            const sourceCell = document.createElement('td');
            const sourceSelect = document.createElement('select');
            sourceSelect.className = 'form-select form-select-sm';
            sourceSelect.id = `source_${field.name}`;
            
            // 添加空选项
            const emptyOption = document.createElement('option');
            emptyOption.value = '';
            emptyOption.textContent = '-- 不映射 --';
            sourceSelect.appendChild(emptyOption);
            
            // 添加源字段选项
            this.sourceFields.forEach(sourceField => {
                const option = document.createElement('option');
                option.value = sourceField.name;
                option.textContent = `${sourceField.name} (${sourceField.type})`;
                sourceSelect.appendChild(option);
            });
            
            sourceCell.appendChild(sourceSelect);
            
            // 默认值输入
            const defaultCell = document.createElement('td');
            const defaultInput = document.createElement('input');
            defaultInput.type = 'text';
            defaultInput.className = 'form-control form-control-sm';
            defaultInput.id = `default_${field.name}`;
            defaultInput.placeholder = '默认值';
            defaultCell.appendChild(defaultInput);
            
            row.appendChild(nameCell);
            row.appendChild(typeCell);
            row.appendChild(sourceCell);
            row.appendChild(defaultCell);
            tbody.appendChild(row);
        });

        // 显示字段映射卡片
        document.getElementById('fieldMappingCard').style.display = 'block';
        document.getElementById('startImport').disabled = false;
    }

    async startImport() {
        const sourceTable = document.getElementById('sourceTable').value;
        const targetTable = document.getElementById('targetTable').value;
        const importMode = document.getElementById('importMode').value;

        if (!sourceTable || !targetTable) {
            this.showError('请先选择源表和目标表');
            return;
        }

        // 收集字段映射和默认值
        this.collectFieldMapping();

        try {
            this.showLoading('正在启动导入任务...');

            const response = await axios.post('/start_import', {
                source_table: sourceTable,
                target_table: targetTable,
                field_mapping: this.fieldMapping,
                default_values: this.defaultValues,
                import_mode: importMode
            });

            if (response.data.success) {
                this.hideLoading();
                this.showSuccess('导入任务已启动');
                this.startLogPolling();
                this.showProgressCard();
            } else {
                this.hideLoading();
                this.showError(response.data.message);
            }
        } catch (error) {
            this.hideLoading();
            this.showError('启动导入任务失败: ' + error.message);
        }
    }

    collectFieldMapping() {
        this.fieldMapping = {};
        this.defaultValues = {};

        this.targetFields.forEach(field => {
            const sourceSelect = document.getElementById(`source_${field.name}`);
            const defaultInput = document.getElementById(`default_${field.name}`);

            if (sourceSelect.value) {
                this.fieldMapping[field.name] = sourceSelect.value;
            }

            if (defaultInput.value) {
                this.defaultValues[field.name] = defaultInput.value;
            }
        });
    }

    startLogPolling() {
        // 清除之前的轮询
        if (this.logInterval) {
            clearInterval(this.logInterval);
        }

        // 立即获取一次日志
        this.refreshLog();

        // 每秒轮询日志
        this.logInterval = setInterval(() => {
            this.refreshLog();
        }, 1000);
    }

    stopLogPolling() {
        if (this.logInterval) {
            clearInterval(this.logInterval);
            this.logInterval = null;
        }
    }

    async refreshLog() {
        try {
            const response = await axios.get('/get_log');
            if (response.data.success) {
                const logContainer = document.getElementById('logContainer');
                if (response.data.log) {
                    logContainer.innerHTML = `<pre class="log-content">${response.data.log}</pre>`;
                    // 滚动到底部
                    logContainer.scrollTop = logContainer.scrollHeight;
                    
                    // 解析进度信息
                    this.parseProgressFromLog(response.data.log);
                    
                    // 检查是否导入完成
                    if (response.data.log.includes('数据导入完成！')) {
                        this.stopLogPolling();
                        this.updateProgress(100, '导入完成');
                    }
                } else {
                    logContainer.innerHTML = '<div class="text-muted text-center py-3"><i class="fas fa-info-circle"></i> 等待导入任务开始...</div>';
                }
            }
        } catch (error) {
            console.error('获取日志失败:', error);
        }
    }

    parseProgressFromLog(logContent) {
        // 解析进度百分比
        const progressMatch = logContent.match(/进度: (\d+)%/);
        if (progressMatch) {
            const percent = parseInt(progressMatch[1]);
            this.updateProgress(percent, `导入中... ${percent}%`);
        }
        
        // 解析记录数信息
        const recordMatch = logContent.match(/累计导入 (\d+)\/(\d+) 条/);
        if (recordMatch) {
            const imported = parseInt(recordMatch[1]);
            const total = parseInt(recordMatch[2]);
            const percent = Math.round((imported / total) * 100);
            this.updateProgress(percent, `已导入 ${imported}/${total} 条记录`);
        }
    }

    clearLog() {
        document.getElementById('logContainer').innerHTML = 
            '<div class="text-muted text-center py-3"><i class="fas fa-info-circle"></i> 等待导入任务开始...</div>';
    }

    resetMapping() {
        this.fieldMapping = {};
        this.defaultValues = {};
        
        // 重置所有选择框和输入框
        this.targetFields.forEach(field => {
            const sourceSelect = document.getElementById(`source_${field.name}`);
            const defaultInput = document.getElementById(`default_${field.name}`);
            
            if (sourceSelect) sourceSelect.value = '';
            if (defaultInput) defaultInput.value = '';
        });

        this.showSuccess('字段映射已重置');
    }

    async previewData() {
        const sourceTable = document.getElementById('sourceTable').value;
        
        if (!sourceTable) {
            this.showError('请先选择源表');
            return;
        }

        try {
            this.showLoading('正在加载数据预览...');

            const response = await axios.post('/preview_data', {
                source_table: sourceTable,
                limit: 10
            });

            if (response.data.success) {
                this.renderPreviewTable(response.data);
                this.hideLoading();
                
                // 显示预览模态框
                const modal = new bootstrap.Modal(document.getElementById('previewModal'));
                modal.show();
            } else {
                this.hideLoading();
                this.showError(response.data.message);
            }
        } catch (error) {
            this.hideLoading();
            this.showError('预览数据失败: ' + error.message);
        }
    }

    renderPreviewTable(data) {
        const thead = document.getElementById('previewTableHead');
        const tbody = document.getElementById('previewTableBody');
        const previewCount = document.getElementById('previewCount');
        
        // 清空表格
        thead.innerHTML = '';
        tbody.innerHTML = '';
        
        // 设置预览数量
        previewCount.textContent = data.total_previewed;
        
        // 创建表头
        const headerRow = document.createElement('tr');
        data.fields.forEach(field => {
            const th = document.createElement('th');
            th.textContent = field;
            th.className = 'text-nowrap';
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        
        // 创建数据行
        data.data.forEach(row => {
            const tr = document.createElement('tr');
            data.fields.forEach(field => {
                const td = document.createElement('td');
                td.textContent = row[field] || '';
                td.className = 'text-nowrap';
                // 限制显示长度
                if (td.textContent.length > 50) {
                    td.title = td.textContent;
                    td.textContent = td.textContent.substring(0, 50) + '...';
                }
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
    }

    checkFieldsButton() {
        const sourceTable = document.getElementById('sourceTable').value;
        const targetTable = document.getElementById('targetTable').value;
        const loadFieldsBtn = document.getElementById('loadFields');
        const previewDataBtn = document.getElementById('previewData');
        const backupDataBtn = document.getElementById('backupData');
        
        console.log('检查按钮状态:', {
            sourceTable,
            targetTable,
            loadFieldsBtn: loadFieldsBtn ? '存在' : '不存在',
            previewDataBtn: previewDataBtn ? '存在' : '不存在',
            backupDataBtn: backupDataBtn ? '存在' : '不存在'
        });
        
        if (loadFieldsBtn) {
            loadFieldsBtn.disabled = !(sourceTable && targetTable);
            console.log('loadFields按钮状态:', loadFieldsBtn.disabled ? '禁用' : '启用');
        }
        if (previewDataBtn) {
            previewDataBtn.disabled = !sourceTable;
        }
        if (backupDataBtn) {
            backupDataBtn.disabled = !targetTable;
        }
    }

    showBackupModal() {
        const targetTable = document.getElementById('targetTable').value;
        if (!targetTable) {
            this.showError('请先选择目标表');
            return;
        }
        
        document.getElementById('backupTargetTable').value = targetTable;
        document.getElementById('backupTableName').value = '';
        
        const modal = new bootstrap.Modal(document.getElementById('backupModal'));
        modal.show();
    }

    async performBackup() {
        const targetTable = document.getElementById('targetTable').value;
        const backupName = document.getElementById('backupTableName').value;
        
        try {
            this.showLoading('正在备份数据...');

            const response = await axios.post('/backup', {
                target_table: targetTable,
                backup_name: backupName || undefined
            });

            this.hideLoading();

            if (response.data.success) {
                this.showSuccess(response.data.message);
                // 关闭备份模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('backupModal'));
                modal.hide();
            } else {
                this.showError(response.data.message);
            }
        } catch (error) {
            this.hideLoading();
            this.showError('备份失败: ' + error.message);
        }
    }

    showProgressCard() {
        document.getElementById('progressCard').style.display = 'block';
        this.updateProgress(0, '准备中...');
    }

    updateProgress(percent, text) {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        progressBar.style.width = percent + '%';
        progressBar.textContent = percent + '%';
        progressText.textContent = text;
    }

    showLoading(text = '请稍候') {
        document.getElementById('loadingText').textContent = text;
        const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
        modal.show();
    }

    hideLoading() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
        if (modal) {
            modal.hide();
        }
    }

    // 强制关闭所有模态框
    forceCloseAllModals() {
        const modals = ['loadingModal', 'successModal', 'errorModal', 'previewModal', 'backupModal'];
        modals.forEach(modalId => {
            const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
            if (modal) {
                modal.hide();
            }
        });
        
        // 移除模态框背景
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
            backdrop.remove();
        }
        
        // 恢复body的滚动
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
    }

    showSuccess(message) {
        document.getElementById('successMessage').textContent = message;
        const modal = new bootstrap.Modal(document.getElementById('successModal'));
        modal.show();
        
        // 2秒后自动关闭成功提示
        setTimeout(() => {
            const modalInstance = bootstrap.Modal.getInstance(document.getElementById('successModal'));
            if (modalInstance) {
                modalInstance.hide();
            }
        }, 2000);
    }

    showError(message) {
        document.getElementById('errorMessage').textContent = message;
        const modal = new bootstrap.Modal(document.getElementById('errorModal'));
        modal.show();
    }

    // 显示内联消息（不使用模态框）
    showInlineMessage(message, type = 'info') {
        // 创建消息元素
        const messageDiv = document.createElement('div');
        messageDiv.className = `alert alert-${type === 'success' ? 'success' : 'info'} alert-dismissible fade show`;
        messageDiv.style.position = 'fixed';
        messageDiv.style.top = '20px';
        messageDiv.style.right = '20px';
        messageDiv.style.zIndex = '9999';
        messageDiv.style.minWidth = '300px';
        
        messageDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // 添加到页面
        document.body.appendChild(messageDiv);
        
        // 3秒后自动移除
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, 3000);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    new DatabaseImporter();
});
