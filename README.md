# Mental Palace - AI Mental Health Companion

## 📌 Overview
**Mental Palace** is an AI-powered mental health companion designed to provide a safe and non-judgmental space for users to express their thoughts, reflect on their emotions, and receive personalized, empathetic responses. It features multiple AI personas that adapt to different mental health support styles, from compassionate listening to cognitive behavioral therapy (CBT) guidance.

---

## 🚀 Features
- **User Authentication**: Secure login and registration system.
- **Chat Sessions**: Users can create, rename, and delete chat sessions.
- **Memory & Personalization**: AI remembers previous conversations for a personalized experience.
- **Multiple Personas**:
  - **Mental Palace Counselor**: Balanced, structured, and supportive.
  - **Compassionate Listener**: Focuses on deep empathy and validation.
  - **Motivational Coach**: Encourages action and positive reinforcement.
  - **CBT Guide**: Helps users reframe negative thoughts using cognitive behavioral techniques.
- **Secure Database**: Uses SQLite for storing users, sessions, and chat histories.
- **Log Out Functionality**: Ensures secure session handling.
- **Streamlit UI**: A clean, modern, and user-friendly interface for seamless interaction.

---

## 🛠️ Dependencies
The following Python packages are required to run the project:

```plaintext
streamlit==1.42.2
langchain==0.3.19
langchain-community==0.3.18
langchain-core==0.3.37
langchain-google-genai==2.0.10
google-generativeai==0.8.4
google-ai-generativelanguage==0.6.15
python-dotenv==1.0.1
sqlite3 (built-in)
```

To install all dependencies, run:
```sh
pip install -r requirements.txt
```

---

## 💻 Installation & Setup

### 1️⃣ Clone the Repository
```sh
git clone https://github.com/your-username/MentalPalace.git
cd MentalPalace
```

### 2️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

### 3️⃣ Set Up Environment Variables
Create a `.env` file in the root directory and add your Gemini API key:
```plaintext
GEMINI_API_KEY=your_google_api_key_here
```

### 4️⃣ Run the Application
```sh
streamlit run app.py
```

### 5️⃣ Access the Application
After running the above command, visit:
- **Localhost**: [http://localhost:8501](http://localhost:8501)
- **Network URL** (for external access): Check your terminal output

---

## 🏗️ Project Structure
```plaintext
MentalPalace/
│── database.py      # Handles SQLite operations
│── auth.py          # Manages user authentication
│── chatbot.py       # AI chatbot logic and memory system
│── app.py           # Main Streamlit app
│── .env             # Stores environment variables (API keys)
│── requirements.txt # Lists all dependencies
│── README.md        # Documentation file
└── img/             # Stores logos and images
```

---

## 🤖 How It Works
1. **Log in or Register** to create an account.
2. Choose an **AI Persona** that fits your needs.
3. Start a **new chat** or select a previous session.
4. **Interact** with the AI in a safe and supportive environment.
5. Log out securely when finished.

---

## 🛠️ Contributing
1. Fork the repository 🍴
2. Create your feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add new feature'`
4. Push to the branch: `git push origin feature-name`
5. Open a pull request ✅