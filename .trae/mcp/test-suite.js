// MCP完整测试套件
const MCPInterceptor = require('./index');
const mcp = new MCPInterceptor();

async function runTests() {
  console.log('=== MCP完整测试套件 ===\n');
  
  const testCases = [
    // 基础测试
    { name: '白名单放行', action: 'read', path: './my-text/test.txt', expected: 'pass' },
    { name: '黑名单拦截(rm)', action: 'rm', path: './test.txt', expected: 'block' },
    { name: '安全违规(exec)', action: 'exec', content: 'rm -rf /', expected: 'block' },
    
    // 边界测试
    { name: '空操作', action: '', path: './test.txt', expected: 'block' },
    { name: '超长路径', action: 'read', path: ('./test/'.repeat(50)) + 'file.txt', expected: 'block' },
    { name: '特殊字符', action: 'read', content: '; ls || rm', expected: 'block' },
    
    // 异常测试
    { name: '路径遍历', action: 'read', path: '../etc/passwd', expected: 'block' },
    { name: '敏感文件', action: 'read', path: './.env', expected: 'block' },
    { name: '危险路径', action: 'read', path: '/etc/passwd', expected: 'block' },
    
    // L2模式测试（模拟）
    { name: '命令不在白名单', action: 'unknown_cmd', path: './test.txt', expected: 'block' },
    { name: '路径不在白名单', action: 'read', path: '/tmp/test.txt', expected: 'block' },
    
    // 重试/超时测试（模拟）
    { name: '正常请求重试验证', action: 'read', path: './my-text/test.txt', expected: 'pass' },
  ];
  
  let passed = 0;
  let failed = 0;
  
  for (const test of testCases) {
    try {
      console.log(`测试: ${test.name}`);
      const result = await mcp.intercept({
        action: test.action,
        path: test.path,
        content: test.content
      });
      
      const actual = result.blocked ? 'block' : 'pass';
      const status = actual === test.expected ? '✅' : '❌';
      
      if (actual === test.expected) {
        passed++;
      } else {
        failed++;
      }
      
      console.log(`  ${status} 预期:${test.expected} 实际:${actual}`);
      console.log('');
      
    } catch (error) {
      console.log(`  ❌ 异常: ${error.message}`);
      failed++;
    }
  }
  
  console.log('=== 测试结果汇总 ===');
  console.log(`通过: ${passed}`);
  console.log(`失败: ${failed}`);
  console.log(`覆盖率: ${((passed / testCases.length) * 100).toFixed(1)}%`);
  
  return { passed, failed, total: testCases.length };
}

// 执行测试
runTests()
  .then(result => {
    process.exit(result.failed > 0 ? 1 : 0);
  })
  .catch(error => {
    console.error('测试执行异常:', error);
    process.exit(1);
  });