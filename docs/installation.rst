Installation
============

.. note :: **The easiest way to install scorebot is to run the included setup/scorebot-setup.sh script, otherwise, continue with the steps below.**
|

.. note :: **YOU MUST be ROOT to complete most of the following steps**

**1. First, you should ensure your distribution is up to date**
   apt-get update && apt-get upgrade -y
|

**2. Next, we need to ensure we have all the required packages**
   apt-get install -y python-dnspython python-rrdtool apache2 php5 php5-mysql pyhton-pymongo python-dns python mysqldb git mongodb mysql-server mysql-client pip2
|

**3. Some required packages need to be downloaded via pip**
   .. note :: If your unfamiluar with PIP, you can see documentation at https://pypi.python.org/pypi/pip
   pip install jaraco.modb bottle paste requests backports.functools_lru_cache
|

**4. At this point, lets go ahead and get the latest scorebot from github**
   git clone https://github.com/dichotomy/scorebot.git
|

**5. Now we need get our Ticketing Interface website, which is a seperate project**
   .. warning :: This server should not be open to the internet, as this is a CTF, and some files may be intentially vulnerable.
   Head over to <http://sourceforge.net/projects/phpticketsystem/>  and download the BETA_1.zip.
   Extract the files to \\var\\www\\html\\
|

**6. Add the ticket database named sts to mysql and a scorebot user.**
  | mysql -uroot -p<mysql root user password> --execute="CREATE DATABASE sts; GRANT ALL ON sts.* TO scorebot@localhost IDENTIFIED
      BY '<password you want scorebot to use>';"
|

**7. Next import all the ticket database tables.**
   | mysql -uscorebot -p<password for scorebot> sts < sts/config/sts.sql
   | **Example:** mysql -uscorebot -pFAKEPASSWORD sts < setup/sts/config/sts.sql
|

At this point, we are now completed installed and ready to start configuring scorebot.
