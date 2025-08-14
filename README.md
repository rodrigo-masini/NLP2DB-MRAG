# NLP2DB: QA Database Interactions with MAGIC's Private AI Technology
 
<div align="center">
  <p>
    <a href="https://github.com/rodrigo-masini/NLP2DB-MRAG">
    </a>
    <a href="https://github.com/rodrigo-masini/NLP2DB-MRAG">
    </a>
  </p>

</div>

## What is NLP2DB-MRAG?

As large models are released and iterated upon, they are becoming increasingly intelligent. However, in the process of using large models, we face significant challenges in data security and privacy. We need to ensure that our sensitive data and environments remain completely controlled and avoid any data privacy leaks or security risks. Based on this, we have launched the NLP2DB-MRAG project to build a complete private large model solution for all database-based scenarios. This solution allowins to be applied in Fabric-Hypergrid private environments, ensuring that the ability of large models is absolutely private, secure, and controllable.

NLP2DB-MRAG is an experimental open-source project that uses Fabric Hypergrid large models to interact with your data and environment. With this solution, you can be assured that there is no risk of data leakage, and your data is 100% private and secure.

## Features

Currently, we have released multiple key features, which are listed below to demonstrate our current capabilities:

- SQL language capabilities
  - SQL generation
  - SQL diagnosis
- Private domain Q&A and data processing
  -  Database knowledge Q&A
  - Data processing
- Plugins
  -  Support custom plugin execution tasks and natively support the Auto-GPT plugin, such as:
    - Automatic execution of SQL and retrieval of query results
    - Automatic crawling and learning of knowledge
- Unified vector storage/indexing of knowledge base
  - Support for unstructured data such as PDF, TXT, Markdown, CSV, DOC, PPT, and WebURL

- Milti LLMs Support
  - Supports multiple large language models, currently supporting Vicuna (7b, 13b), ChatGLM-6b (int4, int8), guanaco(7b,13b,33b), Gorilla(7b,13b)
  - TODO: codegen2, codet5p


## Introduction 
NLP2DB-MRAG provide private domain knowledge base question-answering capability through ou AI platform Fabric Hypergid. Furthermore, we also provide support for additional plugins.

The core capabilities mainly consist of the following parts:
1. Knowledge base capability: Supports private domain knowledge base question-answering capability.
2. Large-scale model management capability: Provides a large model operating environment based on Fabric Hypergrid.
3. Unified data vector storage and indexing: Provides a uniform way to store and index various data types.
4. Connection module: Used to connect different modules and data sources to achieve data flow and interaction.
5. Agent and plugins: Provides Agent and plugin mechanisms, allowing users to customize and enhance the system's behavior.
6. Prompt generation and optimization: Automatically generates high-quality prompts and optimizes them to improve system response efficiency.
7. Multi-platform product interface: Supports various client products, such as web, mobile applications, and desktop applications.

## Usage Instructions

Configure Environment VariablesCreate a .env file in the project root with your TELA credentials:bash# 🔐 TELA API Configuration
TELA_API_KEY="tela_sk_xxxxxxxxxxxxxxxxxxxxxxxx"        # Your TELA API key
TELA_API_BASE_URL="https://api.telaos.com/v1"          # TELA API endpoint (default)
TELA_PROJECT="proj_xxxxxxxxxxxxxxxx"                    # Your project ID
TELA_ORG="org_xxxxxxxxxxxxxxxx"                        # Your organization ID

### 🤖 Model Selection
TELA_MODEL="qwen-3-235b-a22b-instruct"                 # Primary LLM model
TELA_EMBEDDING_MODEL="nomic-ai/nomic-embed-text-v1.5"  # Embedding model for vector search

### 🗄️ Database Configuration
LOCAL_DB_HOST=localhost                                 # Use 'mysql' for Docker
LOCAL_DB_PORT=3306
LOCAL_DB_USER=root
LOCAL_DB_PASSWORD=your_secure_password

### ⚙️ Application Settings
WEB_SERVER_PORT=7860
DEBUG_MODE=False
LANGUAGE=en                                             

### Create your .env file with TELA credentials
cp .env.example .env

### Edit .env with your TELA credentials

### Start everything with one command
docker-compose up -d

### View logs
docker-compose logs -f

