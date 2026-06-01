// 标准MCP服务端 - JSON-RPC 2.0协议
// 严格遵循MCP stdio协议规范

const MCPInterceptor = require('./index');
const mcp = new MCPInterceptor();

// JSON-RPC 2.0响应
function createResponse(id, result) {
    return JSON.stringify({
        jsonrpc: '2.0',
        result: result,
        id: id
    });
}

function createError(id, code, message) {
    return JSON.stringify({
        jsonrpc: '2.0',
        error: {
            code: code,
            message: message
        },
        id: id
    });
}

// 处理MCP请求
async function handleMethod(method, params, id) {
    switch (method) {
        case 'intercept':
            const result = await mcp.intercept(params);
            return createResponse(id, result);
        
        case 'health':
            return createResponse(id, { status: 'ok' });
        
        case 'getRules':
            return createResponse(id, {
                L1: ['security', 'whitelist', 'blacklist'],
                L2: ['strict', 'soft'],
                L3: ['suggestions']
            });
        
        default:
            return createError(id, -32601, 'Method not found');
    }
}

// stdio主循环
async function main() {
    let buffer = '';

    process.stdin.setEncoding('utf8');
    process.stdin.on('data', async (data) => {
        buffer += data;
        
        try {
            // 支持单行JSON或多行
            const lines = buffer.split('\n').filter(line => line.trim());
            
            for (const line of lines) {
                if (!line.trim()) continue;
                
                const request = JSON.parse(line);
                
                if (request.jsonrpc !== '2.0') {
                    console.log(createError(request.id, -32600, 'Invalid Request'));
                    continue;
                }
                
                const response = await handleMethod(request.method, request.params, request.id);
                console.log(response);
            }
            
            buffer = '';
        } catch (error) {
            // 可能是不完整的JSON，继续等待
        }
    });

    process.stdin.on('end', () => {
        process.exit(0);
    });
}

main().catch(error => {
    console.error('MCP Server Error:', error);
    process.exit(1);
});