
# Autonomous Agent Project

This project implements autonomous agents that communicate asynchronously, process incoming messages reactively, and perform proactive tasks based on internal conditions. These agents can represent various entities (like people, organizations, or devices) in a specific domain.

## Project Features

The autonomous agents in this project are designed with the following capabilities:

1. **Asynchronous Message Handling**: Agents interact with their environment by consuming and emitting messages.
2. **Reactive and Proactive Behavior**:
   - **Reactive**: Agents react to messages using specific handlers.
   - **Proactive**: Agents generate new messages based on internal state or time conditions.
3. **Continuous Operation**: Agents run continuously, handling incoming messages and performing actions periodically.

## Project Structure

### Main Components

1. **Agent**: The core of the autonomous agent system. It manages behaviors and message handlers, as well as the message inbox and outbox.
2. **Behaviors**: Define proactive operations performed by the agent periodically.
3. **Message Handlers**: Define how the agent reacts to specific message types.
4. **Message Bus**: Manages the messages flowing between agents.

### Included Behaviors and Handlers

- **RandomMessageBehavior**: Generates random 2-word messages from a predefined word list every 2 seconds.
- **HelloMessageHandler**: Responds to messages containing "hello" by printing them to stdout and sending a reply.
- **ERC20BalanceChecker**: Checks the balance of a specified ERC-20 token every 10 seconds.
- **CryptoTransferHandler**: Transfers 1 ERC-20 token to a specified address if a "crypto" message is received and there are sufficient tokens.

## Setup Instructions

1. **Clone the Repository**: Clone the repository to your local machine.

   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **Install Dependencies**: Install required Python libraries.

   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**: Create a `.env` file with the following environment variables:

   ```plaintext
   RPC_NODE_URL=<Your_RPC_Node_URL>
   TOKEN_ADDRESS=<ERC20_Token_Contract_Address>
   ETHEREUM_ADDRESS=<Your_Ethereum_Address>
   PRIVATE_KEY=<Your_Private_Key>
   ```

4. **Prepare Token ABI**: Ensure `token_abi.json` (containing the token ABI) is in the root directory.

5. **Set Up a Tenderly Fork**: Create a dedicated Tenderly fork for this project and ensure the fork URL is set in `RPC_NODE_URL`. Use this fork exclusively for the agent assignment.

## Running the Agents

1. **Run the Main Script**: Start the agents with the main script.

   ```bash
   python main.py
   ```

2. **Agent Interaction**: Two agents will be initialized:
   - Agent1's outbox is connected to Agent2's inbox and vice versa.
   - The agents will exchange messages and interact based on the configured behaviors and handlers.

3. **Testing**: Run unit and integration tests to verify functionality.

## Tests

1. **Unit Test**: Implements specific tests for individual components (e.g., a single agent's behavior).
2. **Integration Test**: Verifies communication and interaction between two agents.

Run the tests using:

```bash
pytest tests/
```

## Additional Notes

- **Dependencies**: This project uses `web3.py` for Ethereum blockchain interactions.
- **Error Handling**: Agents handle unexpected exceptions and log errors.
- **Logging**: Logs are configured to output to `stdout` for easy monitoring.
  
## Submitting the Project

Submit your project by creating a Pull Request (PR) and assigning reviewers `dvilelaf`, `jmoreira-valory`, and `dagacha`.
