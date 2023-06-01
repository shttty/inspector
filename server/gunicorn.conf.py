import multiprocessing

bind = '0.0.0.0:5000'

worker_class = "gevent"
daemon = False
debug = True
proc_name = 'gunicorn'
pidfile = './log/gunicorn.pid'
errorlog = './log/gunicorn.log'
