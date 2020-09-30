FROM python:3.6

RUN pip install scipy pandas pandas-datareader
RUN mkdir /app
COPY app/* /app/
RUN chmod +x /app/docker-entrypoint.sh
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD python /app/weights.py