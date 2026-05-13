"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const index_js_1 = require("@modelcontextprotocol/sdk/server/index.js");
const stdio_js_1 = require("@modelcontextprotocol/sdk/server/stdio.js");
const types_js_1 = require("@modelcontextprotocol/sdk/types.js");
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
class AutoMemorySystem {
    constructor() {
        this.memoriesDir = path.join('.trae', 'memories');
        this.ensureDirectories();
    }
    ensureDirectories() {
        const dirs = ['user', 'feedback', 'project', 'reference'];
        dirs.forEach(dir => {
            const dirPath = path.join(this.memoriesDir, dir);
            if (!fs.existsSync(dirPath)) {
                fs.mkdirSync(dirPath, { recursive: true });
            }
        });
    }
    isDarkKnowledge(message) {
        const brightPatterns = [
            /\b(React|Vue|Node|Python|Java|Go|Rust)\s+\d+\.\d+(\.\d+)?\b/i,
            /\b(在|位于|路径|文件)\s*[\w./\\-]+\.(js|ts|py|md|json)\b/i,
            /\b(def|function|class)\s+[\w_]+\b/,
        ];
        for (const pattern of brightPatterns) {
            if (pattern.test(message)) {
                return { isDark: false, reason: '明知识' };
            }
        }
        const darkPatterns = [
            { pattern: /习惯|喜欢|偏好|风格/i, reason: '用户偏好' },
            { pattern: /很好|认可|以后都这样|建议|改进/i, reason: '用户反馈' },
            { pattern: /禁止|必须|我们团队/i, reason: '团队规则' },
            { pattern: /因为要|为了兼容|历史遗留|设计原因/i, reason: '设计决策' },
            { pattern: /系统|项目启动|项目背景/i, reason: '项目背景' },
            { pattern: /Jira|票号|文档在|链接|参考/i, reason: '外部引用' },
        ];
        for (const { pattern, reason } of darkPatterns) {
            if (pattern.test(message)) {
                return { isDark: true, reason };
            }
        }
        return { isDark: false, reason: '无法分类' };
    }
    classify(message) {
        if (/习惯|喜欢|偏好|风格/i.test(message))
            return 'user';
        if (/很好|认可|以后都这样|建议|改进/i.test(message))
            return 'feedback';
        if (/禁止|必须|我们团队|因为要|为了兼容|历史遗留|设计原因|系统|项目启动|项目背景/i.test(message))
            return 'project';
        if (/Jira|票号|文档在|链接|参考/i.test(message))
            return 'reference';
        return 'user';
    }
    writeMemory(message, memType) {
        const sanitized = message.replace(/[^\w\u4e00-\u9fa5\-_]/g, '_').substring(0, 20);
        const filename = sanitized.replace(/_+/g, '_').replace(/^_|_$/g, '') || 'memory';
        const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
        const content = `---
type: ${memType}
created: ${timestamp}
---

# ${message.substring(0, 30)}...

${message}

**Why:** ${this.isDarkKnowledge(message).reason}
**How to apply:** 根据记忆类型自动触发
`;
        let filepath = path.join(this.memoriesDir, memType, `${filename}.md`);
        let counter = 1;
        while (fs.existsSync(filepath)) {
            filepath = path.join(this.memoriesDir, memType, `${filename}_${counter}.md`);
            counter++;
        }
        fs.writeFileSync(filepath, content, 'utf-8');
        return filepath;
    }
    process(message) {
        const { isDark, reason } = this.isDarkKnowledge(message);
        if (isDark) {
            const memType = this.classify(message);
            const filepath = this.writeMemory(message, memType);
            return {
                auto_saved: true,
                type: memType,
                path: filepath,
                reason: reason
            };
        }
        return {
            auto_saved: false,
            reason: reason
        };
    }
}
const server = new index_js_1.Server({
    name: 'auto-memory-mcp',
    version: '1.0.0',
}, {
    capabilities: {
        tools: {},
    },
});
const memorySystem = new AutoMemorySystem();
server.setRequestHandler(types_js_1.ListToolsRequestSchema, async () => {
    return {
        tools: [
            {
                name: 'process_message',
                description: '处理用户消息，自动识别暗知识并保存到记忆库',
                inputSchema: {
                    type: 'object',
                    properties: {
                        message: {
                            type: 'string',
                            description: '用户消息内容'
                        }
                    },
                    required: ['message']
                }
            }
        ]
    };
});
server.setRequestHandler(types_js_1.CallToolRequestSchema, async (request) => {
    try {
        const { message } = request.params.arguments;
        const result = memorySystem.process(message);
        return {
            content: [
                {
                    type: 'text',
                    text: JSON.stringify(result, null, 2)
                }
            ]
        };
    }
    catch (error) {
        return {
            content: [
                {
                    type: 'text',
                    text: `Error: ${error instanceof Error ? error.message : String(error)}`
                }
            ],
            isError: true
        };
    }
});
async function main() {
    const transport = new stdio_js_1.StdioServerTransport();
    await server.connect(transport);
    console.error('Auto Memory MCP Server started');
}
main().catch(console.error);
//# sourceMappingURL=index.js.map