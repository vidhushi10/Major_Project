 - AI Assistant Chatbot

An intelligent, LLM-powered Hiring Assistant chatbot built using **Streamlit** and **Mistral (via Ollama)**. This chatbot is designed for initial candidate screening at a fictional recruitment agency called **TalentScout**, specializing in technology placements.

> 💡 The chatbot collects candidate information, generates technical questions based on their tech stack, and maintains conversation flow contextually using prompt engineering.

---

## 🚀 Features

- 👋 Welcomes candidates and explains its role
- 📩 Collects key candidate details:
  - Full Name, Email, Phone Number
  - Years of Experience
  - Desired Role(s)
  - Current Location
  - Tech Stack
- ⚙️ Generates **3–5 technical questions per tech skill**
- 🧠 Maintains context across interactions
- 🛡️ Fallback mechanism for invalid inputs
- 🎯 Ends conversation gracefully
- 💅 Stylish chat-like UI with emojis and interactive elements
- ✅ Local deployment with optional cloud demo

---

## 🖼️ Demo

https://loom.com/your-demo-link  
*(Replace with your actual Loom or video demo)*

---

## 📦 Installation & Setup

### 🔧 Requirements

- Python 3.9+
- Ollama with Mistral model installed
- Streamlit
- Required libraries in `requirements.txt`

### 📁 Setup

```bash
# Clone the repo
git clone https://github.com/your-username/talent-assistant-bot.git
cd talent-assistant-bot

# (Optional) Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py


