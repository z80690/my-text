const { spawn } = require('child_process');

const child = spawn('npx', ['trae-auto-memory-mcp'], {
  stdio: ['pipe', 'pipe', 'pipe']
});

child.stderr.on('data', (data) => {
  console.log('Server Log:', data.toString());
});

child.stdout.on('data', (data) => {
  console.log('Server Output:', data.toString());
});

setTimeout(() => {
  const testMessage = JSON.stringify({
    jsonrpc: '2.0',
    id: 1,
    method: 'tools/list'
  }) + '\n';
  
  console.log('Sending test message...');
  child.stdin.write(testMessage);
}, 2000);

setTimeout(() => {
  const testMessage2 = JSON.stringify({
    jsonrpc: '2.0',
    id: 2,
    method: 'tools/call',
    params: {
      name: 'process_message',
      arguments: {
        message: '我喜欢使用 TypeScript 开发项目'
      }
    }
  }) + '\n';
  
  console.log('Sending test message 2...');
  child.stdin.write(testMessage2);
}, 3000);

setTimeout(() => {
  console.log('\n✅ Test completed successfully!');
  child.kill();
  process.exit(0);
}, 5000);
