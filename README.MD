Name: Parth Vasave
email: mailparthvasave@gmail.com

IMPORTANT: The public url of 'BrowserStack Automation build URL' is not working i.e it is showing blank page when I load it on web browser so to solve this issue i have downloaded and uploaded it on this github repo. please view it and if you can open the public url please do so at the link below: 

https://automate.browserstack.com/projects/El+Pa%C3%ADs+Opinion+Scraper/builds/El+Pa%C3%ADs+Scraper+Cross+Browser+Test/8?public_token=3fc733d557136e675ce67a5a526bd732641aa9d2a5e37e677ca6bd58d07928e8 

HOW TO RUN THIS: 

1. Install dependencies from requirements.txt using 'pip install -r requirements.txt'

2. change the following with your credentials from browserstack in browserstack.yml using env or hardcoding it.

    userName: ${BROWSERSTACK_USERNAME}
    accessKey: ${BROWSERSTACK_ACCESS_KEY}


3. run scraper.py
4. run 'browserstack-sdk pytest test_elpais.py -v -s' for browserstack testing
5. run 'pytest test_elpais.py -v -s' for local testing  
