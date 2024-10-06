# QML-Toolbox
A toolbox that analyses loss landscapes by combining metrics, ansatz characteristics and ZX-calculus

## Dependencies
The code contained in this repository requires the following dependencies:
- matplotlib==3.5.2
- networkx==2.8.8
- numpy==1.24.1
- orqviz==0.5.0
- PennyLane==0.27.0
- scipy==1.13.1
- torch==2.0.0

Install dependencies using ``pip install -r requirements.txt``  
Python 3.9.13 is the version compatible with the dependencies.

## Docker
Steps to be performed to run the application using docker.

> Prerequisites: Installed docker and docker compose.
  On Windows you can easily install Docker Desktop, which includes both.

Start the corresponding container by executing:
```
docker compose up
```

If changes were made, execute:
```
docker compose up --build
```
