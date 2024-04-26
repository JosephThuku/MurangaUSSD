# Muranga County Government USSD System

## Description

This is a USSD system that allows residents of Muranga County to access various services offered by the county government. It is a simplebackend API built using Africa's Talking USSD API and Flask.

The system is part of the requirements for the completion award of Bsc in Information Technology at the Mount Kenya University.

## Features

- User dials the USSD code to access the system
- User can view the services offered by the county government
- User can view the county government officials
- User can pay for services offered by the county government via mpesa

## Technologies

- Python
- Flask
- Africa's Talking USSD API

## Installation

- ensure you have python installed on your machine if not install it from [here](https://www.python.org/downloads/)
- install ngrok from [here](https://ngrok.com/download)
- Clone the repository: `git clone "repository link"`
- move to the project directory: `cd "project directory"`
- Install the requirements: `pip install -r requirements.txt`
- Run the application: `python Muranga.py`
- Run ngrok: `./ngrok http 5000` or `ngrok http 5000`
- Copy the ngrok url and paste it in the Africa's Talking ussd callback url
- copy the ussd code and paste it in the Africa's Talking ussd simulator here: [Africa's Talking USSD Simulator](https://simulator.africastalking.com:9011/)
- Dial the code on the simulator to access the system

## Contrbution
