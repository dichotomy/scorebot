Configuration
==============


**1. Edit scorebotcfg.json**
   | #MySQL database info - Line 2 under "settings"
   | **sqlhost = "127.0.0.1"**  -  Enter the IP address of your mysql database if not on the same system
   | **sqluser = "scorebot"** -  Only change if you changed the scorebot username, otherwise leave it
   | **sqlpasswd = "password"** -  Change this to the scorebot password you selected
   | **sqldb = "sts"** -  This is the database you installed the ticket system as. Leave this be unless you changed it.
|

**2. Edit //var//www//html//sts//config//connect.php
   | Database config
   | $db_host                = 'localhost';
   | $db_user                = 'scorebot';
   | $db_pass                = 'password';
   | $db_database    = 'sts';

**3. We now need to add a few required users to the database.**




**5. Next we need to edit some of our python files in scorebot**
   Hopfully these will be moved to a single configuration file here in the near future, but as of now we need to edit a handful of files to reflect your IP structure
|

   ====================         =======         ======================          ==========
   File                         Line            Reads                           Change to
   ====================         =======         ======================          ==========
   Hosts.py			38		re.compile("^10")		Change the 10 to the first Octet of your subnet. I.E 192.168.1.x you would change to 192
   Service.py                   357             10.0.1.28                       No idea what this is used for.
   SiteSearch.py                700             google.com                      ?.
   Ping.py                      280             google.com                      (Might not be accessable on a closed network. Not sure exactly what this is used for).
   globalvars.py                26              dns = 192.168.100.56            (Change to your DNS).
   Host.py                      287             10.0.1.50			Not sure what this does, believe it's not used/testing?
   Host.py                      288             8.8.8.8                         Appears to be usless, was for testing?
   TicketInterface.py           199             beta.net                        Not sure.
   ====================         =======         ======================          ==========
|
