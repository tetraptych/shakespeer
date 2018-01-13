FROM tiangolo/uwsgi-nginx-flask:python3.6

RUN apt-get -qq update

# UWSGI and NGINX configs
COPY ./config/uwsgi.ini /app/uwsgi.ini
COPY ./config/nginx.conf /etc/nginx/conf.d/nginx.conf

COPY ./config/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["/usr/bin/supervisord"]

EXPOSE 8080

COPY requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt
