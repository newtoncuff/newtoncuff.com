# Flask Resume Site

This is a simple single-page website built with Flask that serves as a personal resume. It showcases the user's skills, experience, and education in a clean and responsive layout.

## Project Structure

```
flask-resume-site
├── app.py
├── config.py
├── static
│   ├── css
│   │   └── style.css
│   └── js
│       └── main.js
├── templates
│   ├── base.html
│   └── index.html
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd flask-resume-site
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. **Install the required packages:**
   ```
   pip install -r requirements.txt
   ```

5. **Run the application:**
   ```
   python app.py
   ```

6. **Open your browser and go to:**
   ```
   http://127.0.0.1:5000
   ```

## Features

- Responsive design that works on both desktop and mobile devices.
- Clean layout to effectively present resume information.
- Easy to customize and extend with additional features.

## License

This project is licensed under the MIT License - see the LICENSE file for details.