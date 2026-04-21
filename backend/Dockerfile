FROM  python:3.12.3-slim
COPY ./app /root/inspector
WORKDIR /root/inspector
COPY ./requirements.txt /root/requirements.txt
RUN  pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && pip install --no-cache-dir --upgrade -r /root/requirements.txt
# CMD ["/usr/local/bin/gunicorn", "-c", "gunicorn.conf.py", "app:app"]
CMD ["python", "-u", "app.py"]
