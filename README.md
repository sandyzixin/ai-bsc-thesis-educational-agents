# AI BSc Thesis LLM-driven Retrieval-Augmented Educational Conversational Agents

This repository contains code and analysis materials for my BSc Artificial Intelligence thesis on LLM-driven retrieval-augmented educational conversational agents. This project compares two different interaction formats: a text-based chatbot and a speech-enabled embodied virtual human. 

## Project Overview

The project investigates whether the interaction format of an educational conversational agent influences students' perceived learning experience. Both agents use the same LLM-driven Retrieval-Augmented Generation (RAG) backend, but differ in their interaction format. Additionally, it also investigates to what extent students are willing to use such agents in practice.

The repository includes the following:

* the chatbot code
* the Japan politics context document used by the shared RAG system
* the data analysis notebook
* documenntation of files and components that are not included

## Private Components

The full Unity project, the shared RAG implementation and some other code files are not included in this repository. These components are excluded either for security reasons, such as files containing API keys or private configuration settings, or because they were provided by the supervisor and are not my own code to share publicly.

## Data Analysis Notebook

The analysis notebook is located in: ``analysis/analysis.ipynb``

Before publishing, the notebook outputs were cleared to prevent accidental sharing of private data, local file paths, or identifiable information.

### Data Availability

The original study data are not included in this repository due to privacy and ethical considerations. The analysis notebook is provided, but it cannot be run without access to the private dataset.

## Requirements

The required Python packages are listed in: ``requirements.txt``

To install the required packages, run:

```bash
pip install -r requirements.txt
```

## Notes on Reproducibility

This repository is intended to support my thesis by documenting the code structure and data analysis. However, full reproduction of the study results is not possible from this repository alone due to privacy and ethical reasons.