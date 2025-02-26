# Drivers’ Route Optimization Project

## Overview
This project focuses on optimizing drivers' routes in the logistics and merchandise transport sector using data mining techniques. The goal is to improve efficiency by generating data to simulate a fictitious company's standard routes, identifying preferred routes for individual drivers, and creating ideal routes tailored to each driver's preferences. The project leverages clustering, recommendation systems, and frequent itemset mining to achieve these objectives.

## Key Features
1. **Recommended Standard Routes**: Generates a new set of standard routes based on drivers' actual routes, improving adherence to company-provided instructions.
2. **Five Preferred Routes for Each Driver**: Identifies the top five standard routes that each driver is most likely to follow, based on their historical travel patterns.
3. **Ideal Standard Route for Each Driver**: Constructs a personalized standard route for each driver, tailored to their preferences and historical behavior.

## Implementation Details
### 1. **Recommended Standard Routes**
- **Clustering**: Actual routes are clustered using K-Means, with the number of clusters equal to the number of standard routes.
- **Centroid Extraction**: The centroids of each cluster are used to generate recommended standard routes.
- **Evaluation**: The clustering quality is assessed using the Silhouette Coefficient, Davies-Bouldin Index, and Calinski-Harabasz Score. 

### 2. **Five Preferred Routes for Each Driver**
- **Preferences Object**: A `Preferences` object is created for each driver, summarizing their historical actual routes, frequent cities, trips, and merchandise.
- **Similarity Calculation**: The similarity between each standard route and the driver's preferences is computed, and the top five routes with the highest similarity are selected.
- **Evaluation**: The robustness of the method is tested by comparing the results from a training set to those from a test set.

### 3. **Ideal Standard Route for Each Driver**
- **Route Construction**: An ideal route is constructed based on the driver's Preferences, prioritizing frequent trips, cities, and merchandise.
- **Evaluation**: The ideal route is tested by comparing it to the driver's updated preferences after incorporating new data.

## How to Use
Parameters for data generation are defined in the `.env` file and can be modified as needed. To run the code from the main folder, use the following command:
```bash
python src/main.py
```
This will create an *output* folder containing three JSON files with the proposed solutions.

If there is no need to generate new data, one can use the command:
```bash
python src/main.py --generate-data False
```
> **Note**: The code requires the files **actual{run_id}.json** and **standard{run_id}.json** to be present in the data folder. The *run_id* is a parameter defined in the *.env* file. If these files are missing, the program will not run.

To verify the quality of the outputs, one can run the provided test scripts using the following commands. Note that this operation is computationally expensive and will require some time to run succesfully:
```bash
python src/first_test.py
python src/second_test.py
python src/third_test.py
```
For more information about the testing process and results, one can check Section 4 of the attached paper.

## Requirements
- Python 
- Spark
- Java

## Contributors
- Agnese Cervino
- Andrea Leoni
- Enrico Guerriero
- Damiano Zaccaron
