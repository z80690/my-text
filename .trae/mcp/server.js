const http = require('http');
const url = require('url');
const MCPInterceptor = require('./index');

const PORT = 3000;
const mcp = new MCPInterceptor();

const server = http.createServer(async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;

  if (pathname === '/api/intercept' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', async () => {
      try {
        const request = JSON.parse(body);
        const result = await mcp.intercept(request);

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          success: true,
          data: result
        }));
      } catch (error) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          success: false,
          error: error.message
        }));
      }
    });
    return;
  }

  if (pathname === '/api/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      success: true,
      status: 'ok',
      timestamp: new Date().toISOString()
    }));
    return;
  }

  if (pathname === '/api/rules') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      success: true,
      data: {
        L1: ['security.json', 'whitelist.json', 'blacklist.json'],
        L2: ['strict.json', 'soft.json'],
        L3: ['suggestions.json']
      }
    }));
    return;
  }

  if (pathname === '/' || pathname === '/index.html') {
    const fs = require('fs');
    const path = require('path');
    const htmlPath = path.join(__dirname, 'config-ui.html');
    const html = fs.readFileSync(htmlPath, 'utf-8');
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(html);
    return;
  }

  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ success: false, error: 'Not found' }));
});

server.listen(PORT, () => {
  console.log(`=== MCP服务已启动 ===`);
  console.log(`访问地址: http://localhost:${PORT}`);
  console.log(`健康检查: http://localhost:${PORT}/api/health`);
  console.log(`测试接口: POST http://localhost:${PORT}/api/intercept`);
  console.log(`========================`);
});