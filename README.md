# Welcome to Airsigner! This auction system allows whitelisted MEV searchers to place silent bids for the right to use a certain bundle of oracle updates that they retrieve from a data provider via a signed message through an HTTP endpoint. 

## Airsigner Execution

### The Airsigner Execution piece runs at data provider and is responsible for signing bundles of bids that it receives from the Airsigner Relay, which is another execution running externally buy a trusted party or in the future a network of nodes operating in a decentralized manner.

### Start Airsigner Execution like so:
```
host:~/AirsignerRelay/airsigner$ python3 airsigner_execution.py
AirsignerExecution: Starting Airsigner Execution
AirsignerHttp: Starting Airsigner webserver at 192.168.1.93:33667
```

## Airsigner Relay

### The Airsigner Relay accepts bids from searchers, validates them, and communicates with the Airsigner to retrieve signed oracle updates based on the winner of each auction bundle.

### Start Airsigner Relay like so:
```
host:~/AirsignerRelay/relay$ python3 relay_execution.py
RelayExecution: Starting Relay auction execution on thread MainThread
RelayExecution: running event monitor service on thread: 2
RelayHttp: Starting Relay HTTP webserver at 192.168.1.93:33666 on thread 1
```

## Unit Tests

### There is a Unit Test script that will create random requests to the Airsigner Relay of many different types. There will be continuous successful requests, duplicate requests, incorrect requests, and others.

### Start Unit Tests like so:
```
host:~/AirsignerRelay/relay$ python3 unit_tests.py
{'success': '0xa30d1736223559b1cc637e3daaa8ce199d74cd2be777214ac89c4c195b770b95', 'subscription_ids': ['0xdd7a1204cca6280e04b940631b837681594b0a1122b1c48f14449bfa54c74419', '0xdf1f500ae61874b301ce737b820a30ce58c374db820b2b71e2c83a0813ccf801']}
```

## Check Winners

### There is a script to check auction winners through the web API /claim endpoint

### Check Winners like so:

```
host:~/AirsignerRelay/relay$ python3 check_winners.py
time: 1663647743
jacob: {"jacob": "no auctions won"}
midhav: {"midhav": "no auctions won"}
burak_the_legend: {"burak_the_legend": "no auctions won"}
```

## Outputs

### The Outputs for the different pieces will look like the following:

