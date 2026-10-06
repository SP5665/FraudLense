FraudLense

FraudLense is an AI/ML-based fraud detection and investigation system designed to identify potentially fraudulent credit card transactions, explain model predictions, and support an analyst investigation workflow.

The project combines machine learning, SHAP explainability, MySQL, FastAPI, and Streamlit to create an end-to-end fraud detection system.

📌 Project Overview

Fraud detection is a highly imbalanced classification problem where fraudulent transactions represent only a very small portion of all transactions.

FraudLense uses an XGBoost classification model to generate a fraud probability for each transaction. High-risk transactions are further analyzed using SHAP explainability, allowing the system to identify the features that contributed most strongly to the prediction.

The results are stored in a MySQL database and exposed through a FastAPI backend. A Streamlit dashboard provides an interface for transaction screening, investigation, and audit-log review.

🚀 Key Features
AI/ML-based fraud detection using XGBoost
Handling of severe class imbalance using scale_pos_weight
Fraud probability scoring
Configurable fraud detection threshold
SHAP-based model explainability
Identification of top contributing features
Single transaction prediction
Batch CSV transaction screening
Automatic investigation creation for HIGH-risk transactions
Analyst investigation workflow
Analyst decisions and notes
Audit logging
MySQL database integration
FastAPI backend
Swagger API documentation
Streamlit interactive dashboard
Database table views
Source-file based transaction screening
🏗️ System Architecture
                    CREDIT CARD DATASET
                            |
                            v
                     Pandas / NumPy
                            |
                            v
                    Data Preparation
                            |
                            v
                 XGBoost Classification
                   + scale_pos_weight
                            |
                            v
                    Fraud Probability
                            |
                +-----------+-----------+
                |                       |
                v                       v
              LOW                     HIGH
                |                       |
                |                       v
                |                SHAP Explanation
                |                       |
                |                       v
                |               Top Contributors
                |                       |
                +-----------+-----------+
                            |
                            v
                     MySQL Database
                            |
                            v
                       FastAPI API
                            |
                            v
                  Streamlit Dashboard
                            |
                            v
                 Analyst Investigation
                            |
                            v
                       Audit Logs
🛠️ Technology Stack
Programming Language
Python 3.11.9
Machine Learning
Pandas
NumPy
Scikit-learn
XGBoost
SHAP
Backend
FastAPI
Uvicorn
Database
MySQL
MySQL Connector/Python
Frontend / Dashboard
Streamlit
Visualization
Matplotlib
Other Libraries
Requests
python-dotenv
python-multipart
Development Tools
Visual Studio Code
Git
GitHub
MySQL Workbench
📊 Dataset

FraudLense currently uses the publicly available Credit Card Fraud Detection dataset.

The dataset contains 284,807 transactions and the following main columns:

Time
V1 to V28
Amount
Class
Target Variable
0 → Normal transaction
1 → Fraudulent transaction
Dataset Distribution
Normal transactions: 284,315
Fraudulent transactions: 492
Fraudulent transactions: 0.173%

This severe class imbalance makes fraud detection a challenging classification problem.

Important Note About V1-V28

V1 through V28 are anonymized PCA-transformed numerical features.

They are used by the machine learning model as statistical patterns and should not be interpreted as specific real-world attributes such as merchant type, location, card type, or transaction category.

The original dataset is not included in this repository.

🔄 Machine Learning Pipeline

The machine learning pipeline consists of the following stages:

Dataset
   |
   v
Data Loading
   |
   v
Feature / Target Separation
   |
   v
Stratified Train-Test Split
   |
   v
Class Imbalance Handling
   |
   v
XGBoost Training
   |
   v
Model Evaluation
   |
   v
Model Saving
   |
   v
Fraud Prediction
   |
   v
SHAP Explanation
1. Data Preparation

The dataset is loaded using Pandas and separated into:

Features (X)
Target (y)

The data is split into training and testing sets using a stratified split so that the fraud/normal class distribution is preserved.

