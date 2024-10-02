# ml_models/feature_engineering.py
import pandas as pd
from neo4j import GraphDatabase
import sys
sys.path.append('../')
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

def extract_features():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        # Query transactions and related data
        results = session.run("""
           MATCH (u:User)-[:OWNS]->(a:Account)-[:INITIATED]->(t:Transaction)
            OPTIONAL MATCH (t)-[:FROM_LOCATION]->(l:Location)
            OPTIONAL MATCH (t)-[:USING_DEVICE]->(d:Device)
            OPTIONAL MATCH (t)-[:USING_IP]->(ip:IPAddress)
            OPTIONAL MATCH (t)-[:AT]->(m:Merchant)
            RETURN t.transaction_id AS transaction_id,
                t.amount AS amount,
                t.date AS date,
                t.transaction_type AS transaction_type,
                t.status AS status,
                a.account_id AS account_id,
                u.user_id AS user_id,
                l.country AS country,
                l.city AS city,
                d.device_type AS device_type,
                d.os AS os,
                ip.ip_address AS ip_address,
                m.name AS merchant_name,
                m.industry AS merchant_industry
        """)

        data = []
        for record in results:
            data.append(record.data())

    driver.close()

    df = pd.DataFrame(data)

    # Feature Engineering
    df['amount'] = df['amount'].astype(float)
    df['is_foreign'] = df['country'].apply(lambda x: 0 if x == 'USA' else 1)
    df['device_risk'] = df['device_type'].apply(lambda x: 1 if x in ['Mobile', 'Tablet'] else 0)
    df['ip_risk'] = df['ip_address'].apply(lambda x: 1 if x.startswith('198.') or x.startswith('203.') else 0)

    # Time-based features
    df['date'] = pd.to_datetime(df['date'])
    df['hour'] = df['date'].dt.hour

    # Graph-based features (e.g., number of connections)
    # For simplicity, we'll simulate this
    df['user_connections'] = df['user_id'].apply(lambda x: 2 if x == 1 else 1)

    # Select features
    features = df[['transaction_id', 'amount', 'is_foreign', 'device_risk', 'ip_risk', 'hour', 'user_connections']]
    features = features.fillna(0)

    # Save features
    features.to_csv('features.csv', index=False)

if __name__ == '__main__':
    extract_features()
