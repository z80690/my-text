// MCP执行拦截层 - 入口文件
// 职责：绑定L1硬约束，强制执行安全拦截

const fs = require('fs');
const path = require('path');

class MCPInterceptor {
  constructor() {
    this.config = this.loadConfig();
    this.rules = this.loadL1Rules();
    this.logDir = path.join(__dirname, '..', 'logs');
    this.ensureLogDir();
  }

  loadConfig() {
    const configPath = path.join(__dirname, 'config.json');
    return JSON.parse(fs.readFileSync(configPath, 'utf-8'));
  }

  loadL1Rules() {
    const L1Path = path.join(__dirname, '..', 'rules', 'L1');
    return {
      security: this.loadJSON(path.join(L1Path, 'security.json')),
      whitelist: this.loadJSON(path.join(L1Path, 'whitelist.json')),
      blacklist: this.loadJSON(path.join(L1Path, 'blacklist.json'))
    };
  }

  loadJSON(filePath) {
    try {
      return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
    } catch {
      return {};
    }
  }

  ensureLogDir() {
    if (!fs.existsSync(this.logDir)) {
      fs.mkdirSync(this.logDir, { recursive: true });
    }
  }

  generateRequestId() {
    return 'REQ-' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
  }

  log(level, layer, description) {
    const logEntry = {
      request_id: this.currentRequestId,
      level: level,
      layer: layer,
      description: description,
      timestamp: new Date().toISOString()
    };
    
    const logLine = JSON.stringify(logEntry) + '\n';
    const logFile = level === 'ERROR' ? 'error.log' : 'warn.log';
    
    fs.appendFileSync(path.join(this.logDir, logFile), logLine);
    console.log(logLine.trim());
    
    return logEntry;
  }

  async intercept(request, retryCount = 0) {
    this.currentRequestId = request.request_id || this.generateRequestId();
    const startTime = Date.now();
    
    try {
      // 1. 安全底线校验
      const securityCheck = this.checkSecurity(request);
      if (securityCheck.blocked) {
        const log = this.log('ERROR', 'L1', `安全违规: ${securityCheck.reason}`);
        return { blocked: true, message: '服务暂时繁忙，请稍后再试', log: log };
      }

      // 2. 黑名单校验
      const blacklistCheck = this.checkBlacklist(request);
      if (blacklistCheck.blocked) {
        const suggestion = this.getSuggestion(request.action);
        const log = this.log('ERROR', 'L1', `黑名单命中: ${blacklistCheck.reason}`);
        return { blocked: true, message: suggestion || '服务暂时繁忙，请稍后再试', log: log };
      }

      // 3. 白名单校验
      const whitelistCheck = this.checkWhitelist(request);
      if (!whitelistCheck.allowed) {
        const log = this.log('WARN', 'L1', `不在白名单: ${whitelistCheck.reason}`);
        return { blocked: true, message: '暂不支持该操作', log: log };
      }

      // 4. 放行
      const log = this.log('INFO', 'MCP', '安全检查通过，放行');
      return { blocked: false, log: log };

    } catch (error) {
      // 重试逻辑
      if (retryCount < this.config.interception.retry_count) {
        await this.delay(this.config.interception.retry_interval_ms);
        return this.intercept(request, retryCount + 1);
      }

      // 超时兜底
      const elapsed = Date.now() - startTime;
      if (elapsed > this.config.interception.total_timeout_ms) {
        const log = this.log('ERROR', 'MCP', `超时兜底: 耗时${elapsed}ms`);
        return { blocked: true, message: '服务暂时繁忙，请稍后再试', log: log };
      }

      const log = this.log('ERROR', 'MCP', `执行异常: ${error.message}`);
      return { blocked: true, message: '服务暂时繁忙，请稍后再试', log: log };
    }
  }

  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  checkSecurity(request) {
    const security = this.rules.security;
    const action = request.action?.toLowerCase();
    const content = request.content?.toLowerCase();
    const requestPath = request.path?.toLowerCase();

    // 检查危险命令
    if (security.blocked_commands?.some(cmd => action?.includes(cmd) || content?.includes(cmd))) {
      return { blocked: true, reason: `包含危险命令: ${action}` };
    }

    // 检查危险模式
    if (security.blocked_patterns?.some(pattern => {
      try {
        const regex = new RegExp(pattern);
        return regex.test(content || '') || regex.test(requestPath || '');
      } catch {
        return (content || '').includes(pattern) || (requestPath || '').includes(pattern);
      }
    })) {
      return { blocked: true, reason: `包含危险模式` };
    }

    // 检查危险关键词
    if (security.blocked_keywords?.some(kw => content?.includes(kw))) {
      return { blocked: true, reason: `包含危险关键词` };
    }

    // 检查路径长度
    if (security.path_length_limit && requestPath && requestPath.length > security.path_length_limit) {
      return { blocked: true, reason: `路径过长: ${requestPath.length} > ${security.path_length_limit}` };
    }

    // 检查内容长度
    if (security.content_length_limit && content && content.length > security.content_length_limit) {
      return { blocked: true, reason: `内容过长: ${content.length} > ${security.content_length_limit}` };
    }

    return { blocked: false };
  }

