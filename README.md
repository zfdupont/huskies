# Gerrymandering Analyzer

Huskies is a Redistricting Analyzer that processes state census data, generates new redistricting plans, and serves them to users over an HTTP server. This tool aims to facilitate the analysis and creation of fair and effective redistricting plans.

## Features

- **Data Processing:** Ingests state census data detailing census plans.
- **Plan Generation:** Generates new redistricting plans based on the provided census data.
- **HTTP Server:** Serves the generated plans and ensemble summaries to users through an HTTP interface.

## Table of Contents

- [Repository Structure](#repository-structure)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Plan Generation](#plan-generation)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Repository Structure

The repository is divided into two main sections:

1. **server:** Contains a Spring HTTP server that serves plans and ensemble summaries from the database. It performs no calculations.
2. **scripts:** Handles all the calculations, generates new plans, and makes POST requests to the database after generating plans.

## Installation

To get started with Huskies, follow these steps:

1. **Clone the repository:**
   ```
   git clone https://github.com/zfdupont/huskies.git
   cd huskies
   ```

2. **Install dependencies:**
   - For the server:
     ```
     cd server
     ./mvnw install
     ```

   - For the scripts:
     ```
     cd scripts
     pip install -r requirements.txt
     ```

3. **Run the server:**
   ```
   cd server
   ./mvnw spring-boot:run
   ```

4. **Run the scripts:**
   ```
   cd scripts
   python main.py
   ```

## Usage

Once the server is running, it will be accessible at `http://localhost:8000`. You can interact with the server using the provided API endpoints.

## API Endpoints
### GET /summary
Retrieve the ensemble summary for a specified state.

#### Request
```
GET /summary?state=StateName
```

#### Response
```
{
  "ensemble_summary": {
    "metric1": value1,
    "metric2": value2,
    ...
  },
  "winner_split": {
    "party1": count1,
    "party2": count2,
    ...
  },
  "box_whiskers_data": {...},
  "incumbent_data": {...}
}
```

### GET /plans
Retrieve all generated plans.

#### Response
```
[
  {
    "id": "plan_id_1",
    "name": "Plan 1",
    "state": "StateName",
    "geoJson": {
      ...
    }
  },
  ...
]
```

### POST /plans
Add a new redistricting plan to the server.

#### Request Body
```
{
  "name": "New Plan",
  "state": "StateName",
  "geoJson": {
    ...
  }
}
```

#### Response
```
{
  "id": "new_plan_id",
  "name": "New Plan",
  "state": "StateName",
  "geoJson": {
    ...
  }
}
```

## Plan Generation
To create district plans, we make use of GerryChain.
GerryChain utilizes Markov Chain Monte Carlo (MCMC) methods to explore the space of possible redistricting plans. The core components involved are:

#### Graph Representation
The state is represented as a graph where nodes correspond to geographic units (e.g., census blocks) and edges represent adjacencies between them. This graph is loaded from a JSON file.

#### Initial Partition
An initial redistricting plan is used as a starting point for the chain. This partition is based on existing district assignments.

#### Proposal Mechanism (ReCom)
The ReCom (Recursive Division) method is used to propose new districting plans. It merges adjacent districts and then re-divides them to form new districts while maintaining population balance and geographical contiguity.

#### Constraints
Constraints ensure the generated plans meet specific criteria such as population balance within districts and geographical compactness.

- **Population Constraint:** Ensures each district's population is within ±5% (`POP_PERCENT_ALLOWED = 0.05`) of the ideal population.
- **Compactness Constraint:** Ensures geographical compactness by limiting the number of cut edges to twice (`CUT_EDGES_MULTIPLIER = 2`) the initial number of cut edges.

#### Markov Chain
The Markov Chain iteratively moves from one plan to another by accepting or rejecting proposed plans based on the defined constraints. This process generates an ensemble of plans that can be analyzed for fairness and compliance with redistricting principles.

#### Ensemble Analysis
The generated ensemble of plans allows for statistical analysis to understand the properties and biases of different redistricting plans, aiding in the evaluation of their fairness.

### Explanation of Constants and Functions

#### Constants
- **POP_PERCENT_ALLOWED:** The allowable deviation from the ideal population for each district, set to 5%.
- **NODE_REPEATS:** The number of times to repeat the process of node selection in the ReCom proposal, set to 2.
- **CUT_EDGES_MULTIPLIER:** The multiplier for the initial number of cut edges to enforce compactness, set to 2.

## Configuration

The server can be configured using the `application.properties` file for the Spring server and a `.env` file for the scripts. Below is an example configuration:

### application.properties (Spring server)
```
server.port=8000
logging.level.root=INFO
```

### .env (scripts)
```
DATABASE_URI="your_database_url",
HUSKIES_HOME="path/to/scripts"
```

- `server.port`: Port on which the Spring server will run.
- `logging.level.root`: Logging level for the Spring server.
- `DATABASE_URI`: URL of the database to which the scripts will POST data.
- `HUSKIES_HOME`: Directory where census data and generated plans will be stored.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
