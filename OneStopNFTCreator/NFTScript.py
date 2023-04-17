
import hashlib
import json
import copy

from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from beaker import sandbox



def mintNFT(algod_client, creator_address, creator_private_key, asset_name, asset_unit_name):
    
    account_info: Dict[str, Any] = algod_client.account_info(creator_address)
    print(f"Account balance: {account_info.get('amount')} microAlgos")


    params = algod_client.suggested_params()
    
 
    unsigned_txn = transaction.AssetCreateTxn(
        sender=creator_address, 
        sp=params, 
        total=1, 
        decimals=0, 
        default_frozen=False,
        unit_name=asset_unit_name,
        asset_name=asset_name,
    )

    signed_txn = unsigned_txn.sign(creator_private_key)

    txid = algod_client.send_transaction(signed_txn)

    txn_result = transaction.wait_for_confirmation(algod_client, txid, 4)
    created_asset = txn_result["asset-index"]

    return created_asset 

def transferNFT(algod_client, creator_address, creator_private_key, receiver_address, receiver_private_key, asset_id):

    params = algod_client.suggested_params()

    optInTxn = transaction.AssetOptInTxn(
        receiver_address, 
        sp=params, 
        index = asset_id
    )
       
    newParams = copy.deepcopy(params)
    newParams.fee = 2 * params.min_fee
    newParams.flat_fee = True

    fundTxn = transaction.PaymentTxn(
        sender=creator_address, 
        sp= newParams, 
        receiver=receiver_address, 
        amt=200_000
    )

    newParams2 = copy.deepcopy(params)
    newParams2.fee = 0
    newParams2.flat_fee = True

    assetTxn = transaction.AssetTransferTxn(
        sender=creator_address, 
        sp=newParams2, 
        receiver=receiver_address, 
        amt=1, 
        index=asset_id
    )

    txns = [fundTxn, optInTxn, assetTxn]
    txnGroup = transaction.assign_group_id(txns=txns)
    signedTxns = [
        txns[0].sign(creator_private_key),
        txns[1].sign(receiver_private_key),
        txns[2].sign(creator_private_key)
    ]

    transactRes = algod_client.send_transactions(signedTxns)
    update_result = transaction.wait_for_confirmation(algod_client, transactRes, 4)
