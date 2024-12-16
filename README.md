# Language File Analyzer

This Python script analyzes stalcraft language files (like `.lang` files) to identify changes, count prefixes, and detect empty values.

## Installation

1. **Clone the repository:**
   
bash
   git clone <
2. **Install dependencies:**
   
bash
   pip install -r requirements.txt


## Usage

1.  **Ensure your config.py is setup properly** (if you are using a custom config location or names)
2.  **Make sure that ru.lang is in a location accessible to the script**
3.  Run the script:
   
bash
   python lang_analyzer.py
   The script will find the ru.lang file (or the path you provide in the code) and generate a log file and a dump file in the dump and logs directories respectively.


## Configuration

The script uses a Config class (located in config.py) to define the output directories.  You can modify these paths in the config.py file.


## Contributing

Contributions are welcome! Please open an issue or submit a pull request.