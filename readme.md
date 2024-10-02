
# Financial Fraud Detection System

## Overview

This project implements a sophisticated Financial Fraud Detection System using Python, Neo4j, and machine learning techniques. It models financial transactions and user relationships in Neo4j, detects anomalies, and identifies potentially fraudulent activities. The system also provides a RESTful API with endpoints to query transaction data, detect fraud, and visualize suspicious transaction paths.

### Key Features

- **Dense Graph Model**: Complex relationships between users, accounts, devices, locations, IP addresses, and merchants to mimic real-world scenarios.
- **Fraud Detection**: Utilizes machine learning techniques with graph-based features and time-series data to classify transactions as fraudulent or legitimate.
- **Robust API**: Provides endpoints for fraud detection, transaction queries, and investigation of suspicious paths.
- **Logging and Error Handling**: Logs important actions, predictions, and errors for better traceability.

## Use Case

### Scenario

The system models a financial institution with users, accounts, and transactions. Fraud patterns such as large transactions from unusual locations, transactions using high-risk devices or IP addresses, and anomalous transaction sequences are detected. The system flags transactions that meet specific fraud criteria and provides investigators with an API to explore suspicious transactions and relationships.

For example, a transaction initiated from an IP address associated with a foreign location and a high-risk device could be flagged as fraud based on predetermined rules and machine learning predictions.

## Database Schema Setup Guide

### Prerequisites

- **Neo4j**: Download and install [Neo4j Desktop](https://neo4j.com/download/) or use a hosted version like Neo4j AuraDB.
- **Python**: Install Python 3.8+ and required libraries.

### Node Types

- **User**: Represents users of the financial system.
  - Attributes: `user_id`, `name`, `age`, `location`, `email`, `phone`
  
- **Account**: Represents financial accounts owned by users.
  - Attributes: `account_id`, `account_type`, `creation_date`, `status`

- **Transaction**: Represents financial transactions between accounts.
  - Attributes: `transaction_id`, `amount`, `date`, `transaction_type`, `status`

- **Device**: Represents devices used to initiate transactions.
  - Attributes: `device_id`, `device_type`, `os`

- **Location**: Represents physical locations associated with transactions.
  - Attributes: `location_id`, `country`, `city`

- **IPAddress**: Represents IP addresses from which transactions are initiated.
  - Attributes: `ip_address_id`, `ip_address`

- **Merchant**: Represents merchants where transactions are made.
  - Attributes: `merchant_id`, `name`, `industry`

### Relationship Types

- `(User)-[:OWNS]->(Account)`
- `(User)-[:USES_DEVICE]->(Device)`
- `(User)-[:KNOWS]->(User)` (social connections)
- `(Account)-[:INITIATED]->(Transaction)`
- `(Transaction)-[:COMPLETED]->(Account)`
- `(Transaction)-[:AT]->(Merchant)`
- `(Transaction)-[:USING_DEVICE]->(Device)`
- `(Transaction)-[:FROM_LOCATION]->(Location)`
- `(Transaction)-[:USING_IP]->(IPAddress)`
- `(Device)-[:LOCATED_AT]->(Location)`
- `(IPAddress)-[:ASSOCIATED_WITH]->(Location)`

### Import Data into Neo4j

Use the provided `import_data.py` script to load the data into Neo4j.

1. Update the Neo4j credentials in `neo4j/config.py`.
2. Place the data CSV files in the `data/` directory.
3. Run the data import script:

```bash
cd neo4j/
python import_data.py
```

This will populate the Neo4j database with nodes and relationships representing the financial system.

## Deciding Factors for Fraud Detection

The system uses several factors to classify transactions as potentially fraudulent:

1. **Transaction Amount**: Large transactions, especially those above a certain threshold (e.g., $8000), are flagged.
2. **Foreign Locations**: Transactions initiated from locations outside of the user's home country (e.g., a U.S. user initiating a transaction from Russia) are considered risky.
3. **High-Risk Devices**: Mobile devices and tablets are considered higher risk due to their vulnerability to theft and malware.
4. **Suspicious IP Addresses**: IP addresses known to be associated with malicious activity or high-risk countries are flagged.
5. **Unusual Times**: Transactions made at unusual times (e.g., 2 AM) are more likely to be fraudulent.
6. **User Connections**: Users with fewer social connections (as modeled in the graph) might be more susceptible to fraud.

The machine learning model uses these features to detect anomalies in transactions, classifying them as either `fraud` or `legitimate`.

## API Guide

### Endpoints

#### 1. **Fraud Detection**

- **Endpoint**: `/predict`
- **Method**: POST
- **Description**: Predicts whether a transaction is fraudulent based on the provided features.

**Request Example**:

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "transaction_id": 5006,
  "amount": 10000.00,
  "is_foreign": 1,
  "device_risk": 1,
  "ip_risk": 1,
  "hour": 2,
  "user_connections": 1
}' http://127.0.0.1:5000/predict
```

**Response Example**:

```json
{
  "prediction": "fraud"
}
```

#### 2. **Get Transaction Details**

- **Endpoint**: `/transaction/<transaction_id>`
- **Method**: GET
- **Description**: Fetches details of a specific transaction, including the accounts involved, location, device, and IP address.

**Request Example**:

```bash
curl http://127.0.0.1:5000/transaction/5006
```

**Response Example**:

```json
{
  "transaction": {
    "transaction_id": 5006,
    "amount": 10000.0,
    "date": "2021-05-06T00:00:00.000+0000",
    "transaction_type": "Withdrawal",
    "status": "Completed"
  },
  "from_account": {
    "account_id": 1001,
    "account_type": "Checking",
    "creation_date": "2018-01-15",
    "status": "Active"
  },
  "to_account": null,
  "location": {
    "location_id": "L6",
    "country": "Russia",
    "city": "Moscow"
  },
  "device": {
    "device_id": "D1",
    "device_type": "Mobile",
    "os": "iOS"
  }
}
```

#### 3. **Get Fraud Path**

- **Endpoint**: `/fraud-path/<account_id>`
- **Method**: GET
- **Description**: Retrieves the path of suspicious transactions involving the specified account.

**Request Example**:

```bash
curl http://127.0.0.1:5000/fraud-path/1001
```

**Response Example**:

```json
{
  "paths": [
    [
      {"account_id": 1001, "account_type": "Checking", "creation_date": "2018-01-15", "status": "Active", "label": "Account"},
      {"transaction_id": 5001, "amount": 1500.0, "date": "2021-05-01T00:00:00.000+0000", "transaction_type": "Transfer", "status": "Completed", "label": "Transaction"},
      {"account_id": 1002, "account_type": "Savings", "creation_date": "2019-06-20", "status": "Active", "label": "Account"}
    ]
  ]
}
```

## Conclusion

This system demonstrates the use of graph databases and machine learning to detect financial fraud. By leveraging Neo4j for dense graph modeling and advanced relationships, the system provides an efficient method for identifying suspicious activities. The RESTful API allows users to interact with the system, making it suitable for integration into larger applications.

### Future Enhancements

- **Real-Time Processing**: Implement streaming data for real-time fraud detection.
- **Advanced Graph Algorithms**: Use Neo4j's Graph Data Science library for community detection and similarity scoring.
