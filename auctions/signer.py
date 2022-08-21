from eth_account import Account
from eth_account.messages import defunct_hash_message
from eth_abi.packed import encode_single_packed
import eth_utils

def encoded_values(abi_types, values):
    if len(abi_types) != len(values):
        raise ValueError("Length mismatch between provided abi types and values.  Got {0} types and {1} values.".format(len(abi_types), len(values)))
    return ''.join(encode_single_packed(abi_type, value).hex() for abi_type, value in zip(abi_types, values))

def solidity_keccak(abi_types, values):
    if len(abi_types) != len(values):
        raise ValueError("Length mismatch between provided abi types and values.  Got {0} types and {1} values.".format(len(abi_types), len(values)))
    hex_string = eth_utils.add_0x_prefix(''.join(encode_single_packed(abi_type, value).hex() for abi_type, value in zip(abi_types, values)))
    return eth_utils.keccak(hexstr=hex_string)

def sign_confirmation(account, abi_types, values):
    hash = solidity_keccak(abi_types=abi_types, values=values)
    msg_hash = defunct_hash_message(hexstr=hash.hex())
    signed_msg_hash = Account.signHash(msg_hash, account.privateKey)
    return signed_msg_hash
