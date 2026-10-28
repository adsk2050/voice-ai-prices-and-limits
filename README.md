# voice-ai-prices-and-limits

Prices and rate limits for voice AI services, as structured data that
updates itself: **speech-to-text (STT)**, **text-to-speech (TTS)** and
**telephony**, for Indian and global providers.

Every number is scraped from the provider's own page, stored with the
page's own words as evidence, and re-checked every day. Every change is
a commit, so the git history is the price history.

> **LLM prices are not here.** [models.dev](https://models.dev) keeps
> them well. If you need an LLM price this repo has a reason to carry
> (an Indian provider models.dev lacks, say), open an issue.

## The files

| File | What is in it |
|---|---|
| `data/stt.json` | Speech-to-text prices, per provider, model, mode and plan |
| `data/tts.json` | Text-to-speech prices |
| `data/telephony.json` | Call prices: per country, inbound or outbound, pulse, minimums |
| `data/checked.json` | When each provider's page was last checked, and whether its scraper worked |
| `schema/row.schema.json` | The shape every row must have. CI rejects a file that breaks it |

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

## What you actually pay

The listed price is not the whole bill. The data records what the
pages state: whether tax is included, billing pulse, minimum charges,
fees per call. What depends on the buyer (your country, whether you are
tax-registered, reverse charge on foreign services, your card's forex
markup) is not data; a calculator that takes those as inputs is
planned.

## How it updates

A GitHub Action runs every scraper once a day, and on demand from the
Actions tab.

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

Keeping the scrapers working is a shared job: when a provider moves
its page or changes its layout, the daily run opens a "scraper broken"
issue, and a fix is a pull request to that provider's scraper.

## Licence

MIT.