2. Handling Class Imbalance

FraudLense uses XGBoost's scale_pos_weight parameter to give more importance to the minority fraud class during training.

The weight is calculated as:

Number of Normal Transactions
--------------------------------
Number of Fraudulent Transactions

The calculated value for the training data was approximately:

577.29

SMOTE was considered as an alternative approach, but it is not combined with scale_pos_weight in the final pipeline.

3. XGBoost Model

FraudLense uses an XGBoost classifier for fraud detection.

The current model configuration includes:

n_estimators     = 200
max_depth        = 6
learning_rate    = 0.1
eval_metric      = logloss
random_state     = 42

The scale_pos_weight value is calculated from the training data.

The trained model is saved as:

models/fraud_model.json
🎯 Fraud Probability and Risk Classification

The model produces a probability indicating how strongly the transaction is predicted to belong to the fraud class.

The current baseline threshold is:

0.5

The threshold is configurable through the .env file:

FRAUD_THRESHOLD=0.5

The classification logic is:

Fraud Probability >= Threshold
            |
            v
           HIGH


Fraud Probability < Threshold
            |
            v
            LOW

The threshold can be adjusted later depending on the desired precision-recall trade-off.

📈 Model Evaluation

The model was evaluated using:

Precision
Recall
F1-score
Confusion Matrix
ROC-AUC
PR-AUC

Current test-set results:

Metric	Score
Fraud Precision	0.88
Fraud Recall	0.84
Fraud F1-score	0.86
ROC-AUC	0.9684
PR-AUC	0.8787
Confusion Matrix
                 Predicted
                 Normal   Fraud

Actual Normal     56853     11
Actual Fraud         16     82

These results are based on the current public benchmark dataset and model configuration.

🔍 SHAP Explainability

FraudLense uses SHAP (SHapley Additive exPlanations) to explain model predictions.

SHAP identifies how individual features contributed to a particular model prediction.

For high-risk transactions, FraudLense calculates SHAP values and selects the top contributing features.

Example:

Feature	SHAP Value
V14	+6.13
V4	+1.91
V10	+1.66
V3	+1.54
V7	+1.03
Interpreting SHAP Values
Positive SHAP value → pushes the prediction toward the fraud class
Negative SHAP value → pushes the prediction away from the fraud class
Larger absolute SHAP value → stronger contribution to that prediction

SHAP values represent model contribution values. They are not percentages of fraud probability.

🗄️ MySQL Database

FraudLense uses MySQL to persist transactions, predictions, investigations, and audit logs.

The database contains four main tables.

1. Transactions

Stores transaction information.

Main fields include:

transaction_id
transaction_time
amount
v1 to v28
source_file
created_at
2. Predictions

Stores model prediction results.

Main fields include:

prediction_id
transaction_id
fraud_probability
risk_level
model_version
predicted_at
3. Investigations

Stores investigation information for flagged transactions.

Main fields include:

investigation_id
transaction_id
status
analyst_decision
analyst_notes
created_at
updated_at
4. Audit Logs

Stores actions performed during investigations.

Main fields include:

log_id
transaction_id
action
details
timestamp
🔎 Investigation Workflow

When a transaction is classified as HIGH risk, FraudLense can create an investigation record.

Transaction
     |
     v
Fraud Prediction
     |
     v
HIGH Risk
     |
     v
SHAP Explanation
     |
     v
Investigation Created
     |
     v
Analyst Reviews Transaction
     |
     v
Analyst Records Decision
     |
     v
Audit Log

The analyst can review:

Transaction details
Fraud probability
Risk level
SHAP feature contributions
Investigation status
Analyst notes

The analyst can then record a decision for the investigation.

📂 Batch Transaction Screening

FraudLense supports uploading CSV files containing multiple transactions.

The batch workflow is:

CSV Upload
     |
     v
Validate Required Columns
     |
     v
Run XGBoost Predictions
     |
     v
Generate Fraud Probabilities
     |
     v
