## PriceBot

A universal price finder for things, currently setup to work for automobiles only right now

Abstracted Sites:
- Craigslist
- Ebay
- AutoTempest

### Sample Runs

Look in the test directory for examples on how to use pricebot\
This folder also contains sample outputs of gathered results

Install python 3.12 for all users, and put it into C:\Python312

Install UV, a python package manager

Initiate the venv, py running the following
    uv venv --python=3.12

Activate your venv by running 
    \.venv\Scripts\activate

Install requirements
    uv pip install -r requirements.txt

And then pip install pricebot (Not sure if doing just this line will install requirements?)\
    uv pip install -e .

And then add chromedriver.exe to PATH (or put it in c:\python312 assuming python is in your PATH already)
