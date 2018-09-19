# CZ4045---NLP
Project assignment for NTU CZ4045 Natural Language Processing

## Version information
- Python 3.6


## Contents
- [Placing dataset files](placing-dataset-files)
- [Project Installation Guide](project-installation-guide)
- [Usage guide](usage-guide)


## Placing dataset files
The review dataset file are omitted to save space in project directory. Please place your `CellPhoneReview.json` dataset file in the `dataset/` folder.

## Project Installation Guide
Project setup is as simple as the following 2 steps 
#### 1. Install package requirements
The following command will install the required python packages.
```
        $ pip install -r requirements.txt
```

#### 2. Run migrations to create the sqlite3 database
The purpose of using the database instead of operating directly on the `.json` is to speed up retrieval and query of the dataset. Execute the following command to create the database.
```
        $ python manage.py migrate
```

## Usage guide
This section describes the steps or commands needed for running the code that solves the problems listed in the project assignment.
#### Populate the database
The project uses sqlite3 db engine. Once the sqlite3 database has been created and the `CellPhoneReview.json` placed in the `dataset/` folder, execute the following command to populate the sqlite3 database with amazon review records.
```
        $ python main.py initdb
``` 
