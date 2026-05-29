const http = require('http');

const BASE_URL = 'http://localhost:3000';

function httpRequest(method, path, data = null) {
    return new Promise((resolve, reject) => {
        const url = new URL(path, BASE_URL);
        const options = {
            hostname: url.hostname,
            port: url.port,
            path: url.pathname + url.search,
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        const req = http.request(options, (res) => {
            let body = '';
            res.on('data', chunk => { body += chunk; });
            res.on('end', () => {
                try {
                    resolve({ statusCode: res.statusCode, data: JSON.parse(body) });
                } catch (e) {
                    resolve({ statusCode: res.statusCode, data: body });
                }
            });
        });

        req.on('error', reject);
        if (data) {
            req.write(JSON.stringify(data));
        }
        req.end();
    });
}

async function runTests() {
    console.log('=== AB Test: Task Management API Tests ===\n');

    let passed = 0;
    let failed = 0;

    async function test(name, fn) {
        try {
            await fn();
            console.log(`✅ PASS: ${name}`);
            passed++;
        } catch (e) {
            console.log(`❌ FAIL: ${name}`);
            console.log(`   Error: ${e.message}`);
            failed++;
        }
    }

    console.log('--- Health Check ---');
    await test('Health check returns ok', async () => {
        const res = await httpRequest('GET', '/health');
        if (res.statusCode !== 200) throw new Error(`Expected 200, got ${res.statusCode}`);
        if (res.data.status !== 'ok') throw new Error('Status not ok');
    });

    console.log('\n--- User CRUD Tests ---');

    let createdUserId;
    await test('Create user with valid data', async () => {
        const res = await httpRequest('POST', '/api/users', {
            username: 'testuser',
            email: 'test@example.com'
        });
        if (res.statusCode !== 201) throw new Error(`Expected 201, got ${res.statusCode}`);
        if (!res.data.id) throw new Error('User ID not returned');
        createdUserId = res.data.id;
    });

    await test('Create user with invalid email', async () => {
        const res = await httpRequest('POST', '/api/users', {
            username: 'testuser2',
            email: 'invalid-email'
        });
        if (res.statusCode !== 400) throw new Error(`Expected 400, got ${res.statusCode}`);
    });

    await test('Create user with short username', async () => {
        const res = await httpRequest('POST', '/api/users', {
            username: 'ab',
            email: 'test2@example.com'
        });
        if (res.statusCode !== 400) throw new Error(`Expected 400, got ${res.statusCode}`);
    });

    await test('Get all users', async () => {
        const res = await httpRequest('GET', '/api/users');
        if (res.statusCode !== 200) throw new Error(`Expected 200, got ${res.statusCode}`);
        if (!Array.isArray(res.data)) throw new Error('Expected array');
    });

    await test('Get user by ID', async () => {
        const res = await httpRequest('GET', `/api/users?id=${createdUserId}`);
        if (res.statusCode !== 200) throw new Error(`Expected 200, got ${res.statusCode}`);
        if (res.data.username !== 'testuser') throw new Error('Username mismatch');
    });

    await test('Get non-existent user', async () => {
        const res = await httpRequest('GET', '/api/users?id=999999');
        if (res.statusCode !== 404) throw new Error(`Expected 404, got ${res.statusCode}`);
    });

    await test('Update user', async () => {
        const res = await httpRequest('PUT', `/api/users?id=${createdUserId}`, {
            username: 'updateduser',
            email: 'updated@example.com'
        });
        if (res.statusCode !== 200) throw new Error(`Expected 200, got ${res.statusCode}`);
        if (res.data.username !== 'updateduser') throw new Error('Username not updated');
    });

    await test('Delete user', async () => {
        const res = await httpRequest('DELETE', `/api/users?id=${createdUserId}`);
        if (res.statusCode !== 200) throw new Error(`Expected 200, got ${res.statusCode}`);
    });

    console.log('\n--- Task CRUD Tests ---');

    let createdTaskId;
    await test('Create task with valid data', async () => {
        const res = await httpRequest('POST', '/api/tasks', {
            title: 'Test Task',
            description: 'Test Description',
            priority: 'high'
        });
        if (res.statusCode !== 201) throw new Error(`Expected 201, got ${res.statusCode}`);
        if (!res.data.id) throw new Error('Task ID not returned');
        createdTaskId = res.data.id;
    });

    await test('Create task with invalid priority', async () => {
        const res = await httpRequest('POST', '/api/tasks', {
            title: 'Test Task 2',
            priority: 'invalid'
        });
        if (res.statusCode !== 400) throw new Error(`Expected 400, got ${res.statusCode}`);
    });

    await test('Create task without title', async () => {
        const res = await httpRequest('POST', '/api/tasks', {
            description: 'No title'
        });
        if (res.statusCode !== 400) throw new Error(`Expected 400, got ${res.statusCode}`);
    });

    await test('Get all tasks', async () => {
        const res = await httpRequest('GET', '/api/tasks');
        if (res.statusCode !== 200) throw new Error(`Expected 200, got ${res.statusCode}`);
        if (!Array.isArray(res.data)) throw new Error('Expected array');
    });

    await test('Get task by ID', async () => {
        const res = await httpRequest('GET', `/api/tasks?id=${createdTaskId}`);
        if (res.statusCode !== 200) throw new Error(`Expected 200, got ${res.statusCode}`);
        if (res.data.title !== 'Test Task') throw new Error('Title mismatch');
    });

    await test('Update task', async () => {
        const res = await httpRequest('PUT', `/api/tasks?id=${createdTaskId}`, {
            title: 'Updated Task',
            status: 'completed'
        });
        if (res.statusCode !== 200) throw new Error(`Expected 200, got ${res.statusCode}`);
        if (res.data.title !== 'Updated Task') throw new Error('Title not updated');
        if (res.data.status !== 'completed') throw new Error('Status not updated');
    });

    await test('Delete task', async () => {
        const res = await httpRequest('DELETE', `/api/tasks?id=${createdTaskId}`);
        if (res.statusCode !== 200) throw new Error(`Expected 200, got ${res.statusCode}`);
    });

    console.log('\n--- Route Tests ---');
    await test('Non-existent route returns 404', async () => {
        const res = await httpRequest('GET', '/api/nonexistent');
        if (res.statusCode !== 404) throw new Error(`Expected 404, got ${res.statusCode}`);
    });

    console.log('\n=== Test Summary ===');
    console.log(`Total: ${passed + failed}`);
    console.log(`Passed: ${passed}`);
    console.log(`Failed: ${failed}`);
    console.log(`Success Rate: ${((passed / (passed + failed)) * 100).toFixed(2)}%`);

    process.exit(failed > 0 ? 1 : 0);
}

runTests().catch(console.error);
