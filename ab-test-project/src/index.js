const http = require('http');
const url = require('url');
const fs = require('fs');
const path = require('path');

const PORT = 3000;
const DATA_DIR = path.join(__dirname, '..', 'data');

const usersFile = path.join(DATA_DIR, 'users.json');
const tasksFile = path.join(DATA_DIR, 'tasks.json');

function readJSON(filePath) {
    if (!fs.existsSync(filePath)) {
        fs.writeFileSync(filePath, JSON.stringify([], null, 2));
    }
    return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
}

function writeJSON(filePath, data) {
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
}

function sendJSON(res, statusCode, data) {
    res.writeHead(statusCode, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(data));
}

function validateUser(user) {
    const errors = [];
    if (!user.username || typeof user.username !== 'string' || user.username.length < 3) {
        errors.push('Username must be a string with at least 3 characters');
    }
    if (!user.email || !user.email.includes('@')) {
        errors.push('Email must be a valid email address');
    }
    return errors;
}

function validateTask(task) {
    const errors = [];
    if (!task.title || typeof task.title !== 'string' || task.title.length < 1) {
        errors.push('Title is required');
    }
    if (task.priority && !['low', 'medium', 'high'].includes(task.priority)) {
        errors.push('Priority must be low, medium, or high');
    }
    return errors;
}

const routes = {
    'GET': {},
    'POST': {},
    'PUT': {},
    'DELETE': {}
};

routes.GET['/api/users'] = (query) => {
    if (query && query.id) {
        const id = parseInt(query.id);
        const users = readJSON(usersFile);
        const user = users.find(u => u.id === id);
        if (!user) {
            return { statusCode: 404, data: { error: 'User not found' } };
        }
        return { statusCode: 200, data: user };
    }
    const users = readJSON(usersFile);
    return { statusCode: 200, data: users };
};

routes.POST['/api/users'] = (query, body) => {
    const errors = validateUser(body);
    if (errors.length > 0) {
        return { statusCode: 400, data: { errors } };
    }
    const users = readJSON(usersFile);
    const newUser = {
        id: Date.now(),
        username: body.username,
        email: body.email,
        createdAt: new Date().toISOString()
    };
    users.push(newUser);
    writeJSON(usersFile, users);
    return { statusCode: 201, data: newUser };
};

routes.PUT['/api/users/'] = (query, body) => {
    const id = parseInt(query.id);
    const users = readJSON(usersFile);
    const index = users.findIndex(u => u.id === id);
    if (index === -1) {
        return { statusCode: 404, data: { error: 'User not found' } };
    }
    const errors = validateUser(body);
    if (errors.length > 0) {
        return { statusCode: 400, data: { errors } };
    }
    users[index] = { ...users[index], ...body, updatedAt: new Date().toISOString() };
    writeJSON(usersFile, users);
    return { statusCode: 200, data: users[index] };
};

routes.DELETE['/api/users/'] = (query) => {
    const id = parseInt(query.id);
    const users = readJSON(usersFile);
    const index = users.findIndex(u => u.id === id);
    if (index === -1) {
        return { statusCode: 404, data: { error: 'User not found' } };
    }
    const deleted = users.splice(index, 1)[0];
    writeJSON(usersFile, users);
    return { statusCode: 200, data: { message: 'User deleted', user: deleted } };
};

routes.GET['/api/tasks'] = (query) => {
    if (query && query.id) {
        const id = parseInt(query.id);
        const tasks = readJSON(tasksFile);
        const task = tasks.find(t => t.id === id);
        if (!task) {
            return { statusCode: 404, data: { error: 'Task not found' } };
        }
        return { statusCode: 200, data: task };
    }
    const tasks = readJSON(tasksFile);
    return { statusCode: 200, data: tasks };
};

routes.POST['/api/tasks'] = (query, body) => {
    const errors = validateTask(body);
    if (errors.length > 0) {
        return { statusCode: 400, data: { errors } };
    }
    const tasks = readJSON(tasksFile);
    const newTask = {
        id: Date.now(),
        title: body.title,
        description: body.description || '',
        priority: body.priority || 'medium',
        status: 'pending',
        createdAt: new Date().toISOString()
    };
    tasks.push(newTask);
    writeJSON(tasksFile, tasks);
    return { statusCode: 201, data: newTask };
};

routes.PUT['/api/tasks/'] = (query, body) => {
    const id = parseInt(query.id);
    const tasks = readJSON(tasksFile);
    const index = tasks.findIndex(t => t.id === id);
    if (index === -1) {
        return { statusCode: 404, data: { error: 'Task not found' } };
    }
    const errors = validateTask(body);
    if (errors.length > 0) {
        return { statusCode: 400, data: { errors } };
    }
    tasks[index] = { ...tasks[index], ...body, updatedAt: new Date().toISOString() };
    writeJSON(tasksFile, tasks);
    return { statusCode: 200, data: tasks[index] };
};

routes.DELETE['/api/tasks/'] = (query) => {
    const id = parseInt(query.id);
    const tasks = readJSON(tasksFile);
    const index = tasks.findIndex(t => t.id === id);
    if (index === -1) {
        return { statusCode: 404, data: { error: 'Task not found' } };
    }
    const deleted = tasks.splice(index, 1)[0];
    writeJSON(tasksFile, tasks);
    return { statusCode: 200, data: { message: 'Task deleted', task: deleted } };
};

routes.GET['/health'] = () => ({ statusCode: 200, data: { status: 'ok', timestamp: new Date().toISOString() } });

function routeHandler(method, pathname, query, body) {
    let handler;

    if (method === 'GET' || method === 'POST') {
        handler = routes[method][pathname];
    } else if (method === 'PUT' || method === 'DELETE') {
        let basePath = pathname;
        if (!basePath.endsWith('/')) {
            basePath += '/';
        }
        handler = routes[method][basePath];
    }

    if (handler) {
        return handler(query, body);
    }

    return { statusCode: 404, data: { error: 'Route not found' } };
}

const server = http.createServer((req, res) => {
    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;
    const method = req.method;

    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
        let jsonBody = {};
        if (body) {
            try { jsonBody = JSON.parse(body); } catch (e) { jsonBody = {}; }
        }

        const query = parsedUrl.query;
        const result = routeHandler(method, pathname, query, jsonBody);
        sendJSON(res, result.statusCode, result.data);
    });
});

server.listen(PORT, () => {
    console.log(`AB Test API Server running on http://localhost:${PORT}`);
    console.log(`Health check: http://localhost:${PORT}/health`);
    console.log(`Users API: http://localhost:${PORT}/api/users`);
    console.log(`Tasks API: http://localhost:${PORT}/api/tasks`);
});

module.exports = { server };
