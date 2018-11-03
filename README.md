# CZ4045---NLP
Project assignment for NTU CZ4045 Natural Language Processing

## Version information
- Python 3.6


## Contents
- [Placing dataset files](#placing-dataset-files)
- [Project Installation Guide](#project-installation-guide)
- [Usage guide](#usage-guide)


## Placing dataset files
The review dataset file are omitted to save space in project directory. Please place your `CellPhoneReview.json` dataset file in the `dataset/` folder.

## Project Installation Guide
Project setup is as simple as the following 2 steps
#### 1. Install package requirements
The following command will install the required python packages.
```
$ pip install -r requirements.txt
```

#### 2. Download NLTK models
The following NLTK models need to be downloaded to run some of the features provided by the `NLTK` i.e. `pos tagging`. Run the following codes on a python interpreter.
```
>>> import nltk
>>> nltk.download('punkt')
>>> nltk.download('averaged_perceptron_tagger')
>>> nltk.download('wordnet')
```

## Usage guide
This section describes the steps or commands needed for running the code that solves the problems listed in the project assignment. Please ensure the `CellPhoneReview.json` has been placed in the `dataset/` folder before using any of the commands.

#### 1. Dataset Analysis
Execute the following command in `command prompt` to start Dataset Analysis. A trace sample is available [here](results/Dataset%20Analysis/trace.txt)
```
$ python main.py analysis
``` 

#### 2. Noun Phrase Summarizer


#### 3. Sentiment Word Detection
Execute the following command in `command prompt` to start generating the top 20 positive and negative words.
```
$ python main.py sentiment
``` 
A trace sample is available [here](results/sentiment_word_detection/trace.txt). Please note that the actual console output will differ somewhat from the `trace.txt` file as the file does not include console output for printing progress such as `1000 of 190,000 done`.

#### 4. Application
