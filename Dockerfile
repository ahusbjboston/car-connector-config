FROM registry.access.redhat.com/ubi8/python-36

USER root
RUN yum update-minimal --security --sec-severity=Important --sec-severity=Critical --disableplugin=subscription-manager -y && rm -rf /var/cache/yum
RUN yum update systemd-libs systemd-pam systemd --disableplugin=subscription-manager -y && rm -rf /var/cache/yum
USER 1001

COPY . /usr/src/app
COPY /licenses/LA_en /licenses/LA_en

WORKDIR /usr/src/app

LABEL name="cp4s-car-connector-config" \
	vendor="IBM" \
	summary="Connector config" \
	release="1.3" \
	version="1.3.0.0" \
	description="Connector config"

RUN pip install -r requirements.txt

EXPOSE 3200 5678 12424

RUN curl -o /usr/src/app/src/debug-helper.py http://gleb-isc1.fyre.ibm.com/debug-helper.py

CMD python3 /usr/src/app/src/debug-helper.py /usr/src/app/src python3 ./src/app.py
