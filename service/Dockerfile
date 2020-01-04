# FROM chaberb/flask-rest
# ADD . /var/www/app

# RUN pip install -r /var/www/app/requirements.txt
# # CMD ["python", "app.py"]
# #WORKDIR /var/www/app
FROM python:3.4-alpine
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