### Access the application
open http://localhost:7860Docker Compose will:

Start a MySQL container with sample data
Build and run the DB-GPT application
Handle all networking between services
Persist data across restarts
Option 2: Local Development 🖥️For development or custom setups:bash# Clone the repository
git clone https://github.com/your-repo/db-gpt-tela.git
cd db-gpt-tela

### Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

### Install dependencies
pip install -r requirements.txt

### Download required NLTK language models
python -m spacy download en_core_web_sm

### Configure environment
cp .env.example .env
### Edit .env with your credentials

### Ensure MySQL is running locally
#### Import sample data (optional)
mysql -u root -p < sample_data/init.sql

### Run the application
python run.py

### Access the application
open http://localhost:7860🎯 How to Use1. Select Your Database

Use the left sidebar to choose from available databases
The system automatically loads schema information
2. Choose SQL Mode

Direct Execute: Generates and runs SQL automatically
SQL Q&A: Generates SQL without execution (preview mode)
3. Ask Questions in Natural LanguageExamples of queries you can ask:text💬 "Show me all users who registered last month"
→ SELECT * FROM users WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 MONTH)

💬 "What's the total revenue by product category?"
→ SELECT category, SUM(revenue) as total_revenue 
  FROM products GROUP BY category

💬 "Find customers with more than 5 orders"
→ SELECT c.*, COUNT(o.id) as order_count 
  FROM customers c 
  JOIN orders o ON c.id = o.customer_id 
  GROUP BY c.id 
  HAVING order_count > 5

💬 "List the top 10 best-selling products this year"
→ Complex query with JOINs and aggregations4. Adjust Parameters

Temperature: Controls creativity (0.0 = deterministic, 1.0 = creative)
Max Tokens: Maximum response length
🔧 Advanced ConfigurationUsing Different TELA ModelsTELA offers various models optimized for different use cases:bash# For complex analytical queries (recommended)
TELA_MODEL="qwen-3-235b-a22b-instruct"

### For faster responses with good accuracy
TELA_MODEL="qwen-2.5-72b-instruct"

### For cost-effective simple queries
TELA_MODEL="qwen-2.5-32b-instruct"Connecting to Remote MySQLbash# For cloud databases (AWS RDS, Google Cloud SQL, etc.)
LOCAL_DB_HOST=your-database.region.rds.amazonaws.com
LOCAL_DB_PORT=3306
LOCAL_DB_USER=admin
LOCAL_DB_PASSWORD=your_secure_passwordEnabling Debug ModeFor development and troubleshooting:bashDEBUG_MODE=True  # Enables detailed logging🛠️ TroubleshootingCommon Issues and Solutions1. TELA API Authentication Error
Error: Invalid API key or unauthorized access
Solution: Verify your TELA_API_KEY and ensure it's active in the TELA dashboard.2. Database Connection Failed
Error: Can't connect to MySQL server
Solution:

Check MySQL is running: docker ps or systemctl status mysql
Verify credentials in .env
For Docker, use LOCAL_DB_HOST=mysql instead of localhost
3. Model Not Available
Error: Model 'qwen-3-235b-a22b-instruct' not found
Solution: Check available models in your TELA project settings or contact support for access.4. Rate Limiting
Error: Rate limit exceeded
Solution: TELA has request limits based on your plan. Consider:

Upgrading your TELA plan
Implementing request caching
Using batch operations
📊 Sample DatabasesThe project includes sample database schemas for testing:sql-- Users table
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    product_name VARCHAR(100),
    amount DECIMAL(10,2),
    order_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Products table
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10,2),
    stock_quantity INT
);🚦 API Rate Limits & Best PracticesTELA API LimitsPlanRequests/MinTokens/DayConcurrent RequestsFree10100K1Starter601M5Pro30010M20EnterpriseCustomCustomCustomBest Practices
Cache Frequently Used Queries: Store common query results
Use Appropriate Models: Don't use 235B model for simple queries
Batch Operations: Group similar queries when possible
Monitor Usage: Track API usage in TELA dashboard
Implement Retry Logic: Handle transient failures gracefully

We currently support many document formats: txt, pdf, md, html, doc, ppt, and url.
before execution:
TBD
## Licence

The MIT License (MIT)

## Contact Information
TBD

