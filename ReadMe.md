## PriceBot

A universal price finder for things, currently setup to work for automobiles only right now

Abstracted Sites:
- Craigslist

### Sample Runs

Look in the examples directory on how to use pricebot\
This folder also contains sample outputs of gathered results

Install python 3.12 for all users, and put it into C:\Python312

Install UV, a python package manager

    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

Install requirements

    uv sync

You may have to activate your venv by running

    \.venv\Scripts\activate

And then add chromedriver.exe to PATH\
(or put it in c:\python312 assuming python is in your PATH already)\
You may need to download the latest chrome driver to match the version of chrome you are using

