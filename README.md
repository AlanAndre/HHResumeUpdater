# HH Resume Updater
### This script allows you to raise your resume in the search automatically on hh.ru

#### How to use it:

> - You no longer need to download the driver of Chrome browser. Webdriver manager got you covered
>
> - Install selenium. pip install selenium==3.141.0
> 
> - create a 'config.py' file with "user_name, password = '$USERNAME', '$PASSWORD'"
>
> - Start script. You can choose how many times the script will run

#### With a Raspberry Pi:
Loguru is more memory intensive than 'print', so I've found.
> - `sudo apt-get install chromium-browser`
> 
> - `sudo apt-get install chromium-chromedriver`
> 
> - A nice idea to increase swap space:
> > - `sudo nano /etc/dphys-swapfile`
> > - Raspbian has 100MB of swap by default. You should change it to 2048MB in the configuration file. 
      So you will have to find this line:`CONF_SWAPSIZE=100` And then change it into:
      `CONF_SWAPSIZE=2048`
> > - `sudo /etc/init.d/dphys-swapfile stop`
> > - `sudo /etc/init.d/dphys-swapfile start`

> - This is my way of automating the process using Crontab which outputs standard output and standard error to "updater.log":
> > - `crontab -e`
> 
> > - `0 3,7,11,15,19,23 * * * /usr/bin/python3 <PATH>/hh_updater.py > <PATH>/updater.log 2>&1`
> 
> On my RasberryPi Zero, which is also running PiHole, the script takes +- 5 minutes.

#### Features of this script:

> - Works in hidden mode (the browser does not open) This can be changed in the settings
> 
> - Bypasses captcha
> 
> - Prints the result of execution to the console after each action
>
> - Writes the results of work to a log file
>
> - Possible errors are provided

#### CHANGES:

> - Uses <a href=https://github.com/Delgan/loguru>Loguru</a>, which covers the output and errors. Cleans up log file each 5 days. Can modify that.
> 
> - Brushed up the code
> 
> - Now uses selenium web-driver 
> 
> - Added random values of sleep
