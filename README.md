# Trade Execution and Monitoring Microservice

 This microservice provides functionality for receiving trade signals via a webhook, executing those trades, and actively monitoring them with stop-loss management. It is built on the FastAPI framework, offering both speed and ease of use.

## Core Features:

**Trade Execution**: Processes incoming trade signals and places orders accordingly. Handles both equity and option order types.

**Stop-Loss Monitoring**: Actively tracks open trades and triggers automatic counter trades (RMS exit) based on calculated stop-loss levels to manage risk.

**Account Integration**: Communicates with a users account service to fetch relevant account details (balances, margins).

## Prerequisites

**Python 3.10+**: Ensure you have a compatible Python version installed.


**Trading Platform Integration**: The code uses placeholders for interaction with an actual trading platform. 

## Setup

### **Clone the repository**
```bash
git clone https://github.com/kelue/falcon.git
```
### **Create a virtual environment**

```bash
cd trade-microservice
python3 -m venv env
source env/bin/activate 
```

### **Install dependencies**:

```bash
pip install -r requirements.txt
```

### **Environment Variables** (.env file):
Create a .env file in the project's root directory and populate it with the following:

```env

USERS_URL=<URL of  your account service>
SMARTAPI_USER=<Your trading platform's username>
SMARTAPI_PASS=<Your trading platform's password>
SMARTAPI_KEY=<Your trading platform's API key>
TOTP_SECRET=<Secret key for authentication>
```

### **Run the server**:

```bash
uvicorn main:app --reload
```

## Using the Webhook

The microservice exposes a webhook endpoint at /opentrade. Send trade signals to this endpoint as POST requests with the following JSON structure:

```json
{
    "symbolname" : "<name>",
    "signal" : "buy",
    "price" :  46000,
    "type" : "option/equity",
    "strategyname" : "str" 
}

```

## Additional Notes

Stop-Loss Management: The service calculates stop-loss prices based on the trade information and user-defined parameters (percentage or fixed amount). 

symbol_tokens.json: This file is used to store fetched tokens for symbols to streamline price retrieval.

