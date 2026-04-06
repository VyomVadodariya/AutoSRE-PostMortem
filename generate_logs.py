import os
import random
from datetime import datetime, timedelta

# Strict deterministic setup
random.seed(42)
WORKSPACE = "./sre_workspace"

# DDoS IPs for the Hard Task
DDOS_IPS = ["192.168.1.100", "192.168.1.101", "192.168.1.102"]

def setup_workspace():
    # 1. Create directory structure
    dirs = ["logs", "services", "config"]
    for d in dirs:
        os.makedirs(os.path.join(WORKSPACE, d), exist_ok=True)
    
    # 2. Generate access.log (Task 1 & Task 3 Data)
    log_path = os.path.join(WORKSPACE, "logs", "access.log")
    start_time = datetime.now() - timedelta(hours=24)
    
    with open(log_path, "w") as f:
        for i in range(10000):
            current_time = start_time + timedelta(seconds=i*8)
            time_str = current_time.strftime("%d/%b/%Y:%H:%M:%S +0000")
            
            # Inject Task 3 (DDoS)
            if random.random() < 0.05:  
                bad_ip = random.choice(DDOS_IPS)
                f.write(f'{bad_ip} - - [{time_str}] "POST /api/v1/checkout HTTP/1.1" 429 0 "-" "BotAgent/1.0"\n')
            # Inject Task 1 (Config Bug)
            elif random.random() < 0.01:
                f.write(f'10.0.0.5 - - [{time_str}] "GET /api/v1/health HTTP/1.1" 502 154 "-" "ELB-HealthChecker/2.0"\n')
            # Normal Traffic
            else:
                good_ip = f"203.0.113.{random.randint(1, 255)}"
                f.write(f'{good_ip} - - [{time_str}] "GET / HTTP/1.1" 200 1024 "-" "Mozilla/5.0"\n')

    # 3. Create Task 1 Target
    yaml_content = """version: '3.8'\nservices:\n  web:\n    image: nginx:latest\n    ports:\n      - "8080:80"\n"""
    with open(os.path.join(WORKSPACE, "config", "docker-compose.yml"), "w") as f:
        f.write(yaml_content)

    # 4. Create Task 2 Target
    payment_code = """def process_payment(amount):\n    status = "pending"\n    while status == "pending":\n        print(f"Processing ${amount}...")\n    return True\n"""
    with open(os.path.join(WORKSPACE, "services", "payment_service.py"), "w") as f:
        f.write(payment_code)

    # 5. Create Task 2 Grader Test
    test_code = """import payment_service\nprint("Starting test...")\npayment_service.process_payment(50)\nprint("Test passed!")\n"""
    with open(os.path.join(WORKSPACE, "services", "test_payment.py"), "w") as f:
        f.write(test_code)

    # 6. Create Task 3 Target
    db_yaml = """database:\n  host: "db.internal"\n  user: "admin"\n  password: "" \n"""
    with open(os.path.join(WORKSPACE, "config", "database.yml"), "w") as f:
        f.write(db_yaml)

if __name__ == "__main__":
    setup_workspace()