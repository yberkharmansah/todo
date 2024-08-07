import pyodbc
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# SQL Server bağlantısı için gerekli bilgileri buraya ekleyin
server = 'BERK'
database = 'users'
driver = 'ODBC Driver 17 for SQL Server'

conn = pyodbc.connect('DRIVER={SQL Server};SERVER=BERK;DATABASE=users;Trusted_Connection=yes;')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    print(f"Kullanıcı adı: {username}, Şifre: {password}")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM UserCredentials WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()

    if user:
        user_id = user[0]
        return jsonify({'message': 'Login successful','user_id': user_id})
    else:
        return jsonify({'message': 'Invalid username or password'}), 401
@app.route('/todo/user/<int:user_id>', methods=['GET'])
def get_todos_with_subtasks(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Todos WHERE user_id = ?", (user_id,))
    todos = cursor.fetchall()

    todos_list = []
    for todo in todos:
        print(todo[1])
        todo_id = todo[0]
        cursor.execute("SELECT * FROM Subtasks WHERE todo_id = ?", (todo_id,))
        subtasks = cursor.fetchall()

        subtasks_list = [{'subtask_id': row[0], 'title': row[1],'completed':row[2]} for row in subtasks]

        todos_list.append({
            'todo_id': todo_id,
            'title': todo[1],
            'subtasks': subtasks_list
        })
    return jsonify({'todos': todos_list})
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM UserCredentials WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if user:
        user_data = {
            'user_id': user[0],
            'username': user[1],
            # Diğer kullanıcı bilgileri buraya eklenmeli
        }
        return jsonify(user_data)
    else:
        return jsonify({'message': 'User not found'}), 404
@app.route('/add-todo/<int:user_id>', methods=['POST'])
def add_todo(user_id):
    data = request.get_json()
    title = data.get('title')

    if not title:
        return jsonify({'message': 'Başlık eksik'}), 400

    cursor = conn.cursor()
    cursor.execute("INSERT INTO Todos (user_id, title) VALUES (?, ?)", (user_id, title))
    conn.commit()

    return jsonify({'message': 'Todo added successfully'}), 201
@app.route('/add-subtask/<int:todo_id>', methods=['POST'])
def add_subtask(todo_id):
    data = request.get_json()
    title = data['title']
    completed = data['completed']

    cursor = conn.cursor()
    cursor.execute("INSERT INTO Subtasks (todo_id, title, completed) VALUES (?, ?, ?)", (todo_id, title, completed))
    conn.commit()

    return jsonify({'message': 'Subtask added successfully'})
@app.route('/delete-todo/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Todos WHERE todo_id = ?", (todo_id,))
    conn.commit()
    return jsonify({'message': 'Todo deleted successfully'})

@app.route('/delete-subtask/<int:subtask_id>', methods=['DELETE'])
def delete_subtask(subtask_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Subtasks WHERE subtask_id = ?", (subtask_id,))
    conn.commit()
    return jsonify({'message': 'Subtask deleted successfully'})
@app.route('/update-subtask-completion/<int:subtask_id>', methods=['PUT'])
def update_subtask_completion(subtask_id):
    data = request.get_json()
    completed = data.get('completed')

    cursor = conn.cursor()
    cursor.execute("UPDATE Subtasks SET completed = ? WHERE subtask_id = ?", (completed, subtask_id))
    conn.commit()

    return jsonify({'message': 'Subtask completion updated successfully'})
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM UserCredentials WHERE username = ?", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        return jsonify({'message': 'Username already exists'}), 409

    cursor.execute("INSERT INTO UserCredentials (username, password) VALUES (?, ?)", (username, password))
    conn.commit()

    return jsonify({'message': 'Registration successful'}), 201

if __name__ == '__main__':
    app.run(debug=True)
