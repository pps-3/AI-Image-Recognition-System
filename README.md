# AI-Image-Recognition-System

# AI Vision Lab - Image Recognition System

AI Vision Lab is a modern web application that uses machine learning to recognize objects in images. The system features a sleek, responsive interface with both light and dark modes, and provides detailed recognition results with confidence scores.

## Features

- **AI-Powered Image Recognition**: Utilizes MobileNetV2 for fast and accurate image classification
- **Modern UI**: Clean, intuitive interface with animations and visual feedback
- **Dark Mode**: Toggle between light and dark themes for comfortable viewing
- **Multiple Predictions**: Shows primary match and alternative possibilities
- **Drag & Drop**: Easy image uploading with drag and drop functionality
- **MongoDB Storage**: Saves images and predictions for future reference

## Technology Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask)
- **AI Model**: TensorFlow with MobileNetV2
- **Database**: MongoDB

## Getting Started

### Prerequisites

- Python 3.8+
- MongoDB
- pip

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/ai-vision-lab.git
   cd ai-vision-lab
   ```

2. Set up the Python virtual environment
   ```bash
   cd backend/flask
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Start MongoDB
   ```bash
   # Start MongoDB service using your system's service manager
   # For example, on macOS with Homebrew:
   brew services start mongodb-community
   ```

4. Run the Flask application
   ```bash
   python app.py
   ```

5. Access the application
   Open your browser and navigate to `http://127.0.0.1:5001/`

## Usage

1. Upload an image by dragging and dropping or clicking the upload area
2. Click "Analyze Image" to process the image
3. View the recognition results, including the primary match and alternatives
4. Toggle between light and dark modes using the button in the top-right corner

## Project Structure

```
ai-vision-lab/
├── backend/
│   └── flask/
│       ├── app.py          # Main Flask application
│       └── venv/           # Python virtual environment
├── frontend/
│   └── index.html         # Frontend interface
└── README.md              # Project documentation
```

## Contributors

- P.Preethi Saran(Team Lead)
- B.Sai Bindu
- V.Venkatesh
- P.Joy Das
