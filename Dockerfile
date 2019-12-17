FROM chaberb/flask-rest
ADD . /var/www/app
#WORKDIR /var/www/app
RUN pip install -r /var/www/app/requirements.txt
# CMD ["python", "app.py"]
