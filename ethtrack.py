from requests import get
from matplotlib import pyplot as plt
from datetime import datetime

API_KEY = "PTWVEPNI8B27DWH5XZ8RXFH28D2J4ID79J"
address = "0x73bceb1cd57c711feac4224d062b0f6ff338501e"
BASE_URL = "https://api.etherscan.io/api"
ETHER_VALUE = 10**18 #data is given in wei which is 1/10^18 eth

def make_api_url(module, action, address, **kwargs): #**kwargs allows u to pass unlimited keyword arguments, get and can access them as a dictionary
    url = BASE_URL + f"?module={module}&action={action}&address={address}&apikey={API_KEY}"

    for key, value in kwargs.items():
        url += f"&{key}={value}"

    return url

def get_account_balance(address):
    get_balance_url = make_api_url("account", "balance", address, tag="latest", x="2")
    response = get(get_balance_url) #get request
    data = response.json() #will return me a python dictionary with the data

    value = int(data["result"])/ETHER_VALUE
    return value

def get_transactions(address):
    get_transactions_url = make_api_url("account", "txlist", address, startblock=0, endblock=99999999, page=1, offset=10000, sort="asc")
    response = get(get_transactions_url)
    data = response.json()["result"] #takes the list under result

    get_internal_tx_url = make_api_url("account", "txlistinternal", address, startblock=0, endblock=99999999, page=1, offset=10000, sort="asc")
    response2 = get(get_internal_tx_url)
    data2 = response2.json()["result"]

    data.extend(data2) #adds internal (smart contract tx) to normal tx
    data.sort(key=lambda x: x['timeStamp']) #sorts all transactions based on timeStamp

    current_balance = 0
    balances = []
    times = []

    for tx in data:
        to = tx["to"] 
        from_address = tx["from"]
        value = int(tx["value"])/ETHER_VALUE
        if "gasPrice" in tx: #internal transactions dont have "gasPrice" key in json
            gas = int(tx["gasUsed"]) * int(tx["gasPrice"]) / ETHER_VALUE
        else:
            gas = int(tx["gasUsed"])/ ETHER_VALUE

        time = datetime.fromtimestamp(int(tx['timeStamp'])) #converts date
        money_in = to.lower() == address.lower()

        if money_in:
            current_balance += value
        else:
            current_balance -= value + gas #pays gas if send

        balances.append(current_balance)
        times.append(time)

    plt.plot(times, balances)
    plt.show()

get_transactions(address)