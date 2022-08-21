from defi_infrastructure.utilities.general.eip191_signer import sign_confirmation
from hdwallet import HDWallet
import json

def get_signed_boost_update(web3, price, time, mnemonic, base, quote, user):
    hdwallet: HDWallet = HDWallet(symbol="ETH", use_default_path=False)
    types = ['int256', 'uint256', 'bytes32', 'bytes32', 'address']
    values = [price, time, base, quote, user]
    hdwallet.from_mnemonic(mnemonic)
    hdwallet.from_path("m/44'/60'/0'/0/0")
    dump = json.dumps(hdwallet.dumps(), indent=4, ensure_ascii=False)
    account = web3.eth.account.from_key(json.loads(dump)["private_key"])
    signature = sign_confirmation(account, types, values).signature
    return signature