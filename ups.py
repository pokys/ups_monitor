import time
import subprocess
import paramiko

# UPS informace
UPS_IP = "172.16.4.22"
COMMUNITY_STRING = "public"  # SNMP Community String
BATTERY_MODE_OID = "1.3.6.1.4.1.3808.1.1.1.2.2.1.0"  # OID pro zjištění, zda UPS běží na baterii
BATTERY_STATUS_OID = "1.3.6.1.4.1.3808.1.1.1.2.2.2.0"  # OID pro zjištění stavu baterie

# Informace o serveru
SERVERS = [
    {"ip": "172.16.4.100", "username": "admin", "password": "password"},
    {"ip": "172.16.4.101", "username": "admin", "password": "password"}
]

def get_snmp_value(ip, oid):
    """Získá hodnotu z SNMP zařízení pomocí snmpwalk"""
    try:
        print(f"Získávání SNMP hodnoty pro OID: {oid} z IP: {ip}")
        result = subprocess.run(
            ["snmpwalk", "-v2c", "-c", COMMUNITY_STRING, ip, oid],
            capture_output=True, text=True, check=True
        )
        output = result.stdout.strip()
        print(f"SNMP výstup: {output}")

        # Extrahování hodnoty bez ohledu na typ
        if "INTEGER:" in output:
            return int(output.split("INTEGER:")[1].strip())
        elif "STRING:" in output:
            return output.split("STRING:")[1].strip().strip('"')
        elif "Gauge32:" in output:
            return int(output.split("Gauge32:")[1].strip())
        else:
            print(f"Neznámý formát SNMP výstupu: {output}")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Chyba při spuštění snmpwalk: {e}")
        return None

def shutdown_server(ip, username, password):
    """Připojí se k serveru přes SSH a vypne jej."""
    try:
        print(f"Vypínání serveru {ip}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)
        
        stdin, stdout, stderr = ssh.exec_command("sudo shutdown now")
        stdout.channel.recv_exit_status()  # čeká na dokončení příkazu
        
        print(f"Server {ip} byl úspěšně vypnut.")
        ssh.close()
    except Exception as e:
        print(f"Chyba při vypínání serveru {ip}: {e}")

def monitor_ups():
    """Hlavní funkce pro monitorování UPS a vypnutí serverů v případě potřeby."""
    while True:
        print("Kontrola stavu UPS...")
        # Kontrola UPS stavu
        battery_mode = get_snmp_value(UPS_IP, BATTERY_MODE_OID)
        battery_status = get_snmp_value(UPS_IP, BATTERY_STATUS_OID)
        
        print(f"Stav baterie: {battery_mode}, Úroveň nabití: {battery_status}")
        
        if battery_mode is None or battery_status is None:
            print("Nelze získat SNMP hodnoty, kontrola se opakuje.")
        else:
            # Akce se provede pouze, když UPS běží na baterii a úroveň nabití je pod 40 %
            if battery_mode == 1 and battery_status < 40:
                print("UPS běží na baterii a úroveň nabití je kritická (méně než 40%)!")
                
                # Provedeme vypnutí všech serverů
                for server in SERVERS:
                    shutdown_server(server["ip"], server["username"], server["password"])
                
                print("Všechny servery byly vypnuty, skript končí.")
                break
            else:
                print("UPS běží na síti nebo je úroveň nabití dostatečná.")

        # Opakování kontroly každou minutu
        time.sleep(60)

# Spustíme monitorování UPS
monitor_ups()
