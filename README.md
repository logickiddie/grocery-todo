# Grocery Shopping List App

A simple Streamlit-based app for managing a grocery shopping list with voice input, categories, and purchase tracking.

## Features
- Add items via text or voice input
- Categorize items (e.g., Fruits, Dairy)
- Mark items as purchased
- Search and filter items
- Clear purchased items
- Persistent storage using SQLite

## Installation
1. Install dependencies: `pip install streamlit speechrecognition pyaudio sqlite3`
2. Run the app: `streamlit run app.py`

## Usage
- Enter items separated by spaces and specify a category.
- Use the microphone button for voice input.
- Check off items as done.
- Search to filter the list.
- Clear purchased items with the button.

## Requirements
- Python 3.7+
- Microphone for voice input (optional)
