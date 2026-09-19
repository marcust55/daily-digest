# Daily Digest

I'm taking four courses at once and kept losing track of what was due when. So I built this: a small Python script that looks at my schedule, figures out what I have today and what's coming up, and asks Claude to turn it into a short morning digest with a suggestion for what to study first.

## Running it

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install anthropic
export ANTHROPIC_API_KEY="your-key"   # Windows PowerShell: $env:ANTHROPIC_API_KEY="your-key"

python digest.py                  # get today's digest
python test.py                    # run the tests (no API key needed)
```

Your schedule lives in `schedule.json`, so edit that to change classes or deadlines.

## How it's put together

I wanted this to be easy to change and easy to test, so I split it into a few small classes instead of one long script:

- **`Schedule`** loads the JSON and answers two questions: what classes do I have today, and what's due soon? Nothing else in the code knows the file format, so I could swap in a database or calendar later without touching anything else.
- **`ClassSession`** and **`Assignment`** are small data objects. `Assignment` knows how to work out its own `days_left()`.
- **`DigestGenerator`** builds the prompt from a `Schedule` and hands it to a client.
- **`LLMClient`** is an abstract class with one method, `generate(prompt)`. `ClaudeClient` calls the real API, and `FakeClient` returns canned text so the tests never hit the network.

The main design idea is that `DigestGenerator` is given its schedule and client instead of creating them itself. That's what lets me test it with a fake client, and I'd rather it use composition than inheritance.

## Things I'd like to add

- Run it automatically every morning and email me the result
- Retry logic for when the API is slow or down
- Pull deadlines straight from my calendar instead of a JSON file
