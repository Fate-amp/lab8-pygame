# Lab 8 - Pygame Random Squares

This project runs a simple Pygame animation that displays 10 colored squares moving randomly and bouncing inside the window.

## Setup (Windows PowerShell)

1. Create the virtual environment:

   python -m venv .venv

2. Activate the virtual environment:

   .\.venv\Scripts\Activate.ps1

3. Install dependencies:

   pip install -r requirements.txt

## Run the App

python main.py

## Notes

- The dependency in requirements.txt is pygame-ce because your current Python version is 3.14, and pygame-ce provides compatible wheels.
- The app code imports pygame normally, so no code changes are needed for this compatibility choice.
