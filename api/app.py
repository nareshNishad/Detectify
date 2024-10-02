# api/app.py

from flask import Flask, request, jsonify
from neo4j import GraphDatabase
import pandas as pd
import joblib
import sys
sys.path.append('../')
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, MODEL_PATH
import logging



# Initialize logging
logging.basicConfig(filename='../logs/app.log', level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

app = Flask(__name__)

# Load ML model
model = joblib.load(MODEL_PATH)

# Initialize Neo4j driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        features = pd.DataFrame([data])

        # Ensure all required features are present
        required_features = ['amount', 'is_foreign', 'device_risk', 'ip_risk', 'hour', 'user_connections']
        for feature in required_features:
            if feature not in features.columns:
                return jsonify({'message': f'Missing feature: {feature}'}), 400

        # Perform prediction
        prediction = model.predict(features[required_features])
        result = 'fraud' if prediction[0] == 1 else 'legitimate'

        # Log the prediction
        logging.info(f"Prediction made for transaction: {data['transaction_id']} - Result: {result}")

        return jsonify({'prediction': result})

    except Exception as e:
        logging.error(f"Error in /predict: {str(e)}")
        return jsonify({'message': 'An error occurred during prediction'}), 500

@app.route('/transaction/<transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (t:Transaction {transaction_id: $transaction_id})
                OPTIONAL MATCH (a:Account)-[:INITIATED]->(t)
                OPTIONAL MATCH (t)-[:COMPLETED]->(b:Account)
                OPTIONAL MATCH (t)-[:FROM_LOCATION]->(l:Location)
                OPTIONAL MATCH (t)-[:USING_DEVICE]->(d:Device)
                RETURN t, a, b, l, d
            """, transaction_id=int(transaction_id))

            record = result.single()
            if record:
                transaction = dict(record['t'])
                from_account = dict(record['a']) if record['a'] else None
                to_account = dict(record['b']) if record['b'] else None
                location = dict(record['l']) if record['l'] else None
                device = dict(record['d']) if record['d'] else None

                return jsonify({
                    'transaction': transaction,
                    'from_account': from_account,
                    'to_account': to_account,
                    'location': location,
                    'device': device
                })
            else:
                return jsonify({'message': 'Transaction not found'}), 404
    except Exception as e:
        logging.error(f"Error in /transaction/{transaction_id}: {str(e)}")
        return jsonify({'message': 'An error occurred fetching the transaction'}), 500

@app.route('/fraud-path/<account_id>', methods=['GET'])
def fraud_path(account_id):
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH path = (a:Account {account_id: $account_id})-[:INITIATED|COMPLETED*1..3]-(b:Account)
                RETURN path LIMIT 10
            """, account_id=int(account_id))

            paths = []
            for record in result:
                path = []
                for node in record['path'].nodes:
                    node_dict = dict(node)
                    node_dict['label'] = list(node.labels)[0]
                    path.append(node_dict)
                paths.append(path)

            return jsonify({'paths': paths})
    except Exception as e:
        logging.error(f"Error in /fraud-path/{account_id}: {str(e)}")
        return jsonify({'message': 'An error occurred fetching fraud paths'}), 500

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'message': 'Endpoint not found'}), 404

if __name__ == '__main__':
    app.run(debug=False)
