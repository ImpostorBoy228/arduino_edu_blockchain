import requests
import hashlib
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

        if nonce % 1000 == 0:
            print(f"Проверка новых заданий...")
            try:
                new_job = requests.get(f"{SERVER_URL}/mine").json()
                if new_job['prev_hash'] != job['prev_hash']:
                    return mine_block()
            except:
                pass

if __name__ == "__main__":
    while True:
        result = mine_block()
        if result:
            print(f"Результат: {result}")
        else:
            print("Майнинг прерван. Повтор через 5 секунд...")
            time.sleep(5)