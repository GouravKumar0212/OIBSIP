# Random Password Generator

A desktop application built with Python to generate strong, secure, and customizable random passwords with clipboard integration and session history.

## Overview

This project provides a clean graphical interface to create cryptographically secure passwords. Users can adjust password length using a slider, select different character types (uppercase, lowercase, numbers, symbols), avoid confusing characters, and evaluate password strength.

## Features

- Length Control: Choose any password length from 8 to 32 characters using an interactive slider (minimum 8 characters enforced).
- Character Options:
  - Uppercase letters (A-Z)
  - Lowercase letters (a-z)
  - Numbers (0-9)
  - Special symbols (!@#$%...)
- Diversity Requirement: Enforces selection of at least two character types for security.
- Cryptographically Secure: Uses Python's built-in secrets module instead of standard random numbers.
- Guaranteed Inclusion: Ensures at least one character from each selected character type is present in the final password.
- Exclude Ambiguous Characters: Option to omit easily confused characters such as 0, O, l, 1, and I.
- Strength Indicator: Visual label and color-coded bar showing strength (Weak, Medium, or Strong).
- Clipboard Integration: Automatically copies the generated password to your clipboard upon generation, with an extra button to copy manually.
- Session History: Displays the last 5 generated passwords during the current session. Passwords are stored only in memory and never written to disk for safety.
- Instant Regeneration: Generate as many passwords as you need without closing the application.

## Requirements

- Python 3.x
- pyperclip library

Tkinter and the secrets module are included with standard Python installations.

## Installation

1. Open your terminal or command prompt in the project directory.
2. Install pyperclip if you have not already:

```bash
pip install pyperclip
```

## How to Run

Start the application with:

```bash
python password_generator.py
```

## How to Use

1. Adjust the slider to your desired password length (8 to 32 characters).
2. Check at least two character types you want to include.
3. Check the option to exclude ambiguous characters if desired.
4. Click "Generate Password".
5. The password will appear in the box, the strength bar will update, and the password will be automatically copied to your clipboard.
6. To copy a previous password from the history list, simply click on it.
