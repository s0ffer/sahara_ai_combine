# Sahara AI Script:

### Functions:
### * Transaction of value to random wallet in `receivers.txt`

---

## Files, settings
### `settings.json` - 
            {
              "min_value": 0.00000000001,
              "max_value": 0.00000000002,
              "min_delay": 1,
              "max_delay": 5,
              "provider_url": "https://testnet.saharalabs.ai",
              "proxy": "",
              "flows": 10
            }

* You can set range for random value and delay before sending TX for each wallet. 
* `flows` - number of concurrent tasks to execute
* `proxy` - optional proxy in format `http://login:pass@ip:port`

### `private_keys.txt` - put your private keys here in rows
Example:
```
0xYourPrivateKey1
0xYourPrivateKey2
0xYourPrivateKey3
```

### `receivers.txt` - optionally you can put another addresses to wallets going to send TX. Theres is 100 generated wallet addresses already.


---

## Setup Instructions

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd <repository-folder>
```

### Step 2: Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Run the Script
```bash
python send_tx.py
```

---

## Requirements
- Python 3.12 or above
- Dependencies listed in `requirements.txt`

---

## Contributing
Feel free to fork this repository, create a new branch, and submit a pull request with your improvements or new features.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.