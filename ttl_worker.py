import time
import threading
from datetime import datetime

def _worker_loop(db_module):
    """
    The background loop that runs indefinitely, checking for expired holds.
    """
    while True:
        try:
            count = db_module.release_expired_holds()
            now_str = datetime.now().strftime("%H:%M:%S")
            print(f"[TTL WORKER] Checked at {now_str} - Released {count} stale holds")
        except Exception as e:
            print(f"[TTL WORKER] Error in worker loop: {e}")
        time.sleep(10)

def start_ttl_worker(db_module):
    """
    Starts the TTL worker in a background daemon thread.
    """
    print("Starting TTL background worker...")
    thread = threading.Thread(target=_worker_loop, args=(db_module,), daemon=True)
    thread.start()
