import requests, time, datetime

def run():
    for api_key in ['jacob', 'midhav', 'burak_the_legend']:
        response = requests.get("http://192.168.1.93:33666/claim?key="+api_key)
        print(f'{api_key}: {response.text}')

if __name__ == "__main__":
    print("time:", int(time.mktime(datetime.datetime.now().timetuple())))
    run()

