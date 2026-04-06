# 📚 Teacher ChatBot

An intelligent AI-powered chatbot that behaves like your personal teacher, helping you learn any subject in the world.

## Features

✨ **Three Teaching Modes:**
- **Interactive Q&A**: Ask questions and get detailed answers
- **Explanations**: Get in-depth explanations with examples
- **Quiz**: Test your knowledge with AI-generated quizzes

🎓 **Smart Teaching:**
- Patient, encouraging teaching style
- Real-world examples and analogies
- Step-by-step breakdowns
- Feedback and guidance

🎤 **Voice Features:**
- **Speech Input**: Speak your questions instead of typing
- **Voice Response**: Listen to the chatbot's answers
- Natural speech-to-text and text-to-speech capabilities

📖 **Any Subject:**
- Learn Python programming
- Study biology, chemistry, physics
- Explore history, literature, language
- Master mathematics
- And much more!

💬 **Chat Memory:**
- All questions are remembered in your chat session
- View complete conversation history
- Build on previous answers
- Context-aware teaching

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key
5. **Note**: Gemini API is free to use!

### 3. Add Your API Key to the App

When you run the app, you'll see a settings panel on the left. Enter your Google Gemini API key there.

### 4. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## How to Use

### Input Methods
Choose how you want to ask your questions:

**1. Type Your Question**
- Directly type your question in the text input box
- Click "Send" to submit

**2. Speak Your Question**
- Select "Speak Question" option
- Click the "🎤 Start Recording" button
- Speak clearly into your microphone
- The chatbot will transcribe your speech

### Voice Response
Enable voice response in the settings to:
- Hear the chatbot's answers spoken aloud
- Customize speech rate
- Learn while multitasking
Text-Based Interaction
- Ask: "What is photosynthesis?"
- Ask follow-up: "Can you give me an example?"
- Continue learning: "How does it help plants?"

### Voice-Based Interaction
1. Click "🎤 Start Recording"
2. Say: "Explain machine learning"
3. Chatbot responds with spoken and text answer
4. Ask follow-up question by voice
5. All questions saved in chat history

### Quiz Mode Examples
- "Quiz me on calculus"
- *Chatbot asks a question*
- *You answer via text or voice*
- *Chatbot provides feedback*
- Continue with more questions
2. **Explanations Mode**
   - Request detailed explanations
   - Ask for examples and analogies
   - Get step-by-step breakdowns

3. **Quiz Mode**
   - Test your knowledge
   - Get one question at a time
   - Receive feedback on answers

## Example Interactions

### Interactive Q&A Mode
- "What is photosynthesis?"
- "How do I write a Python function?"
- "Explain the French Revolution"

### Explanations Mode
- "Explain machine learning like I'm 5"
- "How does the human immune system work?"
- "Walk me through probability theory"

### Quiz Mode
- "Quiz me on calculus"
- "Test my knowledge of world capitals"
- "Give me JavaScript questions"

## Environment Variables

Create a `.env` file in the project root (optional):

```
GOOGLE_GEMINI_API_KEY=your_api_key_here
```

Or simply enter your API key in the app's settings panel.

## Troubleshooting

**Error: "Invalid API key"**
- Check your Google Gemini API key is correct
- Visit [makersuite.google.com](https://makersuite.google.com/app/apikey) to verify
- Make sure you're using the Gemini API key, not another Google API key

**App runs slowly**
- Gemini API calls may take a few seconds
- This is normal behavior

## Troubleshooting

### Speech Issues

**"Error: Could not reach Google Speech Recognition service"**
- Check your internet connection
- The speech recognition requires an internet connection
- Try again in a moment

**Microphone not detected**
- Check if your microphone is properly connected
- On Windows: Settings → Sound → Volume
- On Mac: System Preferences → Security & Privacy → Microphone
- Make sure you gave permission to the browser

**Speech not understood**
- Speak clearly and directly into the microphone
- Reduce background noise
- Try again with a clearer voice

**Text-to-speech not working**
- Ensure speakers are properly connected
- Check volume isn't muted
- Try disabling and re-enabling voice response
- Restart the app

### Chat Memory Issues

**Chat history disappeared**
- Click "Clear Chat History" was pressed
- Refresh the browser page
- Check if you're in the correct chat session

**Questions not saving**
- Make sure you click "Send" button
- Check the conversation is displayed in chat history
- Refresh page to see if messages persist

## Project Structure

```
chattutor/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment file
├── .env                # Your actual environment (create this)
└── README.md          # This file
```

## Tech Stack

- **Google Geminilit**: Web application framework
- **OpenAI API**: AI/LLM for chat responses
- **Python 3.8+**: Programming language

## Tips for Best Results

1. **Be Specific**: The more specific your questions, the better the answers
2. **Follow Up**: Ask follow-up questions for deeper understanding
3. **Request Examples**: Ask "Give me an example" to get practical demonstrations
4. **Use Quiz Mode**: Test yourself regularly to reinforce learning
5. **Clear History**: Start fresh conversations when switching topics

## Future Enhancements

- [ ] Support for multiple languages
- [ ] Export chat history as PDF
- [ ] Adjustable difficulty levels
- [ ] Topics progress tracking
- [ ] Conversation bookmarks
- [ ] Voice input/output

## License

MIT License - Feel free to use and modify for your learning!

## Support

For issues or questions, check the troubleshooting section or review the code comments.

---

**Happy Learning! 📚✨**
