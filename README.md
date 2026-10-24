
# Global Airport Explorer

An interactive airport data analytics dashboard built with
Python, Pandas, Plotly and Streamlit.

## Features

- Interactive airport metrics
- Country and airport-type filters
- Search by airport name, city, or code
- Interactive charts
- Downloadable filtered CSV data
- Airport map (when verified coordinates are available)

## Technology Stack

- Python
- Pandas
- Plotly
- Streamlit

## Run Locally

1. Create and activate your Python environment.
2. Install dependencies:

   pip install -r requirements.txt

3. Run the application:

   streamlit run app.py

## Project Structure

airport-analytics-portfolio/
├── app.py
├── requirements.txt
├── README.md
└── data/
    └── airports.csv

## Data Limitations

The dashboard summarizes the supplied dataset. Its
record counts should not be interpreted as a complete
global airport inventory unless the source is verified
as complete and up to date.
