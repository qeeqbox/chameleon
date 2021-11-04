FROM docker.io/grafana/grafana:7.5.7
COPY ./postgres.yml /etc/grafana/provisioning/datasources/postgres.yml
COPY ./dashboards.yml /etc/grafana/provisioning/dashboards/dashboards.yml
COPY ./chameleon.json /var/lib/grafana/dashboards/chameleon.json