# Shape Regularization and Symmetry Detection

## Overview
This project is part of the Adobe Gensolve Hackathon, focusing on shape regularization and symmetry detection. The goal is to process a set of shapes provided in CSV files, detect and regularize various geometric shapes, implement symmetry detection, and perform gap completion. The processed shapes can be visualized using Streamlit and downloaded as CSV or SVG files.

## Features
- **Shape Detection and Regularization**: Identify and regularize shapes including straight lines, circles, ellipses, rectangles, regular polygons, and star shapes.
- **Symmetry Detection**: Detect and highlight symmetrical properties of shapes.
- **Gap Completion**: Complete missing parts of shapes to restore their original form.
- **Visualization**: Use Streamlit to visualize the shapes before and after processing.
- **Download Options**: Save the processed shapes as CSV or SVG files.

## Setup and Installation
1. **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Set Up a Virtual Environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install Required Packages**
    ```bash
    pip install -r requirements.txt
    ```

## Usage
1. **Run the Streamlit Application**
    ```bash
    streamlit run app.py
    ```

2. **Upload CSV File**
   - Use the `st.file_uploader` widget in the Streamlit app to upload your CSV file containing shape data.

3. **Process Shapes**
   - The uploaded shapes will be processed for regularization and symmetry detection.
   - You can visualize the processed shapes directly in the Streamlit app.

4. **Download Processed Shapes**
   - Download the processed shapes as CSV or SVG files from the Streamlit app interface.

## Project Structure
```
|-- app.py                  # Main Streamlit application file
|-- shape_processing.py     # Core shape processing logic
|-- symmetry_detection.py   # Symmetry detection module
|-- gap_completion.py       # Gap completion module
|-- utils.py                # Utility functions
|-- requirements.txt        # Python dependencies
|-- README.md               # Project documentation
```

## Key Points
- Ensure unique keys for `st.file_uploader` to avoid DuplicateWidgetID errors.
- Handle SVG saving functionality correctly.
- Follow correct file navigation, virtual environment setup, and package installation procedures.
- Focus on correctly processing shapes based on the problem statement provided in `Curvetopia1.pdf` and `problems.zip`.

## Requirements
- Python 3.7 or higher
- Streamlit
- NumPy
- pandas
- Matplotlib
- SVGwrite

## Contributing
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and push to your branch.
4. Create a Pull Request to the main branch.

