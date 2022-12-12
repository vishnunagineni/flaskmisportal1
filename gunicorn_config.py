"""corn WSGI server configiuration."""
from multiprocessing import cpu_count


def max_workers():    
    return cpu_count()*2 + 1

#bind =  'unix:myproject.sock'
umask = 0o007
bind = '0.0.0.0:4004'
max_requests = 1000
worker_class = 'gevent'
workers = max_workers()
reload=True
