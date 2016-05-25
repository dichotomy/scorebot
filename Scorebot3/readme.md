Scorebot3.02 Alpha Code

There may be bugs. 

Requirments:
 - MySQL or Postgres
  - MySQL must use PyMSQL (pip install PyMYSQL)
 - Python 3.5 (no 2.X BS)
 - PIP
 - Django (pip install django)
 - Django IPWare (pip install django-ipware)
 - Django Pickledfield (pip install django-pickledfield)
 - Apache2
 - Mod Wsgi for Apache
 - Python Virtual-Env

How to install:
 - Install Python, PIP, Apache, WSGI and Python Env
  - for Arch Linux: pacman -S apache2 python3 python3-pip python-virtenv mod_wsgi
 - Create python virtual enviroment 
  - virtualenv "path"
 - Source the VirtualEnv
  - source "path"/bin/activate
 - Use PIP to install django, pickledfield, ipware and pymysql 
  - pip install django django-pickledfield django-ipware pymysql
 - Copy the SBE python files to a directory with the VirtualEnv
 - Modify the Apache Config below to suit your needs and add it to your Apache Config
 - Install and Configure your DB of choosing
 - Build the DB
  - python manage.py makemigrations && python manage.py migrate
 - Add admin account
  - python manage.py createsuperuser
 - Start Apache

TODO: Create a script for this.

[Apache Config]
<VirtualHost *:80>
    Alias /static /scorebot/v3.02/static
    <Directory /scorebot/v3.02/static>
	Require all granted
    </Directory>
    <Directory /scorebot/v3.02>
	<Files wsgi.py>
	    Require all granted
	</Files>
    </Directory>
    WSGIDaemonProcess scorebotv3 python-path=/scorebot/v3.02:/scorebot/pyvirt/lib/python3.5/site-packages
    WSGIProcessGroup scorebotv3
    WSGIScriptAlias / /scorebot/v3.02/scorebot/wsgi.py
</VirtualHost>
[/Apache Config]
