# itmo-dev: Elderly People Safety App 🌟

Welcome to the itmo-dev repository, home of the Elderly People Safety App. This project aims to enhance the safety of elderly individuals through a comprehensive application leveraging machine learning models and various cutting-edge technologies.

## Project Features 🚀

- **🔒 SSL Certificates:** The project ensures secure communication through SSL certificates.
- **🛡️ DDoS Protection:** Implemented protection against DDoS attacks using rate limiting.
- **⚙️ Asynchronous Queues:** Utilizes asynchronous queues with the ARQ library for efficient task handling.
- **📊 Data Visualization:** Employs Streamlit for data visualization, making insights accessible and understandable.
- **🌐 Microservices Architecture:** The project follows a microservices architecture for scalability and maintainability.
- **💳 Billing:** deduction of credits for forecasts, different cost of models, 100 free credits for registration

## Demo and Documentation 📚

- **Demo:** Check out the live demo [here](https://karouniform.xyz:8501/).
- **API Documentation:** Explore the API documentation [here](https://karouniform.xyz:8080/docs).

## Machine Learning Models 🤖

The following machine learning models were developed:

1. **LightGBM Model:** Metric - 0.79
2. **Decision Tree Model:** Metric - 0.82
3. **Logistic Regression Model:** Metric - 0.836

Detailed results of the research are available in the `research_result` folder.

## Getting Started 🛠️

### Prerequisites

- [Docker](https://www.docker.com/get-started)


### Running the Project ▶️

1. Clone the repository:

   ```bash
   git clone https://github.com/KaroUniform/itmo-dev
   cd itmo-dev
   ```
2. Build and run the project using Docker Compose:
   ```
   sudo docker-compose up
   ```

### Scaling 📈
You can scale the project by adjusting the number of workers and API instances:

Scale worker (adjust the value of N):
```bash
sudo docker-compose up --scale worker=N
```
Scale API in **gunicorn_conf.py** (adjust the value of N):
```python
workers = N
```
Or *⚠️(Not recommended, not tested)* :
```
sudo docker-compose up --scale api=N
```

## 🌐 Database schema 

### users

| Column   | Type  | Constraints               |
|----------|-------|---------------------------|
| id       | UUID  | Primary Key               |
| balance  | Float | Default: 0                |

### transaction_history

| Column      | Type         | Constraints                                      |
|-------------|--------------|--------------------------------------------------|
| job_id      | UUID         | Primary Key, Index                               |
| user_id     | UUID         | Foreign Key (users.id)                           |
| amount      | Integer      | Not Null                                         |
| model_id    | Integer      | Foreign Key (ml_models.id), Nullable             |
| result      | JSON         | Nullable                                         |
| status      | Enum         | Default: IN_PROGRESS                             |
| err_reason  | String(512)  | Nullable                                         |
| timestamp   | DateTime     | Server Default: func.now()                       |

### ml_models

| Column      | Type    | Constraints               |
|-------------|---------|---------------------------|
| id          | Integer | Primary Key, Index         |
| model_name  | String  | Unique                    |
| model_cost  | Float   |                           |

### Triggers
1. After Insert on transaction_history Table:

* This trigger is executed after a new record is inserted into the transaction_history table.
* It asynchronously fetches the associated user and updates their balance by adding the transaction amount.

2. Before Update on transaction_history Table:

* This trigger is executed before an update operation on the transaction_history table.
* If the transaction status is marked as FAILURE, it asynchronously retrieves the associated user.
* It checks for the change in status to FAILURE and, if detected, refunds the user by adding the absolute amount of the transaction to their balance.
* Additionally, it updates the transaction amount to zero in the transaction_history table.

3. After Insert on users Table:

* This trigger is executed after a new user is inserted into the users table.
* It creates a new transaction record with a predefined amount, status, and result for the user.
* The new transaction is then added to the database asynchronously.