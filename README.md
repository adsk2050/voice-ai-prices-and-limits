# voice-ai-prices-and-limits

Prices and rate limits for voice AI services, as structured data that
updates itself: **speech-to-text (STT)**, **text-to-speech (TTS)** and
**telephony**, for Indian and global providers.

Every number is scraped from the provider's own page, stored with the
page's own words as evidence, and re-checked every day. Every change is
a commit, so the git history is the price history.

[![Request a provider or model](https://img.shields.io/badge/Request-a%20provider%20or%20model-2ea44f)](https://github.com/adsk2050/voice-ai-prices-and-limits/issues/new?template=new-provider.yml)
[![Re-check prices now](https://img.shields.io/badge/Re--check-prices%20now-0969da)](https://github.com/adsk2050/voice-ai-prices-and-limits/issues/new?template=recheck.yml)
[![Report a wrong price](https://img.shields.io/badge/Report-a%20wrong%20price-d73a49)](https://github.com/adsk2050/voice-ai-prices-and-limits/issues/new?template=wrong-price.yml)

> **LLM prices are not here.** [models.dev](https://models.dev) keeps
> them well. If you need an LLM price this repo has a reason to carry
> (an Indian provider models.dev lacks, say), open an issue.

## What is tracked

Generated from the data files on every run. Price is the range across
plans and modes, in the currency the provider states.

<!-- coverage:start -->
| Category | Provider | Product | Modes | Plans | Price | Last checked |
|---|---|---|---|---|---|---|
| Speech-to-text | sarvam | saaras | batch, batch-with-diarization, real-time | pay-as-you-go, pro, growth, business | 0.38–0.59 INR per minute | 2026-10-28 |
| Text-to-speech | sarvam | bulbul-v3 | real-time, streaming, websocket | pay-as-you-go, pro, growth, business | 2.6–3 INR per 1,000 characters | 2026-10-28 |
| Text-to-speech | sarvam | bulbul-v4-flash | real-time, streaming, websocket | pay-as-you-go, pro, growth, business | 0.8–1 INR per 1,000 characters | 2026-10-28 |
| Text-to-speech | sarvam | voice-cloning | real-time | pay-as-you-go, pro, growth, business | 2 INR per 1,000 characters | 2026-10-28 |
<!-- coverage:end -->

## The files

| File | What is in it |
|---|---|
| `data/stt.json` | Speech-to-text prices, per provider, model, mode and plan |
| `data/tts.json` | Text-to-speech prices |
| `data/telephony.json` | Call prices: per country, inbound or outbound, pulse, minimums |
| `data/checked.json` | When each provider's page was last checked, and whether its scraper worked |
| `schema/row.schema.json` | The shape every row must have, as JSON Schema. Generated from the Pydantic models in `src/voice_prices/models.py`; CI fails if the two differ |

Fetch them straight from GitHub, for example
`https://raw.githubusercontent.com/adsk2050/voice-ai-prices-and-limits/main/data/tts.json`.

## One row

```json
{
  "id": "sarvam/bulbul-v4-flash/real-time/pay-as-you-go",
  "category": "tts",
  "provider": "sarvam",
  "product": "bulbul-v4-flash",
  "mode": "real-time",
  "plan": "pay-as-you-go",
  "price": {"amount": "1.00", "currency": "INR", "per": 1000, "unit": "character"},
  "plan_fee": {"amount": "0", "currency": "INR", "period": "month"},
  "tax_included": false,
  "limits": null,
  "source_url": "https://www.sarvam.ai/api-pricing",
  "evidence": "Bulbul V4 Flash, real-time per 1,000 characters ₹1.00 ₹0.925 ₹0.85 ₹0.80",
  "since": "2026-10-28"
}
```

Rules the data keeps:

- **Prices stay in the currency the page states.** A rupee price stays
  in rupees, a dollar price in dollars. Amounts are decimal strings, so
  no float rounding creeps in. Converting to one currency is a separate,
  later step that records the exchange rate and its date.
- **Each plan is its own row.** Pay as you go, Pro, Growth and so on.
- **`evidence` is the text the number was read from**, so anyone can
  check it against the page.
- **`since`** is the first day this repo saw this value. When the
  page was last checked is in `data/checked.json`, per provider, so a
  row's history in git shows only real price changes.
- **`tax_included`** says whether the listed price includes GST, VAT or
  sales tax: `false` when the page says it excludes tax, `null` when
  the page does not say.
- **`limits`** holds the plan's published limits: requests per minute,
  concurrent requests or streams, calls per second. `null` until known.

## Use it from an agent (MCP)

The repo ships an MCP server with three tools:

| Tool | What it answers |
|---|---|
| `list_providers(category)` | Who is covered, and when each provider was last checked |
| `get_prices(category, provider, product, mode, plan)` | The matching rows |
| `compare(category, plan)` | Cheapest first, grouped by currency and unit, never converted |

Add it to an MCP client (Claude Code, Claude Desktop, Cursor and others):

```json
{
  "mcpServers": {
    "voice-prices": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/adsk2050/voice-ai-prices-and-limits", "voice-prices-mcp"]
    }
  }
}
```

It reads the data files from this repo on GitHub and caches them for an
hour. Set `VOICE_PRICES_DATA` to a local `data/` folder or another URL
to read from there instead.

## What you actually pay

The listed price is not the whole bill. The data records what the
pages state: whether tax is included, billing pulse, minimum charges,
fees per call. What depends on the buyer (your country, whether you are
tax-registered, reverse charge on foreign services, your card's forex
markup) is not data; a calculator that takes those as inputs is
planned.

## How it updates

A GitHub Actions workflow (`.github/workflows/update.yml`) runs every
scraper once a day at 03:30 UTC, on GitHub's servers. It also runs on
demand: anyone can open a [re-check issue](https://github.com/adsk2050/voice-ai-prices-and-limits/issues/new?template=recheck.yml),
which starts the run, posts the result on the issue and closes it.
Maintainers can also use **Run workflow** on the Actions tab.

- **No price changed:** it opens a pull request that only moves the
  dates in `data/checked.json`, and merges it at once. A merged pull
  request every day is the sign the data is fresh.
- **A price changed** (or a plan fee, tax flag or limit, or a row
  appeared or went): the pull request shows the old value, the new
  value and the evidence, and waits for a person to merge it.
- **A scraper broke:** the provider keeps its old rows, is marked
  `failed` in `data/checked.json`, and an issue is opened for it. A
  scraper never guesses a number it cannot find.

## Contributing

To add a provider, add one file in `src/voice_prices/scrapers/` and a
test with a short excerpt of the page in `tests/fixtures/`. See
`src/voice_prices/scrapers/sarvam.py` for the pattern. Run
`uv run pytest` and `uv run voice-prices update`, then open a pull
request. Wrong price? Open an issue with a link to the page.

Commits are scanned for secrets (API keys, tokens) with
[gitleaks](https://github.com/gitleaks/gitleaks): on every pull request
in CI, and locally after `uvx pre-commit install`.

Keeping the scrapers working is a shared job: when a provider moves
its page or changes its layout, the daily run opens a "scraper broken"
issue, and a fix is a pull request to that provider's scraper.

## Licence

MIT.
