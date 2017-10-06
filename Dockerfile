# use full image for build (compile) dependencies
FROM python:3 as build

COPY requirements*.txt /
RUN pip install -r requirements.txt
RUN pip install -r requirements.deploy.txt

COPY . /source/
RUN virtualenv /pyenv
RUN /pyenv/bin/pip install /source/

# switch to lightweight base image for distribution
FROM python:3-slim
COPY --from=build /pyenv /pyenv
RUN ln -s /pyenv/bin/failmap-admin /usr/local/bin/

WORKDIR /

# configuration for django-uwsgi to work correct in Docker environment
ENV UWSGI_GID root
ENV UWSGI_UID root
ENV UWSGI_MODULE failmap_admin.wsgi
ENV UWSGI_STATIC_MAP /static=/srv/failmap_admin/static

RUN /pyenv/bin/failmap-admin collectstatic

ENTRYPOINT [ "/usr/local/bin/failmap-admin" ]

CMD [ "help" ]
