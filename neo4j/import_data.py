# neo4j/import_data.py
from neo4j import GraphDatabase
import pandas as pd
import sys
sys.path.append('../')
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

def import_data():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        # Import Users
        users = pd.read_csv('../data/users.csv')
        for _, row in users.iterrows():
            session.run("""
                MERGE (u:User {user_id: $user_id})
                SET u.name = $name, u.age = $age, u.location = $location, u.email = $email, u.phone = $phone
            """, **row.to_dict())

        # Import Accounts and Relationships
        accounts = pd.read_csv('../data/accounts.csv')
        for _, row in accounts.iterrows():
            session.run("""
                MERGE (a:Account {account_id: $account_id})
                SET a.account_type = $account_type, a.creation_date = $creation_date, a.status = $status
            """, **row.to_dict())

            # Create relationship between User and Account
            session.run("""
                MATCH (u:User {user_id: $user_id}), (a:Account {account_id: $account_id})
                MERGE (u)-[:OWNS]->(a)
            """, user_id=row['user_id'], account_id=row['account_id'])

        # Import Devices and Relationships
        devices = pd.read_csv('../data/devices.csv')
        for _, row in devices.iterrows():
            session.run("""
                MERGE (d:Device {device_id: $device_id})
                SET d.device_type = $device_type, d.os = $os
            """, **row.to_dict())

            # Create relationship between User and Device
            session.run("""
                MATCH (u:User {user_id: $user_id}), (d:Device {device_id: $device_id})
                MERGE (u)-[:USES_DEVICE]->(d)
            """, user_id=row['user_id'], device_id=row['device_id'])

        # Import Locations
        locations = pd.read_csv('../data/locations.csv')
        for _, row in locations.iterrows():
            session.run("""
                MERGE (l:Location {location_id: $location_id})
                SET l.country = $country, l.city = $city
            """, **row.to_dict())

        # Import IP Addresses
        ip_addresses = pd.read_csv('../data/ip_addresses.csv')
        for _, row in ip_addresses.iterrows():
            session.run("""
                MERGE (ip:IPAddress {ip_address_id: $ip_address_id})
                SET ip.ip_address = $ip_address
            """, **row.to_dict())

        # Create relationships between IP Addresses and Locations
        for _, row in ip_addresses.iterrows():
            location_id = 'L1'  # For simplicity, associate IPs with known locations
            session.run("""
                MATCH (ip:IPAddress {ip_address_id: $ip_address_id}), (l:Location {location_id: $location_id})
                MERGE (ip)-[:ASSOCIATED_WITH]->(l)
            """, ip_address_id=row['ip_address_id'], location_id=location_id)

        # Import Merchants
        merchants = pd.read_csv('../data/merchants.csv')
        for _, row in merchants.iterrows():
            session.run("""
                MERGE (m:Merchant {merchant_id: $merchant_id})
                SET m.name = $name, m.industry = $industry
            """, **row.to_dict())

        # Import Transactions and Relationships
        transactions = pd.read_csv('../data/transactions.csv')
        for _, row in transactions.iterrows():
            session.run("""
                MERGE (t:Transaction {transaction_id: $transaction_id})
                SET t.amount = $amount, t.date = $date, t.transaction_type = $transaction_type, t.status = $status
            """, **row.to_dict())

            # Create relationships for 'from_account' and 'to_account'
            if pd.notnull(row['from_account']):
                session.run("""
                    MATCH (a:Account {account_id: $from_account}), (t:Transaction {transaction_id: $transaction_id})
                    MERGE (a)-[:INITIATED]->(t)
                """, from_account=row['from_account'], transaction_id=row['transaction_id'])

            if pd.notnull(row['to_account']):
                session.run("""
                    MATCH (a:Account {account_id: $to_account}), (t:Transaction {transaction_id: $transaction_id})
                    MERGE (t)-[:COMPLETED]->(a)
                """, to_account=row['to_account'], transaction_id=row['transaction_id'])

            # Link transaction to merchant if applicable
            if pd.notnull(row['merchant_id']):
                session.run("""
                    MATCH (t:Transaction {transaction_id: $transaction_id}), (m:Merchant {merchant_id: $merchant_id})
                    MERGE (t)-[:AT]->(m)
                """, transaction_id=row['transaction_id'], merchant_id=row['merchant_id'])

            # Link transaction to device
            if pd.notnull(row['device_id']):
                session.run("""
                    MATCH (t:Transaction {transaction_id: $transaction_id}), (d:Device {device_id: $device_id})
                    MERGE (t)-[:USING_DEVICE]->(d)
                """, transaction_id=row['transaction_id'], device_id=row['device_id'])

            # Link transaction to location
            if pd.notnull(row['location_id']):
                session.run("""
                    MATCH (t:Transaction {transaction_id: $transaction_id}), (l:Location {location_id: $location_id})
                    MERGE (t)-[:FROM_LOCATION]->(l)
                """, transaction_id=row['transaction_id'], location_id=row['location_id'])

            # Link transaction to IP address
            if pd.notnull(row['ip_address_id']):
                session.run("""
                    MATCH (t:Transaction {transaction_id: $transaction_id}), (ip:IPAddress {ip_address_id: $ip_address_id})
                    MERGE (t)-[:USING_IP]->(ip)
                """, transaction_id=row['transaction_id'], ip_address_id=row['ip_address_id'])

        # Create 'KNOWS' relationships among users (simulating social connections)
        session.run("""
            MATCH (u1:User {user_id: 1}), (u2:User {user_id: 2})
            MERGE (u1)-[:KNOWS]->(u2)
        """)
        session.run("""
            MATCH (u2:User {user_id: 2}), (u3:User {user_id: 3})
            MERGE (u2)-[:KNOWS]->(u3)
        """)
        session.run("""
            MATCH (u3:User {user_id: 3}), (u4:User {user_id: 4})
            MERGE (u3)-[:KNOWS]->(u4)
        """)
        session.run("""
            MATCH (u4:User {user_id: 4}), (u5:User {user_id: 5})
            MERGE (u4)-[:KNOWS]->(u5)
        """)

    driver.close()

if __name__ == '__main__':
    import_data()
