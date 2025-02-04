import asyncio
import json
import random
import sys

from web3 import AsyncWeb3, AsyncHTTPProvider
from web3.eth import AsyncEth
import requests
from loguru import logger

logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> | <level>{message}</level>",
    colorize=True,
)
log = logger


async def send_ethereum_transaction(private_key, to_address, value_eth, semaphore, delay, w3):
    """
    Async function for sending simple transaction from private keys to wallet in `receivers.txt` in Ethereum.
    Currently, this managed for Sahara AI quest with chainID 313313

    :param private_key: private key of sender.
    :param to_address: receiver address.
    :param value_eth: value for send.
    :param provider_url: EVM node rpc.
    :param proxy_url: optional proxy.
    :return: hash of transaction.
    """
    async with semaphore:
        logger.info(f"Sleeping for: {delay} seconds...")
        await asyncio.sleep(delay)

        # Get wallet address from private key
        account = w3.eth.account.from_key(private_key)
        from_address = account.address

        logger.info(f"Start sending TX | value: {value_eth:.12f} ETH to {to_address} | {from_address}")

        current_gas_price = await w3.eth.gas_price

        # Creaating transaction data
        transaction = {
            'chainId': 313313,
            'from': from_address,
            'to': w3.to_checksum_address(to_address),
            'value': w3.to_wei(value_eth, 'ether'),
            'gasPrice': current_gas_price,
            'nonce': await w3.eth.get_transaction_count(from_address),
            'data': '0x'
        }

        try:
            estimated_gas = await w3.eth.estimate_gas(transaction)
            transaction['gas'] = estimated_gas
        except Exception as e:
            logger.error(f"While gas check: {e} | {from_address}")
            return

        account_balance = await w3.eth.get_balance(from_address)

        # Transaction cost (gas * gas price + value)
        transaction_cost = transaction['gas'] * transaction['gasPrice'] + transaction['value']

        if account_balance < transaction_cost:
            logger.error(f"Insufficient balance, need: {w3.from_wei(transaction_cost, 'ether')} ETH "
                         f"| {from_address} | balance: {w3.from_wei(account_balance, 'ether')} ETH")
            return

        signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
        txn_hash = await w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        logger.success(f"Sent TX | Hash: {w3.to_hex(txn_hash)} | {from_address}")
        return


async def main():
    with open("private_keys.txt", "r") as file:
        private_keys = [line.strip() for line in file.readlines()]
        logger.info(f'Imported {len(private_keys)} wallets')

    with open("receivers.txt", "r") as file:
        recipient_addresses = [line.strip() for line in file.readlines()]
        logger.info(f'Imported {len(recipient_addresses)} recipient addresses')

    random.shuffle(private_keys)

    with open("settings.json", "r") as file:
        settings = json.load(file)
    provider_url = settings.get('rpc', 'https://testnet.saharalabs.ai')
    proxy_url = settings.get('proxy', '')

    session = None
    if proxy_url:
        session = requests.Session()
        session.proxies.update({
            "http": proxy_url,
            "https": proxy_url,
        })

    w3 = AsyncWeb3(
        AsyncHTTPProvider(provider_url, session),
        modules={"eth": (AsyncEth,)},
    )

    # Checking connection
    if not await w3.is_connected():
        raise Exception("Failed to connect to RPC")

    max_concurrent_tasks = settings.get('flows', 10)
    semaphore = asyncio.Semaphore(max_concurrent_tasks)

    tasks = []
    for private_key in private_keys:
        to_address = random.choice(recipient_addresses)

        min_value = settings.get("min_value", 0.00000000001)
        max_value = settings.get("max_value", 0.00000000001)
        value_eth = round(random.uniform(min_value, max_value), 12)

        delay = random.randint(settings["min_delay"], settings["max_delay"])

        task = asyncio.create_task(send_ethereum_transaction(semaphore=semaphore,
                                                             private_key=private_key,
                                                             to_address=to_address,
                                                             value_eth=value_eth,
                                                             w3=w3,
                                                             delay=delay))
        tasks.append(task)

    await asyncio.gather(*tasks)


asyncio.run(main())
