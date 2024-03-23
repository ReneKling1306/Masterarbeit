# AI Image Licensing Website

## Description

This project was developed as part of a Master's thesis that focuses on creating a new licensing model to give creators more control over how their images are used for AI training. 
It includes a Flask-based web application that provides information about the licences and allows users to select a licence and embed it in the metadata of their images.
In addition, it includes portable software applications for Windows, Linux, and macOS that allow for local license selection and insertion.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)

## Installation

1. Download the ZIP or clone the repository

```git clone https://github.com/ReneKling1306/Masterarbeit.git```

2. Open a terminal and navigate into the project

2.(Optional) Create a virtual environment and activate it:

```python -m venv venv```

Windows:

```venv\Scripts\activate```

Linux/macOS:

```source venv/bin/activate```


3. Install the required libraries

```pip install -r requirements.txt```

4. (Additional: Linux) If the Tkinter library is missing:

For Ubuntu or other distros with Apt:

```sudo apt-get install python3-tk```
    
For Fedora:
   
```sudo dnf install python3-tkinter```

5. (Additional: Linux) If the exiftool Perl_Script cannot be executed:

```chmod +x Webanwendung/ExifTool/Perl_ExifTool/exiftool Softwareanwendung/ExifTool/Perl_ExifTool/exiftool Webscraper/ExifTool/Perl_ExifTool/exiftool```

## Usage

### Webanwendung

1. Navigate to the **Webanwendung** folder and run the following command:

```python app.py```

2. Open a browser and got to **http://127.0.0.1:5000** 

### Softwareanwendung

1. Navigate to the **Softwareanwendung** folder and run the following command:

On Windows:

```python Windows.py```

On Linux/macOS:

```python Linux_macOS.py```

### Webscraper

1. Start the Webanwendung

2. Navigate to the **Webscraper** folder and run the following command:

```python webscraper.py```

3. The webscraper will download the image from **http://127.0.0.1:5000/about** and save it as **0.jpg** in the **Images** folder

4. It will then print out the metadata of the images located in **Images** and delete all images without an **Permitted For Training** Licence