```
host:~/AirsignerRelay/relay$ python3 relay_execution.py
RelayExecution: Starting Relay auction execution on thread MainThread
RelayExecution: running event monitor service on thread: 2
RelayHttp: Starting Relay HTTP webserver at 192.168.1.93:33666 on thread 1
1663647027 Participant: object for new user created with key burak_the_legend
1663647027 Bid: burak_the_legend bids 12694818900 for bundle ID: 0x70b9919e1e7cd1d33582eb8fa6f6a0d8517240959f85c8f3669d0efc4f83cfbe auction time: 1663647020
1663647027 RelayExecution: burak_the_legend removed bid for bundle ID: 0x70b9919e1e7cd1d33582eb8fa6f6a0d8517240959f85c8f3669d0efc4f83cfbe
1663647029 Bid: burak_the_legend bids 7251451180 for bundle ID: 0x3c0f8e1eaa585ea565898ab5c972993324c504f7ed49fc8b620348207da17374 auction time: 1663647020
execution phase for auction started at 1663647020 will be completed at 1663647040
calculating winners
1663647030 RelayExecution: bid was queued for burak_the_legend
1663647031 RelayExecution: bid was queued for burak_the_legend
execution phase for auction started at 1663647020 will be completed at 1663647040
1663647033 Participant: object for new user created with key midhav
1663647033 RelayExecution: bid was queued for midhav
1663647033 RelayExecution: bid was queued for burak_the_legend
execution phase for auction started at 1663647020 will be completed at 1663647040
1663647035 RelayExecution: bid was queued for burak_the_legend
1663647035 RelayExecution: bid was queued for burak_the_legend
1663647035 RelayExecution: bid was queued for midhav
execution phase for auction started at 1663647020 will be completed at 1663647040
1663647036 RelayExecution: bid was queued for midhav
1663647038 RelayExecution: bid was queued for midhav
execution phase for auction started at 1663647020 will be completed at 1663647040
1663647039 RelayExecution: bid was queued for burak_the_legend
execution phase for auction started at 1663647020 will be completed at 1663647040
1663647041 Bid: burak_the_legend bids 8623054430 for bundle ID: 0xc4bfaad342a75f1e8f391467671cbf8e57059c7d5a2384ebe1b54480da72438e auction time: 1663647040
1663647041 RelayExecution: burak_the_legend removed bid for bundle ID: 0xc4bfaad342a75f1e8f391467671cbf8e57059c7d5a2384ebe1b54480da72438e
1663647041 Bid: midhav bids 13300987160 for bundle ID: 0xdf16210e7599b3f51b39756ef4bd0b2125e024c1779547363d37d01db6c8fd58 auction time: 1663647040
1663647041 RelayExecution: midhav removed bid for bundle ID: 0xdf16210e7599b3f51b39756ef4bd0b2125e024c1779547363d37d01db6c8fd58
there is a queue with a depth of 10, executing bids....
1663647042 Bid: midhav bids 12687787610 for bundle ID: 0xda139cb24cd036ead818b3721727cdf0a7f960608ae42bb36cbcb0cbb5745710 auction time: 1663647040
1663647042 RelayExecution: burak_the_legend removed bid for bundle ID: 0x8c4a60205f8dc1004c60e8f0adb6dc63462188e571d9f2c764a510f9a5665693
1663647042 Bid: midhav bids 10557089780 for bundle ID: 0xda139cb24cd036ead818b3721727cdf0a7f960608ae42bb36cbcb0cbb5745710 auction time: 1663647040
1663647042 Bid: midhav bids 4596536060 for bundle ID: 0x122f1ecb2925320e5a2cdc19008d3dded3ab3f9d772ecec32afb3bd4d6f20a07 auction time: 1663647040
1663647042 Bid: burak_the_legend bids 7509360110 for bundle ID: 0xf1356ae8609a7d2892dfe5416e8c582c31bca9406f58803962f9dec431b612ce auction time: 1663647040
1663647042 Bid: burak_the_legend bids 1935273170 for bundle ID: 0x9eb7978d6d59aa53b1c23a7a67c7926a7b7977806093fa486bc0ab9ac965eb72 auction time: 1663647040
1663647042 Bid: burak_the_legend bids 10749372350 for bundle ID: 0xfcca3ac895022bef9f6572eb0222c0f515b5535b7f6b15bc0e5110836e7a2ff5 auction time: 1663647040
1663647042 Bid: burak_the_legend bids 20722994200 for bundle ID: 0x8c4a60205f8dc1004c60e8f0adb6dc63462188e571d9f2c764a510f9a5665693 auction time: 1663647040
1663647043 Bid: midhav bids 7233910340 for bundle ID: 0x5aea3d42bc6a96d5970c80a99ee25a833d3729fbc2691f0da58752f9a5195fae auction time: 1663647040
1663647044 Bid: midhav bids 16922273850 for bundle ID: 0x761ea733fc9b9fa012a28559d6414be79e266e9b575d485b3824e777484d0ab9 auction time: 1663647040
1663647047 Bid: burak_the_legend bids 8913551860 for bundle ID: 0xf1356ae8609a7d2892dfe5416e8c582c31bca9406f58803962f9dec431b612ce auction time: 1663647040
1663647048 Bid: midhav bids 22120290510 for bundle ID: 0x1b7c00408ad7ba55df856976bbdc38b2a025ab6445f379cf710477a346431a21 auction time: 1663647040
1663647048 RelayExecution: midhav removed bid for bundle ID: 0x1b7c00408ad7ba55df856976bbdc38b2a025ab6445f379cf710477a346431a21
1663647050 RelayExecution: bid was queued for burak_the_legend
execution phase for auction started at 1663647040 will be completed at 1663647060
calculating winners
```

