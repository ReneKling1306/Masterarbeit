# AI Image Licensing Website

## Description

This project was developed as part of a Master's thesis that focuses on creating a new licensing model to give creators more control over how their images are used for AI training. 
It includes a Flask-based web application that provides information about the licences and allows users to select a licence and embed it in the metadata of their images.
In addition, it includes portable software applications for Windows, Linux, and macOS that allow for local license selection and insertion. Furthermore, a simple web scraper has been 
implemented, which accesses a page from the web application, downloads a sample image, displays its metadata and deletes the image based on the embedded licence.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)

## Installation

1. Download the ZIP or clone the repository

```git clone https://github.com/ReneKling1306/Masterarbeit.git```

2. Install python

Download the latest version here:

```https://www.python.org/downloads/```

(Windows): Download from the Microsoft Store

3. Install pip if it isnt already installed

macOS:

```python -m ensurepip --upgrade```
or
```python3 -m ensurepip --upgrade```

Linux (Ubuntu and other Debian derivatives):

```sudo apt-get install python3-pip```

Windows:

```py -m ensurepip --upgrade```

4. Open a terminal and navigate into the project

5. (Optional) Create a virtual environment and activate it:

5.1 (If it isnt already installed)

For Ubuntu or other distros with Apt:

```sudo apt-get install python3-venv```

Windows/macOS:

```pip install virtualenv```
or
```pip3 install virtualenv```

5.2 Create

```python -m venv venv```
or
```python3 -m venv venv```

5.3 Activate:

Windows:

```venv\Scripts\activate```

Linux/macOS:

```source venv/bin/activate```

6. Install the required libraries

```pip install -r requirements.txt```
or
```pip3 install -r requirements.txt```

7. (Additional: Linux) If the Tkinter library is missing:

For Ubuntu or other distros with Apt:

```sudo apt-get install python3-tk```
    
For Fedora:
   
```sudo dnf install python3-tkinter```

8. (Linux and macOS) Change the permission of the exiftool Perl Script:

```chmod +x Webanwendung/ExifTool/Perl_ExifTool/exiftool Softwareanwendung/ExifTool/Perl_ExifTool/exiftool Webscraper/ExifTool/Perl_ExifTool/exiftool```

## Usage

### Web application

1. Navigate to the **Webanwendung** folder and run the following command:

```python app.py```
or
```python3 app.py```

2. Open a browser and navigate to **http://127.0.0.1:5000** 

### Software

1. (When using the script) Navigate to the **Softwareanwendung** folder and run the following command:

On Windows:

```python Windows.py```
or
```python3 Windows.py```

On Linux/macOS:

```python Linux_macOS.py```
or
```python3 Linux_macOS.py```

2. When using the software after downloading it from the web application:

2.1 Software might be classified as malware

On macOS remove quarantine by executing the following command in the terminal:

```xattr -r -d com.apple.quarantine Linux_macOS.app``` 

2.2. (Linux and macOS) Change the permission of the exiftool Perl Script:

Linux:

```chmod +x AII_Licensing_Linux/ExifTool/Perl_ExifTool/exiftool```

macOS:

```chmod +x Linux_macOS.app/Contents/MacOS/ExifTool/Perl_ExifTool/exiftool```

### Webscraper

1. Requires Firefox to be installed on Linux/Windows and Safari on macOS

2. On macOS
   
2.1. Open Safari

2.1. Click on **Safari** in the menu bar and navigate to **Preferences**

2.2. Check the **Show features for web developers** in the Advanced tab

2.3. Access Developer and check the **Allow Remote Automation**
   
3. Start the web application

4. Navigate to the **Webscraper** folder and run the following command:

```python webscraper.py```
or
```python3 webscraper.py```

5. (Firefox) The script might show an eroor message when executed for the first time. It should however work on the second execution.

6. The webscraper will download the image from **http://127.0.0.1:5000/about** and save it as **0.jpg** in the **Images** folder

7. It will then print out the metadata of the images located in **Images** and delete all images without an **Permitted For Training** Licence
