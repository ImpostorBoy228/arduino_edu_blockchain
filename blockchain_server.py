from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO
import hashlib
import time
import json
from threading import Lock

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
lock = Lock()

class Block:
    def __init__(self, index, prev_hash, data, difficulty, nonce=0):
        self.index = index
        self.prev_hash = prev_hash
        self.data = data
        self.timestamp = time.time()
        self.difficulty = difficulty
        self.nonce = nonce

    @property
    def hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True).encode()
        return hashlib.sha1(block_string).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 1
        self.fake_price = 0.01

    def create_genesis_block(self):
        return Block(0, "0", "Genesis Block", 1)

    @property
    def last_block(self):
        return self.chain[-1]

    def update_price(self):
        self.fake_price *= 1 + (0.05 - 0.1 * (time.time() % 2))
        return round(self.fake_price, 4)

blockchain = Blockchain()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify([b.__dict__ for b in blockchain.chain]), 200

@app.route('/mine', methods=['GET'])
def get_mining_job():
    with lock:
        return jsonify({
            "index": len(blockchain.chain),
            "prev_hash": blockchain.last_block.hash,
            "difficulty": blockchain.difficulty
        }), 200

@app.route('/submit', methods=['POST'])
def submit_block():
    with lock:
        try:
            data = request.get_json()
            print(f"Получено решение: {data}")
            
            # Проверка наличия всех полей
            required_fields = ["index", "prev_hash", "difficulty", "nonce", "data", "timestamp"]
            if not all(field in data for field in required_fields):
                print("Отсутствуют обязательные поля")
                return jsonify({"status": "rejected", "reason": "Missing fields"}), 400
            
            # Проверка корректности индекса
            if data['index'] != len(blockchain.chain):
                print(f"Неверный индекс: ожидалось {len(blockchain.chain)}, получено {data['index']}")
                return jsonify({"status": "rejected", "reason": "Invalid block index"}), 400
            
            # Проверка предыдущего хеша
            if data['prev_hash'] != blockchain.last_block.hash:
                print(f"Неверный предыдущий хеш: ожидалось {blockchain.last_block.hash}, получено {data['prev_hash']}")
                return jsonify({"status": "rejected", "reason": "Previous hash mismatch"}), 400
            
            # Создание нового блока
            new_block = Block(
                data['index'],
                data['prev_hash'],
                data['data'],
                data['difficulty'],
                data['nonce']
            )
            new_block.timestamp = data['timestamp']  # Используем timestamp от майнера
            
            # Проверка хеша
            target = '0' * blockchain.difficulty
            if new_block.hash.startswith(target):
                blockchain.chain.append(new_block)
                if len(blockchain.chain) % 5 == 0:
                    blockchain.difficulty += 1
                
                # Отправка обновления через WebSocket
                socketio.emit('update', {
                    'type': 'block',
                    'data': [{
                        "index": new_block.index,
                        "hash": new_block.hash[:15] + "...",
                        "difficulty": new_block.difficulty
                    }]
                })
                
                # Обновление "цены"
                socketio.emit('update', {
                    'type': 'price',
                    'data': blockchain.update_price()
                })
                
                print(f"Блок принят: {new_block.hash}")
                return jsonify({"status": "accepted", "hash": new_block.hash}), 200
            else:
                print(f"Неверный хеш: {new_block.hash} не начинается с {target}")
                return jsonify({"status": "rejected", "reason": "Invalid proof-of-work"}), 400
                
        except Exception as e:
            print(f"Ошибка при обработке решения: {str(e)}")
            return jsonify({"status": "error", "reason": str(e)}), 500
@socketio.on('connect')
def handle_connect():
    socketio.emit('init', {
        "chain": [{
            "index": block.index,
            "hash": block.hash[:15] + "...",
            "difficulty": block.difficulty
        } for block in blockchain.chain[-5:]],
        "price": blockchain.fake_price
    })

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)