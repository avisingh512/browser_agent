```markdown
# AI-Powered Form Automation System

An intelligent form filling system combining Selenium automation with OpenAI's language model for smart form interactions.

## Features

- 🧠 AI-powered form field interpretation using GPT-4
- 🌐 Dynamic form field detection
- 🔄 Automatic retry and fallback mechanisms
- 📦 Structured data handling with Pydantic models
- 🚀 FastAPI backend for easy integration
- 🛠️ Automatic ChromeDriver management

## Technologies

- Python 3.9+
- FastAPI
- Selenium
- LangChain
- OpenAI API
- Pydantic
- WebDriver Manager

## Prerequisites

1. Python 3.9 or later
2. Chrome browser installed
3. OpenAI API key
4. Basic understanding of REST APIs

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/form-automation.git
   cd form-automation
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create `.env` file:
   ```env
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

2. Send POST request to process a form:
   ```bash
   curl -X POST "http://localhost:8000/process-form" \
   -H "Content-Type: application/json" \
   -d '{"url": "https://example.com/form"}'
   ```

### Example Request
```json
{
  "url": "https://example.com/contact-form"
}
```

### Example Response
```json
{
  "status": "success",
  "filled_fields": [
    {"label": "Email", "value": "user123@example.com"},
    {"label": "Phone", "value": "555-123-4567"}
  ]
}
```

## API Reference

### POST /process-form
**Parameters:**
- `url` (string): URL of the form to process

**Response:**
- Status of operation
- List of filled fields with values

## Configuration

Customize these parameters in the code:
- `temperature` (0.3): Controls AI creativity
- Model selection (`gpt-4o-mini`)
- Field detection thresholds
- Wait times between actions

## Troubleshooting

Common issues:
1. **ChromeDriver issues:**
   - Ensure Chrome is updated
   - Check firewall settings

2. **API errors:**
   - Verify OpenAI API key in `.env`
   - Check API quota

3. **Field detection failures:**
   - Add manual wait times for complex forms
   - Check form structure in developer tools

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create new Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details

---

**Note:** Use responsibly and comply with target websites' terms of service. This tool is intended for educational purposes only.
```
