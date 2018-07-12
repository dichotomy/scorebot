#!/bin/bash

ln -s /opt/scorebot/scorebot/scorebot_assets/scorebot.service /etc/systemd/system/scorebot.service
ln -s /opt/scorebot/scorebot/scorebot_assets/scorebot.service /etc/systemd/system/multi-user.target/scorebot.service
ln -s /opt/scorebot/python/lib/python3.6/site-packages/django/contrib/admin/static/admin /opt/scorebot/scorebot/scorebot_static/admin
chmod http:http -R /opt/scorebot/uploads
chown 770 -R /opt/scorebot/uploads