```
host:~/AirsignerRelay/airsigner$ python3 airsigner_execution.py
AirsignerExecution: Starting Airsigner Execution
AirsignerHttp: Starting Airsigner webserver at 192.168.1.93:33667
1663647091 AirsignerExecution: asset bitcoin price 1935999000000 at 1663647091 signatures 0x2a5845a015cfa3a2eff7633ca0df9500b69b714954263b11a412046b830615a648240a8e6f1125157ea05693d8e777ce73c77cc02ba6c64f529ccc6d561c8d111c & 0xdd823308b84d9dc2d331c419dbc003776fa458a816c65600f114cc726ea37f24125adb2f0565dc9e4b464d4665458d0ecf027278a4bb75e50058fe7d038a48661b
1663647091 AirsignerExecution: asset ethereum price 135692000000 at 1663647091 signatures 0x5de8960b975229ea9cc40135213aac2d8f016ab332df0ecb2046ab558901f8885b76e003bab61d9531c6b6fca3d105cc077dcd08381450f41d73f1c1a33498241c & 0x4596664cbf35d511d15c1a08d79b2b8105ff2b6faa7b11693eb2299c5b9481761b84903f1b872c18823094062ce65a1bb75b25c2e8d46e8299160672d2a26ab81c
1663647111 AirsignerExecution: asset solana price 3249000000 at 1663647111 signatures 0xb276f4131d557255a64f76795b9f223b1e756b8828f8d00e965f19af5ed2b51b0fe768a4db289ce5e529328fe6abfe17f124e44ffd52c8f6875a8ee284b330c71b & 0xc24eec4c094c09cf8a8f9ad93bac0bb4ae0f490e9f325b974a6e6488bac3b7330559c81caf366148aefed25aed0eb4bed1d643547b02682e5e31c110a8c333921b
```

```
vm-host-01:~/AirsignerRelay/relay$ python3 unit_tests.py
{'duplicates': "there is a duplicate in the list of subscription IDs provided: ['0xdf1f500ae61874b301ce737b820a30ce58c374db820b2b71e2c83a0813ccf801', '0xdf1f500ae61874b301ce737b820a30ce58c374db820b2b71e2c83a0813ccf801', '0xdf1f500ae61874b301ce737b820a30ce58c374db820b2b71e2c83a0813ccf801']"}
{'success': '0x70b9919e1e7cd1d33582eb8fa6f6a0d8517240959f85c8f3669d0efc4f83cfbe', 'subscription_ids': ['0xdd7a1204cca6280e04b940631b837681594b0a1122b1c48f14449bfa54c74419', '0xbb2dc3c049af90a82cd4d0f32d4954ce38bea01816fa631fffea4088df548eff']}
{'retracted': 'bid removed for bundle ID: 0x70b9919e1e7cd1d33582eb8fa6f6a0d8517240959f85c8f3669d0efc4f83cfbe'}
{'duplicates': "there is a duplicate in the list of subscription IDs provided: ['0xbb2dc3c049af90a82cd4d0f32d4954ce38bea01816fa631fffea4088df548eff', '0xdd7a1204cca6280e04b940631b837681594b0a1122b1c48f14449bfa54c74419', '0xbb2dc3c049af90a82cd4d0f32d4954ce38bea01816fa631fffea4088df548eff']"}
{'success': '0x3c0f8e1eaa585ea565898ab5c972993324c504f7ed49fc8b620348207da17374', 'subscription_ids': ['0xdf1f500ae61874b301ce737b820a30ce58c374db820b2b71e2c83a0813ccf801', '0xdd7a1204cca6280e04b940631b837681594b0a1122b1c48f14449bfa54c74419']}
{'queued': 'The auction started at 1663647020 is over and currently in the execution phase. Your bid has been queued for the next auction which starts at 1663647040'}

vm-host-02:~/AirsignerRelay/relay$ python3 unit_tests.py
{'success': '0x761ea733fc9b9fa012a28559d6414be79e266e9b575d485b3824e777484d0ab9', 'subscription_ids': ['0xdd7a1204cca6280e04b940631b837681594b0a1122b1c48f14449bfa54c74419', '0xbb2dc3c049af90a82cd4d0f32d4954ce38bea01816fa631fffea4088df548eff', '0xdf1f500ae61874b301ce737b820a30ce58c374db820b2b71e2c83a0813ccf801']}
{'duplicates': "there is a duplicate in the list of subscription IDs provided: ['0xbb2dc3c049af90a82cd4d0f32d4954ce38bea01816fa631fffea4088df548eff', '0xbb2dc3c049af90a82cd4d0f32d4954ce38bea01816fa631fffea4088df548eff', '0xdf1f500ae61874b301ce737b820a30ce58c374db820b2b71e2c83a0813ccf801']"}
{'rejected': "a subscription ID in ['0xbb2dc3c049af90a82cd4d0f32d4954ce38bea01816fa631fffea4088df548eff', '0xdd7a1204cca6280e04b940631b837681594b0a1122b1c48f14449bfa54c74419'] weren't valid or weren't whitelisted, or your account has too many strikes: 0, therefore no bundle was created"}
{'success': '0x1b7c00408ad7ba55df856976bbdc38b2a025ab6445f379cf710477a346431a21', 'subscription_ids': ['0xbb2dc3c049af90a82cd4d0f32d4954ce38bea01816fa631fffea4088df548eff', '0xdf1f500ae61874b301ce737b820a30ce58c374db820b2b71e2c83a0813ccf801', '0xdd7a1204cca6280e04b940631b837681594b0a1122b1c48f14449bfa54c74419']}
{'retracted': 'bid removed for bundle ID: 0x1b7c00408ad7ba55df856976bbdc38b2a025ab6445f379cf710477a346431a21'}
```

