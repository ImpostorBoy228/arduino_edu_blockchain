
# Arduino Blockchain Miner

Проект представляет собой систему для майнинга блоков с использованием Arduino и сервера на Flask. Arduino выполняет работу по вычислению хешей, а сервер на Flask обрабатывает задания и принимает решения от майнера.

## Описание

Проект включает три основных компонента:

1. **Arduino-майнер** — устройство на базе Arduino, которое выполняет хеширование блоков.
2. **Flask-сервер** — сервер для управления блокчейном и обработки решений от майнеров.
3. **Python-скрипты** — клиент, который взаимодействует с сервером и управляет отправкой заданий и получением решений.

### Компоненты:

1. **Arduino (майнер)** - использует SHA-1 для вычисления хешей и решает задачи по Proof-of-Work.
2. **Flask сервер** - управляет цепочкой блоков, проверяет решения и отправляет задания на майнинг.
3. **Python клиенты** - получают задания от сервера и отправляют решения, используя алгоритм Proof-of-Work.

## Требования

- **Arduino Uno** или совместимая плата
- **Arduino IDE**
- **Flask** и **Flask-SocketIO** для серверной части
- **Python** для работы с клиентом
- **Библиотеки**:
    - `pyserial`
    - `requests`
    - `hashlib`
    - `time`
    - `json`

## Установка

1. Скачайте или клонируйте репозиторий.

```bash
git clone https://github.com/your-username/arduino-blockchain-miner.git
```

2. Загрузите код на вашу Arduino с помощью Arduino IDE.
    - Подключите Arduino к компьютеру.
    - Откройте проект в Arduino IDE и загрузите код на устройство.
    - Убедитесь, что выбран правильный порт.

3. Установите зависимости для серверной части:

```bash
pip install flask flask-socketio requests
```

4. Запустите Flask-сервер:

```bash
python server.py
```

5. Запустите Python-скрипт для клиента:

```bash
python arduino_client.py
```

6. После этого Arduino начнёт выполнять майнинг, а сервер будет обрабатывать результаты.

## Как это работает

1. **Arduino** запрашивает задания от сервера (параметры блока, сложность).
2. **Arduino** выполняет вычисления (генерация хешей) и пытается найти подходящий nonce.
3. После нахождения подходящего nonce, **Arduino** отправляет решение на сервер.
4. **Flask-сервер** проверяет решение (проверка хеша) и, если оно верно, добавляет новый блок в цепочку.

## Взаимодействие с сервером

- **GET /mine** — запрос для получения задания на майнинг.
- **POST /submit** — отправка решения от майнера.
- **GET /chain** — получение текущей цепочки блоков.

## Пример работы клиента

Клиент на Python будет выполнять майнинг блоков, запросив задания с сервера и отправляя найденные решения:

```python
import requests
import json
import time

SERVER_URL = "http://localhost:5000"

def mine_block():
    try:
        response = requests.get(f"{SERVER_URL}/mine", timeout=5)
        response.raise_for_status()
        job = response.json()
        print(f"Получено задание: {job}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении задания: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print(f"Ошибка декодирования JSON: {response.text}")
        return None

    target = '0' * job['difficulty']
    nonce = 0
    print(f"Начало майнинга. Цель: {target}")

    while True:
        input_data = json.dumps({
            "index": job['index'],
            "prev_hash": job['prev_hash'],
            "data": "Mined Block",
            "timestamp": int(time.time()),
            "difficulty": job['difficulty'],
            "nonce": nonce
        }, sort_keys=True).encode()

        hash_result = hashlib.sha1(input_data).hexdigest()

        if hash_result.startswith(target):
            print(f"Найден nonce: {nonce}, хеш: {hash_result[:16]}...")
            try:
                solution = {
                    "index": job['index'],
                    "prev_hash": job['prev_hash'],
                    "difficulty": job['difficulty'],
                    "nonce": nonce,
                    "data": "Mined Block",
                    "timestamp": int(time.time())
                }
                print(f"Отправляем решение: {solution}")
                response = requests.post(
                    f"{SERVER_URL}/submit",
                    json=solution,
                    timeout=5
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"Ошибка при отправке: {str(e)}")
                print(f"Ответ сервера: {response.text}")
                return None

        nonce += 1

if __name__ == "__main__":
    while True:
        result = mine_block()
        if result:
            print(f"Результат: {result}")
        else:
            print("Майнинг прерван. Повтор через 5 секунд...")
            time.sleep(5)
```

## Лицензия

Этот проект распространяется под лицензией MIT. См. [LICENSE](LICENSE) для подробностей.
```

Этот файл `README.md` предоставит чёткие инструкции для установки и запуска вашего проекта.