  checkBlacklist(request) {
    const blacklist = this.rules.blacklist;
    const action = request.action?.toLowerCase();
    const requestPath = request.path?.toLowerCase();

    // 检查命令黑名单
    if (blacklist.blocked_commands?.includes(action)) {
      return { blocked: true, reason: `命令${action}在黑名单` };
    }

    // 检查文件黑名单
    const fileName = path.basename(requestPath || '');
    if (blacklist.blocked_files?.includes(fileName)) {
      return { blocked: true, reason: `文件${fileName}在黑名单` };
    }

    // 检查路径黑名单
    if (blacklist.blocked_paths?.some(p => requestPath?.startsWith(p.toLowerCase()))) {
      return { blocked: true, reason: `路径${requestPath}在黑名单` };
    }

    return { blocked: false };
  }

  checkWhitelist(request) {
    const whitelist = this.rules.whitelist;
    const action = request.action?.toLowerCase();
    const requestPath = request.path?.toLowerCase();

    // 检查命令白名单
    if (whitelist.allowed_commands && !whitelist.allowed_commands.includes(action)) {
      return { allowed: false, reason: `命令${action}不在白名单` };
    }

    // 检查路径白名单
    if (whitelist.allowed_paths && !whitelist.allowed_paths.some(p => 
      requestPath?.startsWith(p.toLowerCase())
    )) {
      return { allowed: false, reason: `路径${requestPath}不在白名单` };
    }

    return { allowed: true };
  }

  getSuggestion(action) {
    const suggestions = {
      'rm': '建议使用 mv 替代 rm，防止误删',
      'exec': '禁止直接执行系统命令，请使用封装接口',
      'run': '禁止直接执行系统命令，请使用封装接口',
      'shell': '禁止直接执行系统命令，请使用封装接口'
    };
    return suggestions[action?.toLowerCase()];
  }
}

// 命令行测试
if (require.main === module) {
  const mcp = new MCPInterceptor();
  
  // 解析命令行参数
  const args = process.argv.slice(2);
  const params = {};
  args.forEach(arg => {
    const [key, value] = arg.split('=');
    if (key && value) {
      params[key.replace('--', '')] = value;
    }
  });

  if (Object.keys(params).length > 0) {
    mcp.intercept(params).then(result => {
      console.log('\n=== 测试结果 ===');
      console.log(JSON.stringify(result, null, 2));
    });
  } else {
    // 默认测试用例
    console.log('=== 默认测试 ===');
    
    mcp.intercept({ action: 'read', path: './test.txt' }).then(console.log);
    mcp.intercept({ action: 'rm', path: './test.txt' }).then(console.log);
    mcp.intercept({ action: 'exec', content: 'rm -rf /' }).then(console.log);
  }
}

module.exports = MCPInterceptor;