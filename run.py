import webview
import threading
from invoice_app import app

def run_flask():
    app.run(debug=False)
    
t = threading.Thread(target=run_flask)
t.daemon = True
t.start()

import time
time.sleep(1)

webview.create_window(
    "Invoice Manager",
    "http://127.0.0.1:5000",
    width=800,
    height=600
)
webview.start()