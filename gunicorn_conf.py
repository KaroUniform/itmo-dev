from os import environ

loglevel = "info"
errorlog = "-"  # stderr
accesslog = "-"  # stdout
graceful_timeout = 120
timeout = 120
threads = 4
bind = "0.0.0.0:" + environ.get("PORT", "8000")
max_requests = 5000
certfile = "/ssl/karouniform.xyz.cer"
keyfile = "/ssl/karouniform.xyz.key"
