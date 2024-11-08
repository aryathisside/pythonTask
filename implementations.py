import random
from web3 import AsyncWeb3
from web3.contract import Contract
from typing import List
from common import (
    Behavior,
    MessageHandler,
    Message,
    MessageType,
    MessageBus,
    logger
)

class RandomMessageBehavior(Behavior):
    """
    Generates random 2-word messages periodically
    """
    WORDS = ["hello", "sun", "world", "space", "moon", "crypto", 
             "sky", "ocean", "universe", "human"]
    
    def __init__(self, outbox: MessageBus):
        super().__init__(interval=2.0)  # Generate message every 2 seconds
        self.outbox = outbox
        
    async def execute(self) -> List[Message]:
        words = random.sample(self.WORDS, 2)
        content = f"{words[0]} {words[1]}"
        return [Message(
            type=MessageType.RANDOM,
            content=content
        )]

class HelloMessageHandler(MessageHandler):
    """
    Handles messages containing 'hello' and responds accordingly.
    Prevents infinite response loops by only responding to original hello messages.
    """
    async def can_handle(self, message: Message) -> bool:
        # Only handle messages of type HELLO or containing 'hello'
        # But ignore response messages to prevent loops
        return (message.type == MessageType.HELLO or "hello" in message.content.lower()) and \
               not message.content.startswith("Hello back!")
    
    async def handle(self, message: Message) -> List[Message]:
        logger.info(f"Received hello message: {message.content}")
        response_content = f"Hello back! Received: {message.content}"
        return [Message(
            type=MessageType.HELLO,
            content=response_content,
            metadata={
                "original_message": message.content,
                "is_response": True
            }
        )]
class ERC20BalanceChecker(Behavior):
    """
    Periodically checks ERC20 token balance
    """
    def __init__(self, web3: AsyncWeb3, token_contract: Contract, address: str):
        super().__init__(interval=10.0)  # Check balance every 10 seconds
        self.web3 = web3
        self.token_contract = token_contract
        self.address = address
    
    async def execute(self) -> List[Message]:
        try:
            balance = self.token_contract.functions.balanceOf(self.address).call()
            balance_eth = self.web3.from_wei(balance, 'ether')
            logger.info(f"Token balance for {self.address}: {balance_eth} ETH")
            
            return [Message(
                type=MessageType.BALANCE,
                content=str(balance_eth),
                metadata={
                    "address": self.address,
                    "raw_balance": str(balance),
                    "unit": "ether"
                }
            )]
        except Exception as e:
            logger.error(f"Error checking balance: {e}")
            return []

class CryptoTransferHandler(MessageHandler):
    """
    Handles crypto transfer messages and executes token transfers
    """
    def __init__(
        self, 
        web3: AsyncWeb3, 
        token_contract: Contract,
        source_address: str,
        private_key: str
    ):
        self.web3 = web3
        self.token_contract = token_contract
        self.source_address = source_address
        self.private_key = private_key
    
    async def can_handle(self, message: Message) -> bool:
        return (message.type == MessageType.CRYPTO or 
                "crypto" in message.content.lower())
    
    async def handle(self, message: Message) -> List[Message]:
        try:
            # Get target address from message metadata or use a default
            target_address = message.metadata.get("target_address", "0x0123456789012345678901234567890123456789")
            
            # Check balance
            balance = self.token_contract.functions.balanceOf(
                self.source_address
            ).call()
            
            if balance < self.web3.to_wei(1, 'ether'):
                logger.error("Insufficient balance for transfer")
                return []
                
            # Build transaction
            nonce = self.web3.eth.get_transaction_count(self.source_address)
            transfer_txn = self.token_contract.functions.transfer(
                target_address,
                self.web3.to_wei(1, 'ether')
            ).build_transaction({
                'from': self.source_address,
                'gas': 100000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': nonce,
            })
            
            # Sign and send transaction
            signed_txn = self.web3.eth.account.sign_transaction(
                transfer_txn, 
                self.private_key
            )
            tx_hash = self.web3.eth.send_raw_transaction(
                signed_txn.rawTransaction
            )
            
            logger.info(f"Transfer initiated: {tx_hash.hex()}")
            return [Message(
                type=MessageType.TRANSFER,
                content="Transfer successful",
                metadata={
                    "tx_hash": tx_hash.hex(),
                    "source_address": self.source_address,
                    "target_address": target_address
                }
            )]
        except Exception as e:
            logger.error(f"Error handling transfer: {e}")
            return []