Classify Risk
     |
     +------------------+
     |                  |
     v                  v
    LOW                HIGH
     |                  |
     |                  v
     |            Create Investigation
     |                  |
     +--------+---------+
              |
              v
       Store in MySQL

The dashboard provides:

Total transactions
HIGH-risk transactions
LOW-risk transactions
Flagged transactions
🌐 FastAPI Backend

FastAPI acts as the backend layer between the Streamlit dashboard, machine learning components, and database.

Prediction Endpoints
POST /predict
POST /predict/batch
Transaction Endpoints
GET /transactions
GET /transactions/{transaction_id}
GET /transactions/{transaction_id}/prediction
GET /transactions/{transaction_id}/investigation
GET /transactions/{transaction_id}/details
GET /transactions/{transaction_id}/explanation
GET /transactions/by-source
Investigation Endpoints
POST /investigations
POST /investigations/{id}/decision
Audit Endpoint
GET /audit-logs
Database Endpoints
GET /database/transactions
GET /database/predictions
GET /database/investigations
GET /database/audit-logs
📖 Swagger API Documentation

FastAPI provides interactive API documentation through Swagger UI.

After starting the backend, open:

http://127.0.0.1:8000/docs

Swagger can be used to:

View available endpoints
Send API requests
Test request parameters
Inspect API responses
🖥️ Streamlit Dashboard

The Streamlit dashboard provides an interactive interface for FraudLense.

The dashboard supports:

CSV upload
Batch transaction screening
Screening summary
Flagged transaction viewing
Investigation selection
Transaction details
Transactions database view
Predictions database view
Investigations database view
Audit logs database view

The investigation page provides detailed information about a selected transaction and its SHAP explanation.

📁 Project Structure
FraudLense/
│
├── data/
│   └── creditcard.csv
│
├── models/
│   └── fraud_model.json
│
├── uploads/
│   └── uploaded CSV files
│
├── src/
│   ├── __init__.py
│   ├── check_data.py
│   ├── create_test_batch.py
│   ├── create_test_data.py
│   ├── dashboard.py
│   ├── database.py
│   ├── eda.py
│   ├── explain_model.py
│   ├── main.py
│   ├── predict.py
│   ├── prepare_data.py
│   ├── threshold_analysis.py
│   ├── train_model.py
│   │
│   └── pages/
│       ├── audit.py
│       └── investigation.py
│
├── .env
├── .gitignore
├── README.md
├── requirements.txt
└── venv/

venv/, .env, dataset files, and generated files are excluded from Git using .gitignore.

📄 Important Source Files
File	Purpose
check_data.py	Checks dataset structure and basic statistics
eda.py	Performs exploratory data analysis
prepare_data.py	Prepares data and calculates class imbalance
train_model.py	Trains and evaluates the XGBoost model
threshold_analysis.py	Analyzes different prediction thresholds
explain_model.py	Generates SHAP model explanations
predict.py	Handles transaction prediction and SHAP explanations
database.py	Handles MySQL database operations
main.py	FastAPI backend
dashboard.py	Main Streamlit dashboard
investigation.py	Investigation interface
audit.py	Audit log interface
create_test_data.py	Creates test transaction data
create_test_batch.py	Creates test batch data
⚙️ Installation
1. Clone the Repository
git clone <your-github-repository-url>
cd FraudLense
2. Create a Virtual Environment

FraudLense uses Python 3.11.

python -m venv venv
3. Activate the Virtual Environment

On Windows PowerShell:

Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
venv\Scripts\activate
4. Install Dependencies
pip install -r requirements.txt
🔐 Environment Configuration

Create a .env file in the project root:

MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=fraudlense
FRAUD_THRESHOLD=0.5

The .env file should never be committed to GitHub because it contains database credentials.

🗃️ Database Setup

Create the MySQL database:

CREATE DATABASE fraudlense;

USE fraudlense;

Create the following tables:

transactions
predictions
investigations
audit_logs

The database credentials should be stored in .env.

▶️ Running the Application

