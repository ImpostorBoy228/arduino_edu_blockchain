# Arduino Blockchain Miner

The project is a fucking incomplete system for mining blocks using Arduino and a Flask server. The Arduino performs the work of calculating hashes, and the Flask server processes the jobs and accepts decisions from the miner.

## Description

The project includes three main components:

1. **Arduino-miner** is an Arduino-based device that performs block hashing.
2. **Flask-server** is a server for managing the blockchain and processing decisions from miners.
3. **Python scripts** are a client that interacts with the server and manages the submission of tasks and the receipt of solutions.

### Components:

1. **Arduino (miner)** - uses SHA-1 to calculate hashes and solves Proof-of-Work problems.
2. **Flask server** - manages the blockchain, checks solutions, and sends mining tasks.
3. **Python clients** - receive tasks from the server and send solutions using the Proof-of-Work algorithm.

## Requirements

- **Arduino Uno** or compatible board
- **Arduino IDE**
- **Flask** and **Flask-SocketIO** for the server part
- **Python** for working with the client
- **Libraries**:
    - `pyserial`
    - `requests`
    - `hashlib`
    - `time`
    - `json`

## Installation

1. Download or clone the repository.

```bash
git clone https://github.com/your-username/arduino-blockchain-miner.git
```

2. Upload the code to your Arduino using the Arduino IDE.
    - Connect your Arduino to your computer.
    - Open the project in the Arduino IDE and upload the code to your device.
    - Make sure that the correct port is selected.

3. Install the dependencies for the server side:

```bash
pip install flask flask-socketio requests
```

4. Start the Flask server:

```bash
python server.py
```

5. Start the Python script for the client:

```bash
python arduino_client.py
```

6. After that, the Arduino will start mining, and the server will process the results.

## How it works

1. **Arduino** requests tasks from the server (block parameters, difficulty).
2. **Arduino** performs calculations (hash generation) and tries to find a suitable nonce.
3. After finding a suitable nonce, **Arduino** sends the solution to the server.
4. **Flask-server** checks the solution (hash verification) and, if it is correct, adds the new block to the chain.

## Interaction with the server

- **GET /mine** - request to get a mining job.
- **POST /submit** - sending a solution from the miner.
- **GET /chain** - getting the current block chain.

## Client example

The Python client will mine blocks by requesting tasks from the server and sending the found solutions:

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
        print(f"Received job: {job}")
    except requests.exceptions.RequestException as e:
        print(f"Error while receiving the job: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {response.text}")
        return None

    target = '0' * job['difficulty']
    nonce = 0
    print(f"Starting mining. Target: {target}")

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
            print(f"Found nonce: {nonce}, hash: {hash_result[:16]}...")
            try:
                solution = {
                    "index": job['index'],
                    "prev_hash": job['prev_hash'],
                    "difficulty": job['difficulty'],
                    "nonce": nonce,
                    "data": "Mined Block",
                    "timestamp": int(time.time())
                }
                print(f"Sending a solution: {solution}")
response = requests.post(
                    f"{SERVER_URL}/submit",
                    json=solution,
                    timeout=5
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error when sending: {str(e)}")
print(f"Server response: {response.text}")
return None

        nonce += 1

if __name__ == "__main__":
    while True:
        result = mine_block()
        if result:
            print(f"Result: {result}")
        else:
            print("Mining interrupted. Retry in 5 seconds...")
            time.sleep(5)
```

## License

This project is distributed under the MIT license. See [LICENSE](LICENSE) for details.
```
