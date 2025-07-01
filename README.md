# PDF Q&A Bot with RAG

A sophisticated PDF Question & Answer bot built with **Streamlit**, **LangChain**, **ChromaDB**, and **Google Gemini**. This application implements **Retrieval Augmented Generation (RAG)** to allow users to upload PDF documents and ask questions about their content with AI-powered responses and source citations.

## 🚀 Features

- **📄 PDF Upload & Processing**: Upload and analyze PDF documents
- **🤖 AI-Powered Q&A**: Ask questions using Google Gemini 2.0 Flash
- **🔍 RAG Technology**: Advanced Retrieval Augmented Generation pipeline
- **📚 Vector Database**: ChromaDB for efficient similarity search
- **📖 Source Citations**: View relevant document sections for each answer
- **💬 Interactive Chat**: Real-time conversation interface
- **🎯 Accurate Answers**: Context-based responses from your documents

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI/ML**: Google Gemini API, LangChain
- **Vector Database**: ChromaDB
- **Document Processing**: PyPDF, RecursiveCharacterTextSplitter
- **Embeddings**: Google Generative AI Embeddings

## 📋 Prerequisites

- Python 3.8+
- Google Generative AI API key
- Windows/Mac/Linux

## ⚡ Quick Start

### 1. Clone the Repository

\`\`\`bash
git clone https://github.com/your-username/pdf-qa-bot.git
cd pdf-qa-bot
\`\`\`

### 2. Install Dependencies

\`\`\`bash

# For Windows users (recommended)

python setup_windows.py

# Or use pip directly

pip install -r requirements.txt
\`\`\`

### 3. Set Up API Key

1. Get your Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Copy \`.streamlit/secrets.toml.example\` to \`.streamlit/secrets.toml\`
3. Add your API key:
   \`\`\`toml
   GOOGLE_API_KEY = "your-actual-api-key-here"
   \`\`\`

### 4. Run the Application

\`\`\`bash
streamlit run app.py

# or

python -m streamlit run app.py
\`\`\`

## 🎯 How to Use

1. **📤 Upload PDF**: Use the file uploader to select your PDF document
2. **🔄 Process PDF**: Click "Process PDF" to analyze and index the content
3. **💬 Ask Questions**: Type questions in the chat interface or use sample questions
4. **📖 View Sources**: Expand source sections to see relevant document excerpts

## 🔧 RAG Pipeline Architecture

### 1. Document Loading

- PDFs loaded using LangChain's PyPDFLoader
- Text extracted from all pages

### 2. Text Chunking

- Documents split using RecursiveCharacterTextSplitter
- Chunk size: 1000 characters with 200 character overlap
- Maintains context while enabling efficient retrieval

### 3. Embedding Generation

- Google's embedding-001 model creates vector representations
- High-quality embeddings for semantic similarity

### 4. Vector Storage

- ChromaDB stores document embeddings
- Persistent storage with efficient similarity search

### 5. Retrieval & Generation

- User queries embedded and matched against document vectors
- Top-4 similar chunks retrieved
- Google Gemini generates contextual answers using retrieved content

## 📁 Project Structure

\`\`\`
pdf-qa-bot/
├── app.py # Main Streamlit application
├── setup_windows.py # Windows-specific setup script
├── requirements.txt # Python dependencies
├── .streamlit/
│ ├── secrets.toml.example # API key template
│ └── secrets.toml # Your API key (not in Git)
├── chroma_db/ # ChromaDB storage (auto-created)
├── .gitignore # Git ignore file
└── README.md # This file
\`\`\`

## 🤔 Sample Questions

- "What is the main topic of this document?"
- "Summarize the key points"
- "What are the conclusions?"
- "List the important findings"
- "What methodology was used?"
- "Who are the authors mentioned?"

## 🔧 Configuration

### Environment Variables

- \`GOOGLE_API_KEY\`: Your Google Generative AI API key

### Customization Options

- Modify chunk size and overlap in the \`process_pdf()\` function
- Adjust retrieval parameters (k value) for more/fewer source documents
- Customize the prompt template for different response styles
- Change the AI model in the ChatGoogleGenerativeAI configuration

## 🚨 Troubleshooting

### Common Issues

1. **API Key Error**: Ensure GOOGLE_API_KEY is properly set in secrets.toml
2. **Import Errors**: Run \`python setup_windows.py\` to install correct packages
3. **ChromaDB Issues**: Delete chroma_db folder and restart
4. **Memory Issues**: Reduce chunk size for large documents

### Windows-Specific Issues

- **NumPy Compilation Error**: Use \`setup_windows.py\` instead of requirements.txt
- **Missing Visual C++**: Install Microsoft C++ Build Tools

## 📊 Performance Tips

- Use PDF files under 10MB for optimal performance
- Clear chat history periodically to free memory
- Restart the app if experiencing memory issues
- Use SSD storage for better ChromaDB performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (\`git checkout -b feature/amazing-feature\`)
3. Commit your changes (\`git commit -m 'Add amazing feature'\`)
4. Push to the branch (\`git push origin feature/amazing-feature\`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain** for document processing framework
- **ChromaDB** for vector database capabilities
- **Google** for Generative AI API
- **Streamlit** for the web interface framework

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Open an issue on GitHub
3. Make sure you're using the latest version

---

**Made with ❤️ using Streamlit, LangChain, ChromaDB, and Google Gemini**
