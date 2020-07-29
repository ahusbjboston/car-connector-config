
FROM registry.access.redhat.com/ubi8/ubi-minimal as base
USER root
RUN  microdnf install python3-devel nginx 

FROM base as builder
USER root
RUN  microdnf install python3-pip gcc
COPY requirements.txt requirements.txt
RUN  pip3 install -r requirements.txt --no-cache-dir 


FROM base
ARG TMP_USER_ID=1001
ARG TMP_USER_GROUP=1001

USER root
RUN microdnf update -y && \
    rm -rf /var/cache/yum && \
    microdnf clean all 

COPY . /usr/src/app
RUN chown -R ${TMP_USER_ID}:${TMP_USER_GROUP} /etc/nginx/ && \
    chown -R ${TMP_USER_ID}:${TMP_USER_GROUP} /var/log/nginx && \
    chown -R ${TMP_USER_ID}:${TMP_USER_GROUP} /etc/nginx/conf.d && \
    chown -R ${TMP_USER_ID}:${TMP_USER_GROUP} /tmp/ && \
    chown -R ${TMP_USER_ID}:${TMP_USER_GROUP} /usr/src/app 
RUN touch /var/run/nginx.pid && \
    chown -R ${TMP_USER_ID}:${TMP_USER_GROUP} /var/run/nginx.pid
COPY --from=builder /usr/local/lib64/python3.6/site-packages /usr/local/lib64/python3.6/site-packages
COPY --from=builder /usr/local/lib/python3.6/site-packages /usr/local/lib/python3.6/site-packages
COPY --from=builder /usr/lib64/python3.6/site-packages /usr/lib64/python3.6/site-packages
COPY --from=builder /usr/lib/python3.6/site-packages /usr/lib/python3.6/site-packages
COPY --from=builder /usr/local/bin/uwsgi /usr/local/bin/uwsgi

USER ${TMP_USER_ID}

COPY /licenses/LA_en /licenses/LA_en
COPY  ./nginx.conf /etc/nginx/nginx.conf

WORKDIR /usr/src/app

LABEL name="cp4s-car-connector-config" \
	vendor="IBM" \
	summary="Connector config" \
	release="1.3" \
	version="1.3.0.0" \
	description="Connector config"

ENV FLASK_ENV production

EXPOSE 3200

CMD   uwsgi ./app.ini && \
      sed -i -e 's/$WORKDIR/\/usr\/src\/app/g' /etc/nginx/nginx.conf && \
      nginx -g 'daemon off;'