```
host:~/AirsignerRelay/relay$ python3 check_winners.py
time: 1663647743
jacob: {"jacob": "no auctions won"}
midhav: {"midhav": "no auctions won"}
burak_the_legend: {"your_latest_winners": [{"asset": "bitcoin", "auction_time": "1663647730", "dapi_signature": "0xbe13acddd9c0b361011da4fc40a7f6762f8e104978605db08de7017641f52d930a945092aa12cd6ce08795c706a9521a45f0aad71a5e9f0d572f37caf246aa131b", "relayer_signature": "0x699ac97b05b091d93002285479c7c4a3ad6cad49c6ccbc03c8d57ec47c51d00645826924af113b785c65aa1bda537c4e8082b9a43dcf5211cd72e031a5975ef31c", "price": "1937031000000", "price_decimals": "8", "airnode_time": "1663647740", "endpoint_id": "0xf10f067e716dd8b9c91b818e3a933b880ecb3929c04a6cd234c171aa27c6eefe", "subscription_id": "0xdd7a1204cca6280e04b940631b837681594b0a1122b1c48f14449bfa54c74419", "searcher": "0x19a4D3E10CF0416276a17F8af2d4119BDBa67FF6", "bid": 19097634610}, {"asset": "ethereum", "auction_time": "1663647730", "dapi_signature": "0x36259f461eee7192029488981bc66645614f3ff5dd250dbb77dcef538e17b734706cddc3ef69fce580560ee842285f98dd771dda2b52adb7c05d0f01ac320daa1c", "relayer_signature": "0x652732dcf13bc4ff44fba3cc3b48e9ee4a2f0be3aca3de977bc065467d680787074c7e40fcb422cfb8519d65ae47279f484c14d32227826ec83887f94294d8991b", "price": "135936999999", "price_decimals": "8", "airnode_time": "1663647740", "endpoint_id": "0xf10f067e716dd8b9c91b818e3a933b880ecb3929c04a6cd234c171aa27c6eefe", "subscription_id": "0xdf1f500ae61874b301ce737b820a30ce58c374db820b2b71e2c83a0813ccf801", "searcher": "0x19a4D3E10CF0416276a17F8af2d4119BDBa67FF6", "bid": 19097634610}, {"asset": "ethereum", "auction_time": "1663647730", "dapi_signature": "0x2affd35d6896d02167f77d7e7c6f620553b6c48387c61a83953a753d26adcbe730e14187e99dba986610f07d754211ae0a1a9b16560c7f7642944a28cf423b391b", "relayer_signature": "0xb51fa1d8f1c938f13d4ed0fe213e2489085c98f3c0645ec4aeeb09a20befbde8087bf343654fae78e2f65d16b958b7f79e5b99b50732e16d188d3b84e08e6e601b", "price": "135936999999", "price_decimals": "8", "airnode_time": "1663647741", "endpoint_id": "0xf10f067e716dd8b9c91b818e3a933b880ecb3929c04a6cd234c171aa27c6eefe", "subscription_id": "0xbb2dc3c049af90a82cd4d0f32d4954ce38bea01816fa631fffea4088df548eff", "searcher": "0x19a4D3E10CF0416276a17F8af2d4119BDBa67FF6", "bid": 19097634610}]}
```

### Proposal: https://forum.api3.org/t/secondary-proposal-airsigner-mev-airnode-development/1557
