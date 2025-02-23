FROM odoo:17

WORKDIR /app
COPY ./supplies/requirements.txt /app/requirements.txt
COPY ./enterprise /mnt/odoo_17.0+e.latest

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

CMD ["odoo"]