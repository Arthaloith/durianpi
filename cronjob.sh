#!/bin/bash

# Add the reboot cron job
(crontab -l ; echo "@reboot cd /home/admin/Projects/durianpi && /home/admin/Projects/durianpi/myenv/bin/python webserver.py &") | crontab -

# Add the Durian profiles cron jobs
(crontab -l ; echo "0 6,18 * 1-2 1-7 cd /home/admin/Projects/durianpi && /home/admin/Projects/durianpi/myenv/bin/python pumpcontrol.py p1") | crontab -
(crontab -l ; echo "0 6,18 * 3-4 1-7 cd /home/admin/Projects/durianpi && /home/admin/Projects/durianpi/myenv/bin/python pumpcontrol.py p2") | crontab -
(crontab -l ; echo "0 6,18 * 5-6 1-7 cd /home/admin/Projects/durianpi && /home/admin/Projects/durianpi/myenv/bin/python pumpcontrol.py p3") | crontab -


(crontab -l ; echo "0 10,18 * 1-2 1-7 cd /home/admin/Projects/durianpi && /home/admin/Projects/durianpi/myenv/bin/python pumpcontrol.py p1") | crontab -