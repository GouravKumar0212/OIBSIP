# BMI Calculator Application

A simple desktop application built with Python to calculate Body Mass Index (BMI), check health categories, save records for different users, and track BMI trends over time.

## Overview

This project calculates BMI based on a user's weight in kilograms and height in meters. It provides instant feedback with color-coded categories, stores past calculations locally in an SQLite database, and allows users to view their progress on a line graph.

## Features

- Accurate BMI Calculation: Uses the standard formula (weight / height squared) and rounds the result to two decimal places.
- Health Categories:
  - Underweight: Less than 18.5
  - Normal weight: 18.5 to 24.9
  - Overweight: 25.0 to 29.9
  - Obese: 30.0 and above
- Color Feedback: Visual color indicators for each category (Blue for Underweight, Green for Normal, Orange for Overweight, Red for Obese).
- Input Validation: Checks for valid numbers and prevents zero or negative values.
- Multi-User Support: Stores records for different user names with timestamps.
- Database Storage: Automatically saves records into a local SQLite database file (bmi_records.db).
- History Management:
  - View full history or search by user name.
  - Delete individual selected records.
  - Delete all records at once with confirmation.
- Trend Chart: Displays a line graph showing BMI changes over time using Matplotlib.

## Requirements

- Python 3.x
- Matplotlib library

The GUI (Tkinter) and database (SQLite3) come pre-installed with standard Python.

## Installation

1. Clone or download this project folder to your computer.
2. Open your terminal or command prompt in the project directory.
3. Install matplotlib if you do not have it installed:

```bash
pip install matplotlib
```

## How to Run

Run the application using the following command:

```bash
python bmi_calculator.py
```

## How to Use

1. Enter your name in the User Name field.
2. Enter your weight in kilograms (for example: 70).
3. Enter your height in meters (for example: 1.75).
4. Click "Calculate BMI" to see your BMI value and category. The record will be saved automatically.
5. Click "View History" to see past records in a table.
6. Click "View Trend" to see your BMI progress graph over time.
7. Click "Clear" to reset the input fields.
8. Click "Delete History" if you want to remove saved records.
