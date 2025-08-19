# 🤖 Friday AI Assistant

A powerful AI assistant that combines voice commands, web interface, and Botpress webchat integration. Friday can control your system, solve math problems, generate code, manage databases, and more!

## ✨ Features

- 🎤 **Voice Commands**: Control system applications and settings
- 🧮 **Math Solver**: Solve complex mathematical expressions
- 💻 **Code Generator**: Generate Python code from descriptions
- 🗄️ **Database Management**: Create and manage MySQL databases
- 🔍 **Web Search**: Search the internet for information
- 🤖 **AI Chat**: Intelligent conversations with Gemini AI
- 🌐 **Web Interface**: Beautiful, responsive web UI
- 💬 **Botpress Webchat**: Integrated chat widget for easy interaction

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- MySQL Server (optional, for database features)
- Microphone (for voice commands)

### Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your Gemini API key** (optional but recommended):
   ```bash
   # Windows
   set GEMINI_API_KEY=your_api_key_here
   
   # Or edit the backend.py file directly
   ```

4. **Configure MySQL** (optional):
   - Edit `backend.py` and update the `MYSQL_CONFIG` section
   - Set your MySQL username, password, and database name

### Running the Application

1. **Start the web server**:
   ```bash
   python backend.py
   ```

2. **Open your browser** and go to:
   ```
   http://localhost:5000
   ```

3. **Use the chat widget** in the bottom right corner to interact with Friday!

## 💬 How to Use the Botpress Webchat

The Botpress webchat widget is already integrated into your web interface. Here's how it works:

### Chat Commands

- **System Control**: "open chrome", "close notepad", "volume up", "mute"
- **Math Problems**: "solve 15 + 27 x 3", "calculate 2^10"
- **Code Generation**: "generate code for a calculator", "write a program to sort a list"
- **Database Operations**: "create a database for students", "run query SELECT * FROM users"
- **General Questions**: Ask anything and Friday will use Gemini AI to help!

### Example Conversations

```
You: "Solve 25 x 4 + 10"
Friday: "The answer is 110"

You: "Generate code for a simple calculator"
Friday: "Here's a Python calculator program..." [code output]

You: "Open Notepad"
Friday: "Opening Notepad"

You: "Create a database for employees"
Friday: "Creating database 'friday_employees' with appropriate table structure..."
```

## 🛠️ Configuration

### Gemini AI Setup

1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set it as an environment variable or edit `backend.py`

### MySQL Setup (Optional)

1. Install MySQL Server
2. Create a user and database
3. Update the `MYSQL_CONFIG` in `backend.py`

### Voice Commands

The voice recognition features require:
- A working microphone
- PyAudio (included in requirements.txt)
- Internet connection for Google Speech Recognition

## 📁 Project Structure

```
hackathon project/
├── backend.py          # Flask server with Friday AI logic
├── templates/
│   └── index.html     # Web interface with Botpress widget
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🔧 Troubleshooting

### Common Issues

1. **"No module named 'flask'"**
   - Run: `pip install -r requirements.txt`

2. **Voice recognition not working**
   - Check microphone permissions
   - Ensure PyAudio is installed correctly

3. **MySQL connection errors**
   - Verify MySQL server is running
   - Check credentials in `backend.py`

4. **Botpress widget not loading**
   - Check internet connection
   - Verify the script URLs are accessible

### Getting Help

- Check the console output for error messages
- Ensure all dependencies are installed
- Verify your API keys are correct

## 🌟 Advanced Usage

### Custom Commands

You can extend Friday's capabilities by adding new functions in `backend.py`:

```python
def custom_function(command):
    # Your custom logic here
    return "Custom response"

# Add to the chat route
elif "custom" in user_message:
    response = custom_function(user_message)
```

### Styling the Webchat

The Botpress widget can be customized by modifying the CSS in `templates/index.html`.

### API Endpoints

- `GET /` - Main web interface
- `POST /api/chat` - Chat endpoint for processing messages
- `GET /api/status` - System status and capabilities

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve Friday AI!

---

**Happy coding with Friday AI! 🚀**
