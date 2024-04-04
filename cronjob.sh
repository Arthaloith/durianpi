#!/bin/bash

(crontab -l ; echo "@reboot cd /home/admin/Projects/durianpi && /home/admin/Projects/durianpi/myenv/bin/python webserver.py &") | crontab -

(crontab -l ; echo "0 6,18 * 1-2 0-6 cd /home/admin/Projects/durianpi && /home/admin/Projects/durianpi/myenv/bin/python pumpcontrol -p1") | crontab -
(crontab -l ; echo "0 6,18 * 3-4 0-6 cd /home/admin/Projects/durianpi && /home/admin/Projects/durianpi/myenv/bin/python pumpcontrol -p2") | crontab -
(crontab -l ; echo "0 6,18 * 5-6 0-6 cd /home/admin/Projects/durianpi && /home/admin/Projects/durianpi/myenv/bin/python pumpcontrol -p3") | crontab -

