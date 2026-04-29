from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = 'todo.db'

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/todos', methods=['GET'])
def get_todos():
    conn = get_db()
    cursor = conn.execute('SELECT * FROM todos ORDER BY created_at DESC')
    todos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(todos)

@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'Text is required'}), 400

    conn = get_db()
    cursor = conn.execute('INSERT INTO todos (text) VALUES (?)', (text,))
    todo_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({'id': todo_id, 'text': text, 'completed': 0}), 201

@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()

    conn = get_db()
    if 'completed' in data:
        conn.execute('UPDATE todos SET completed = ? WHERE id = ?', (data['completed'], todo_id))
    if 'text' in data:
        conn.execute('UPDATE todos SET text = ? WHERE id = ?', (data['text'], todo_id))
    conn.commit()
    conn.close()

    return jsonify({'id': todo_id, 'updated': True})

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    conn = get_db()
    conn.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    conn.commit()
    conn.close()
    return jsonify({'id': todo_id, 'deleted': True})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)