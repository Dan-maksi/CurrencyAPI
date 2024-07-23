from fastapi import FastAPI
import requests
from pydantic import BaseModel
from bs4 import BeautifulSoup

# to startup local host:
#   pip install uvicorn
#   uvicorn conversionAPI:app --reload

app = FastAPI()


class Exchange(BaseModel):
    currency_from: str
    currency_to: str
    amount: float


class History(BaseModel):
    year_from: int
    amount: float
    year_to: int


def getExchangeAPI(find, currency_from):
    baseurl = 'https://api.frankfurter.app'

    if currency_from is None:
        endpoint = f'/{find}'
    else:
        endpoint = f'/{find}?from={currency_from}'

    url = baseurl + endpoint
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None


@app.get("/")
def home():
    return {"message": "Welcome to Currency Conversion API"}


@app.get("/list")
def getList():
    data = getExchangeAPI('currencies', None)
    if data is None:
        return {'data': 'Error!'}
    else:
        return data


@app.post("/convert")
def convert(converter: Exchange):
    data = getExchangeAPI('latest', converter.currency_from.upper())
    if converter.currency_from.upper() == converter.currency_to.upper():
        rate = 1
    else:
        rate = data['rates'][converter.currency_to.upper()]
    value = converter.amount * rate
    return {'value': '{:,.2f}'.format(value)}


@app.post("/history")
def history(historical: History):
    if 2024 <= historical.year_from <= 1792 or 2024 <= historical.year_to <= 1792:
        return {'data': 'Year Error!'}
    else:
        url = f'https://www.in2013dollars.com/us/inflation/{historical.year_from}?endYear={historical.year_to}&amount={historical.amount}'

        response = requests.get(url)

        if response.status_code == 200:
            doc = BeautifulSoup(response.text, "html.parser")
            final_amount = doc.findAll(class_='highlighted-amount')[1].text
            return {'value': final_amount}
        else:
            return {'data': response.status_code + ' Error!'}
