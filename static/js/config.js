// 配置管理页面 JavaScript

class ConfigManager {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
    }

    bindEvents() {
        // 测试源数据库连接
        document.getElementById('testSourceConnection').addEventListener('click', () => {
            this.testConnection('source');
        });

        // 测试目标数据库连接
        document.getElementById('testTargetConnection').addEventListener('click', () => {
            this.testConnection('target');
        });

        // 测试所有连接
        document.getElementById('testAllConnections').addEventListener('click', () => {
            this.testAllConnections();
        });

        // 保存配置
        document.getElementById('saveConfig').addEventListener('click', () => {
            this.saveConfig();
        });

        // 重置配置
        document.getElementById('resetConfig').addEventListener('click', () => {
            this.resetConfig();
        });
    }

    async testConnection(dbType) {
        const config = this.getDbConfig(dbType);
        
        try {
            this.showLoading(`正在测试${dbType === 'source' ? '源' : '目标'}数据库连接...`);

            const response = await axios.post('/test_connection', {
                db_config: config,
                db_type: dbType === 'source' ? '源' : '目标'
            });

            this.hideLoading();

            if (response.data.success) {
                this.showSuccess(response.data.message);
            } else {
                this.showError(response.data.message);
            }
        } catch (error) {
            this.hideLoading();
            this.showError('测试连接失败: ' + error.message);
        }
    }

    async testAllConnections() {
        const sourceConfig = this.getDbConfig('source');
        const targetConfig = this.getDbConfig('target');
        
        try {
            this.showLoading('正在测试所有数据库连接...');

            const [sourceResponse, targetResponse] = await Promise.all([
                axios.post('/test_connection', {
                    db_config: sourceConfig,
                    db_type: '源'
                }),
                axios.post('/test_connection', {
                    db_config: targetConfig,
                    db_type: '目标'
                })
            ]);

            this.hideLoading();

            const sourceSuccess = sourceResponse.data.success;
            const targetSuccess = targetResponse.data.success;

            if (sourceSuccess && targetSuccess) {
                this.showSuccess('所有数据库连接测试成功！');
            } else {
                let errorMsg = '连接测试失败：\n';
                if (!sourceSuccess) {
                    errorMsg += `源数据库：${sourceResponse.data.message}\n`;
                }
                if (!targetSuccess) {
                    errorMsg += `目标数据库：${targetResponse.data.message}`;
                }
                this.showError(errorMsg);
            }
        } catch (error) {
            this.hideLoading();
            this.showError('测试连接失败: ' + error.message);
        }
    }

    async saveConfig() {
        const config = this.getConfigData();
        
        try {
            this.showLoading('正在保存配置...');

            const response = await axios.post('/update_config', config);

            this.hideLoading();

            if (response.data.success) {
                this.showSuccess('配置保存成功！');
            } else {
                this.showError(response.data.message);
            }
        } catch (error) {
            this.hideLoading();
            this.showError('保存配置失败: ' + error.message);
        }
    }

    resetConfig() {
        if (confirm('确定要重置所有配置吗？这将恢复到默认设置。')) {
            // 重置源数据库配置
            document.getElementById('sourceHost').value = 'localhost';
            document.getElementById('sourcePort').value = '3306';
            document.getElementById('sourceUser').value = 'root';
            document.getElementById('sourcePassword').value = '';
            document.getElementById('sourceDatabase').value = 'source_db';

            // 重置目标数据库配置
            document.getElementById('targetHost').value = 'localhost';
            document.getElementById('targetPort').value = '3306';
            document.getElementById('targetUser').value = 'root';
            document.getElementById('targetPassword').value = '';
            document.getElementById('targetDatabase').value = 'target_db';

            // 重置系统配置
            document.getElementById('pageSize').value = '100';

            this.showSuccess('配置已重置');
        }
    }

    getDbConfig(dbType) {
        const prefix = dbType === 'source' ? 'source' : 'target';
        
        return {
            host: document.getElementById(`${prefix}Host`).value,
            port: parseInt(document.getElementById(`${prefix}Port`).value),
            user: document.getElementById(`${prefix}User`).value,
            password: document.getElementById(`${prefix}Password`).value,
            database: document.getElementById(`${prefix}Database`).value,
            charset: 'utf8mb4'
        };
    }

    getConfigData() {
        return {
            source_db: this.getDbConfig('source'),
            target_db: this.getDbConfig('target'),
            page_size: parseInt(document.getElementById('pageSize').value)
        };
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

    showSuccess(message) {
        document.getElementById('successMessage').textContent = message;
        const modal = new bootstrap.Modal(document.getElementById('successModal'));
        modal.show();
    }

    showError(message) {
        document.getElementById('errorMessage').textContent = message;
        const modal = new bootstrap.Modal(document.getElementById('errorModal'));
        modal.show();
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    new ConfigManager();
});

