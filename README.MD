HOW TO RUN THIS: 

1. Install dependencies from requirements.txt using 'pip install -r requirements.txt'

2. change the following with your credentials from browserstack in browserstack.yml using env or hardcoding it.

    userName: ${BROWSERSTACK_USERNAME}
    accessKey: ${BROWSERSTACK_ACCESS_KEY}


3. run scraper.py
4. run 'browserstack-sdk pytest test_elpais.py -v -s' for browserstack testing
5. run 'pytest test_elpais.py -v -s' for local testing  