FraudLense requires both the FastAPI backend and Streamlit dashboard.

Start FastAPI

From the project root:

uvicorn src.main:app --reload

The backend will run at:

http://127.0.0.1:8000

Swagger documentation:

http://127.0.0.1:8000/docs
Start Streamlit

Open another terminal, activate the virtual environment, and run:

streamlit run src/dashboard.py

The FraudLense dashboard will open in your browser.

🔄 End-to-End Workflow

A typical FraudLense workflow looks like this:

1. Upload CSV
       |
       v
2. Validate required columns
       |
       v
3. XGBoost generates fraud probabilities
       |
       v
4. Transactions receive LOW/HIGH risk
       |
       v
5. Results stored in MySQL
       |
       v
6. HIGH-risk transactions receive investigations
       |
       v
7. SHAP identifies important model contributors
       |
       v
8. Analyst reviews the transaction
       |
       v
9. Analyst records decision and notes
       |
       v
10. Activity is recorded in audit logs
🧪 Testing

FraudLense was tested during development across the main application components.

Testing included:

Dataset loading
Model training
Model evaluation
SHAP explanation generation
MySQL connection
Transaction insertion
Prediction storage
Investigation creation
Investigation decision updates
Audit logging
Batch CSV screening
FastAPI startup
Swagger endpoint testing
Streamlit dashboard functionality
Database table display
Investigation page
Audit log page

The complete workflow was exercised during development to verify that the major components work together.

🔒 Security Considerations

The project follows basic security practices for a development environment:

Database passwords are stored in .env
.env is excluded from Git
Dataset files are excluded from Git
Python virtual environment is excluded from Git
Database operations are handled through the backend layer

For a production system, additional security measures would be required, including authentication, authorization, secure secrets management, HTTPS, input validation, monitoring, and database security controls.

⚠️ Current Limitations

FraudLense is currently a portfolio/educational project and has several limitations.

Dataset Dependency

The current model is trained on a specific public credit card fraud dataset.

Real-world financial datasets may contain different:

Features
Data formats
Transaction schemas
Business rules
Fraud patterns

Therefore, the current model cannot simply be applied to every real-world transaction dataset.

Anonymized Features

The V1 to V28 features are anonymized PCA-transformed variables, which limits direct human interpretation.

Static Dataset

The current system works with uploaded CSV transaction data rather than a live banking transaction stream.

Model Monitoring

The current version does not include automated:

Model drift detection
Performance monitoring
Automatic retraining
Authentication

The current application does not implement production-level user authentication or role-based access control.

🚀 Future Improvements

Potential future improvements include:

Natural-language explanations using an LLM
Advanced investigator assistance
Model comparison and hyperparameter tuning
Real-time transaction processing
Model drift detection
Automated model retraining
Authentication and role-based access control
More detailed investigation history
Advanced audit trail features
Production deployment
Support for additional transaction schemas
Automated data ingestion pipelines
Enhanced monitoring and reporting
🎓 Project Purpose

FraudLense was developed to demonstrate the integration of multiple software and machine learning concepts into a single end-to-end application.

The project combines:

Machine Learning
       +
Explainable AI
       +
Database Management
       +
Backend API Development
       +
Dashboard Development
       +
Investigation Workflow

This makes FraudLense more than a standalone machine learning model by connecting model predictions with storage, explainability, investigation, and auditing.

📌 Disclaimer

FraudLense is an educational and portfolio project.

It is not intended to be used as a production financial fraud detection system.

A real-world financial fraud detection system would require extensive validation, security controls, domain-specific feature engineering, model monitoring, regulatory compliance, and testing with appropriate real-world data.

👩‍💻 Author

Srishti

FraudLense is an AI/ML project developed to demonstrate fraud detection, explainable machine learning, database integration, REST API development, and interactive dashboard development.

⭐ Acknowledgements

The project uses publicly available credit card fraud detection data for experimentation and model development.

The machine learning and explainability components are built using open-source Python libraries.