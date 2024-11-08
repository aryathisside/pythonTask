import os
import asyncio
import json
from dotenv import load_dotenv
from web3 import Web3
from web3.contract import Contract

from common import Agent
from implementations import (
    RandomMessageBehavior,
    HelloMessageHandler,
    ERC20BalanceChecker,
    CryptoTransferHandler
)

async def setup_agent(name: str, web3: Web3, token_contract: Contract) -> Agent:
    """
    Set up an agent with all required behaviors and handlers
    
    Args:
        name: Name of the agent
        web3: Web3 instance
        token_contract: Token contract instance
        
    Returns:
        Configured Agent instance
    """
    agent = Agent(name)
    
    # Register behaviors
    agent.register_behavior(RandomMessageBehavior(agent.outbox))
    agent.register_behavior(
        ERC20BalanceChecker(
            web3,
            token_contract,
            os.getenv("ETHEREUM_ADDRESS")
        )
    )
    
    # Register handlers
    agent.register_handler(HelloMessageHandler())
    agent.register_handler(
        CryptoTransferHandler(
            web3,
            token_contract,
            os.getenv("ETHEREUM_ADDRESS"),
            os.getenv("PRIVATE_KEY")
        )
    )
    
    return agent

async def setup_web3() -> Web3:
    """Initialize and configure Web3 instance"""
    # Initialize Web3 with HTTP provider
    web3 = Web3(Web3.HTTPProvider(os.getenv("RPC_NODE_URL")))
    
    # Verify connection
    if not web3.is_connected():
        raise ConnectionError("Failed to connect to the Ethereum node")
        
    return web3

async def main():
    """Main function to set up and run the agents"""
    try:
        # Initialize Web3
        web3 = await setup_web3()
        
        # Load token ABI
        with open("./token_abi.json", "r") as abi_file:
            token_abi = json.load(abi_file)

        # Initialize contract
        token_contract = web3.eth.contract(
            address=Web3.to_checksum_address(os.getenv("TOKEN_ADDRESS")),
            abi=token_abi
        )
        
        # Create agents
        agent1 = await setup_agent("Agent1", web3, token_contract)
        agent2 = await setup_agent("Agent2", web3, token_contract)
        
        # Connect agents (agent1's outbox -> agent2's inbox and vice versa)
        agent1.outbox = agent2.inbox
        agent2.outbox = agent1.inbox
        
        # Run agents
        await asyncio.gather(
            agent1.run(),
            agent2.run()
        )
    except KeyboardInterrupt:
        print("\nShutting down agents...")
        if 'agent1' in locals(): agent1.stop()
        if 'agent2' in locals(): agent2.stop()
    except Exception as e:
        print(f"An error occurred: {e}")
        if 'agent1' in locals(): agent1.stop()
        if 'agent2' in locals(): agent2.stop()

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    required_env_vars = [
        "RPC_NODE_URL",
        "TOKEN_ADDRESS",
        "ETHEREUM_ADDRESS",
        "PRIVATE_KEY"
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        exit(1)
        
    # Run the main async function
    asyncio.run(main())