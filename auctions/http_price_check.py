import requests, json

def pricing(asset):
    url = 'https://vnci1lns59.execute-api.us-east-1.amazonaws.com/v1/0xf10f067e716dd8b9c91b818e3a933b880ecb3929c04a6cd234c171aa27c6eefe'
    api_key = '_diarrhea_out_the_dick_diarrhea_out_the_dick_'
    myobj = {'x-api-key': api_key}
    mydata = '{"parameters": {"coinId": "%s"}}' % asset
    response = requests.post(url, headers = myobj, data=mydata)
    data = json.loads(response.text)
    return data["rawValue"]["market_data"]["current_price"]['usd']


def pricing_encoded(mydata):
    url = 'https://vnci1lns59.execute-api.us-east-1.amazonaws.com/v1/0xf10f067e716dd8b9c91b818e3a933b880ecb3929c04a6cd234c171aa27c6eefe'
    api_key = '_diarrhea_out_the_dick_diarrhea_out_the_dick_'
    myobj = {'x-api-key': api_key}
    # mydata = '{"encodedParameters": "0x3173000000000000000000000000000000000000000000000000000000000000636f696e49640000000000000000000000000000000000000000000000000000657468657265756d000000000000000000000000000000000000000000000000"}'
    response = requests.post(url, headers=myobj, data=mydata)
    data = json.loads(response.text)
    return data#["rawValue"]["market_data"]["current_price"]['usd']



if __name__ == "__main__":
    mydata = '{"encodedParameters": "0x3173000000000000000000000000000000000000000000000000000000000000636f696e49640000000000000000000000000000000000000000000000000000657468657265756d000000000000000000000000000000000000000000000000"}'
    print(pricing_encoded(mydata))
