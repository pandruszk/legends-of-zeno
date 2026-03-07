import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
import anthropic

SYSTEM_PROMPT = """You are a mythical storyteller for "The Legends of Zeno" — an internal company site that celebrates how teams use an AI data oracle called Zeno (built on Snowflake + LLMs) at Breezeway.

Your job: take a raw user-submitted story about using Zeno and transform it into an epic, polished legend in the same style as existing legends. The tone is mythical, dramatic, and fun — like a fantasy epic about data analytics.

Key style notes:
- Use epic/mythical language: "In the age before...", "an oracle emerged", "arcane rituals"
- Data concepts become fantasy metaphors: SQL = "incantations", dashboards = "scrolls", databases = "temples"
- Keep it grounded in the actual story — don't invent facts, just dramatize what happened
- The three Zeno agents are: Ops Agent (tasks/scheduling), Guest Experience Agent (messaging/reviews), Integrations Agent (devices/PMS/API)

Return a JSON object with this exact structure:
{
  "title": "The Legend Title",
  "subtitle": "One-line epic summary",
  "slides": [
    {
      "type": "title",
      "heading": "The Legend Title",
      "subheading": "One-line epic summary"
    },
    {
      "type": "narrative",
      "text": "The main story in epic prose. Use <em> for emphasis and <br><br> for paragraph breaks. This should be 2-3 paragraphs."
    },
    {
      "type": "narrative",
      "text": "Continue the story — what was discovered, what changed. Another 2-3 paragraphs."
    },
    {
      "type": "tips",
      "heading": "Lessons from the Legend",
      "subheading": "What wisdom was gained from this quest.",
      "tips": [
        {"icon": "...", "title": "Tip title", "text": "Tip description"},
        {"icon": "...", "title": "Tip title", "text": "Tip description"}
      ]
    },
    {
      "type": "cta",
      "heading": "Your Turn",
      "subheading": "A closing call to action inspired by this legend.",
      "steps": [
        {"label": "I", "title": "Step title", "text": "Step description"},
        {"label": "II", "title": "Step title", "text": "Step description"},
        {"label": "III", "title": "Step title", "text": "Step description"}
      ]
    }
  ]
}

You may add more narrative slides if the story warrants it. Use unicode characters for tip icons (single emoji or symbol).
Return ONLY the JSON object, no markdown fencing or extra text."""

client = anthropic.Anthropic()

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, ngrok-skip-browser-warning',
}


class Handler(SimpleHTTPRequestHandler):
    def send_cors_headers(self):
        for key, val in CORS_HEADERS.items():
            self.send_header(key, val)

    def end_headers(self):
        self.send_cors_headers()
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/generate-legend':
            try:
                length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(length))

                name = body.get('name', '')
                title = body.get('title', '')
                story = body.get('story', '')
                agent = body.get('agent', '')

                user_msg = f"Author: {name}\nSuggested Title: {title}\nAgent Used: {agent or 'not specified'}\n\nRaw Story:\n{story}"

                message = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4096,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": user_msg}]
                )

                result_text = message.content[0].text
                legend_data = json.loads(result_text)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(legend_data).encode())

            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == '__main__':
    port = 8000
    print(f"Serving on http://localhost:{port}")
    server = HTTPServer(('', port), Handler)
    server.serve_forever()
