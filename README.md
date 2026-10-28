# voice-ai-prices-and-limits

Prices and rate limits for voice AI services, as structured data that
updates itself: **speech-to-text (STT)**, **text-to-speech (TTS)**, **telephony** and
**voice-agent platforms**, for Indian and global providers.

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
| Speech-to-text | assemblyai | dictation-api | batch | pay-as-you-go | 0.62 USD per hour | 2026-10-28 |
| Speech-to-text | assemblyai | sync-api | batch | pay-as-you-go | 0.3 USD per hour | 2026-10-28 |
| Speech-to-text | assemblyai | universal-2 | batch | pay-as-you-go | 0.15 USD per hour | 2026-10-28 |
| Speech-to-text | assemblyai | universal-3.5-pro | batch | pay-as-you-go | 0.21 USD per hour | 2026-10-28 |
| Speech-to-text | assemblyai | universal-3.6-pro-realtime | real-time | pay-as-you-go | 0.45 USD per hour | 2026-10-28 |
| Speech-to-text | assemblyai | universal-streaming | real-time | pay-as-you-go | 0.15 USD per hour | 2026-10-28 |
| Speech-to-text | assemblyai | universal-streaming-multilingual | real-time | pay-as-you-go | 0.15 USD per hour | 2026-10-28 |
| Speech-to-text | aws | call-analytics | any | pay-as-you-go | 0.0138–0.03 USD per minute | 2026-10-28 |
| Speech-to-text | aws | content-redaction | any | pay-as-you-go | 0.00102–0.0024 USD per minute | 2026-10-28 |
| Speech-to-text | aws | transcribe | batch, streaming | pay-as-you-go | 0.006–0.01 USD per minute | 2026-10-28 |
| Speech-to-text | azure | fast-transcription | any | pay-as-you-go | 0.36 USD per hour | 2026-10-28 |
| Speech-to-text | azure | speech-to-text | batch, real-time | pay-as-you-go | 0.18–1 USD per hour | 2026-10-28 |
| Speech-to-text | cartesia | ink-2 | any | scale | 0.39 USD per hour | 2026-10-28 |
| Speech-to-text | deepgram | flux-english | streaming | growth, pay-as-you-go | 0.0057–0.0065 USD per minute | 2026-10-28 |
| Speech-to-text | deepgram | flux-multilingual | streaming | growth, pay-as-you-go | 0.0068–0.0078 USD per minute | 2026-10-28 |
| Speech-to-text | deepgram | nova-3-monolingual | batch, streaming | growth, pay-as-you-go | 0.0036–0.0048 USD per minute | 2026-10-28 |
| Speech-to-text | deepgram | nova-3-multilingual | batch, streaming | growth, pay-as-you-go | 0.0043–0.0058 USD per minute | 2026-10-28 |
| Speech-to-text | deepgram | whisper-large | batch | growth, pay-as-you-go | 0.0048 USD per minute | 2026-10-28 |
| Speech-to-text | elevenlabs | scribe-v2 | any | pay-as-you-go | 0.22 USD per hour | 2026-10-28 |
| Speech-to-text | elevenlabs | scribe-v2-medical | any | pay-as-you-go | 0.22 USD per hour | 2026-10-28 |
| Speech-to-text | elevenlabs | scribe-v2-realtime | real-time | pay-as-you-go | 0.39 USD per hour | 2026-10-28 |
| Speech-to-text | gladia | real-time-speech-to-text | real-time | self-serve | 0.68 EUR per hour | 2026-10-28 |
| Speech-to-text | gladia | solaria-1 | batch | self-serve | 0.21–0.27 EUR per hour | 2026-10-28 |
| Speech-to-text | gladia | solaria-3 | batch | self-serve | 0.12–0.16 EUR per hour | 2026-10-28 |
| Speech-to-text | google | dynamic-batch-recognition | batch | gemini-enterprise-flexible-savings-plan-1-year, gemini-enterprise-flexible-savings-plan-3-year, pay-as-you-go | 0.0024–0.003 USD per minute | 2026-10-28 |
| Speech-to-text | google | medical-conversation | any | gemini-enterprise-flexible-savings-plan-1-year, gemini-enterprise-flexible-savings-plan-3-year, pay-as-you-go | 0.0624–0.078 USD per minute | 2026-10-28 |
| Speech-to-text | google | medical-dictation | any | gemini-enterprise-flexible-savings-plan-1-year, gemini-enterprise-flexible-savings-plan-3-year, pay-as-you-go | 0.0624–0.078 USD per minute | 2026-10-28 |
| Speech-to-text | google | recognition | any | gemini-enterprise-flexible-savings-plan-1-year, gemini-enterprise-flexible-savings-plan-3-year, pay-as-you-go | 0.0128–0.016 USD per minute | 2026-10-28 |
| Speech-to-text | google | speech-recognition-with-data-logging | any | gemini-enterprise-flexible-savings-plan-1-year, gemini-enterprise-flexible-savings-plan-3-year, pay-as-you-go | 0.0128–0.016 USD per minute | 2026-10-28 |
| Speech-to-text | google | speech-recognition-without-data-logging | any | gemini-enterprise-flexible-savings-plan-1-year, gemini-enterprise-flexible-savings-plan-3-year, pay-as-you-go | 0.0192–0.024 USD per minute | 2026-10-28 |
| Speech-to-text | inworld | stt-1 | any | on-demand, creator, builder, developer, growth | 0.1–0.15 USD per hour | 2026-10-28 |
| Speech-to-text | openai | gpt-4o-mini-transcribe | any | pay-as-you-go | 0.003 USD per minute | 2026-10-28 |
| Speech-to-text | openai | gpt-4o-transcribe | any | pay-as-you-go | 0.006 USD per minute | 2026-10-28 |
| Speech-to-text | openai | gpt-live-transcribe | real-time | pay-as-you-go | 0.017 USD per minute | 2026-10-28 |
| Speech-to-text | openai | gpt-realtime-whisper | real-time | pay-as-you-go | 0.017 USD per minute | 2026-10-28 |
| Speech-to-text | openai | gpt-transcribe | any | pay-as-you-go | 0.0045 USD per minute | 2026-10-28 |
| Speech-to-text | revai | human | any | pay-as-you-go | 1.99 USD per minute | 2026-10-28 |
| Speech-to-text | revai | reverb | any | pay-as-you-go | 0.2 USD per hour | 2026-10-28 |
| Speech-to-text | revai | reverb-foreign-language | any | pay-as-you-go | 0.3 USD per hour | 2026-10-28 |
| Speech-to-text | revai | whisper-large | any | pay-as-you-go | 0.005 USD per minute | 2026-10-28 |
| Speech-to-text | rime | rime-stt | any | pay-as-you-go | 0.002 USD per minute | 2026-10-28 (scraper broken) |
| Speech-to-text | sarvam | saaras | batch, batch-with-diarization, real-time | pay-as-you-go, pro, growth, business | 0.38–0.59 INR per minute | 2026-10-28 |
| Speech-to-text | smallestai | pulse | batch, real-time | pay-as-you-go | 0.003–0.004 USD per minute | 2026-10-28 |
| Speech-to-text | smallestai | pulse-pro | batch | pay-as-you-go | 0.0035 USD per minute | 2026-10-28 |
| Speech-to-text | soniox | stt | batch, real-time | pay-as-you-go | 0.1–0.12 USD per hour | 2026-10-28 |
| Speech-to-text | soniox | stt-input-audio-tokens | batch, real-time | pay-as-you-go | 1.5–2 USD per 1e+06 tokens | 2026-10-28 |
| Speech-to-text | soniox | stt-input-text-tokens | batch, real-time | pay-as-you-go | 3.5–4 USD per 1e+06 tokens | 2026-10-28 |
| Speech-to-text | soniox | stt-output-text-tokens | batch, real-time | pay-as-you-go | 3.5–4 USD per 1e+06 tokens | 2026-10-28 |
| Speech-to-text | speechmatics | enhanced | batch | pay-as-you-go | 0.38 USD per hour | 2026-10-28 |
| Speech-to-text | speechmatics | melia-1 | batch | pay-as-you-go | 0.12 USD per hour | 2026-10-28 |
| Speech-to-text | speechmatics | oak-1-medical | batch | pay-as-you-go | 0.15 USD per hour | 2026-10-28 |
| Speech-to-text | speechmatics | standard | batch | pay-as-you-go | 0.23 USD per hour | 2026-10-28 |
| Speech-to-text | telnyx | assemblyai-stt | any | pay-as-you-go | 0.005 USD per minute | 2026-10-28 |
| Speech-to-text | telnyx | azure-stt | any | pay-as-you-go | 0.027 USD per minute | 2026-10-28 |
| Speech-to-text | telnyx | basira-stt | any | pay-as-you-go | 0.007 USD per minute | 2026-10-28 |
| Speech-to-text | telnyx | cohere-arabic-stt | any | pay-as-you-go | 0.0015 USD per minute | 2026-10-28 |
| Speech-to-text | telnyx | deepgram-flux-stt | any | pay-as-you-go | 0.005 USD per minute | 2026-10-28 |
| Speech-to-text | telnyx | deepgram-nova-2-stt | any | pay-as-you-go | 0.005 USD per minute | 2026-10-28 |
| Speech-to-text | telnyx | deepgram-nova-3-stt | any | pay-as-you-go | 0.005 USD per minute | 2026-10-28 |
| Speech-to-text | telnyx | google-stt | any | pay-as-you-go | 0.017 USD per minute | 2026-10-28 |
| Speech-to-text | telnyx | grok-xai-stt | any | pay-as-you-go | 0.0033 USD per minute | 2026-10-28 |
| Speech-to-text | telnyx | humain-stt | any | pay-as-you-go | 0.007 USD per minute | 2026-10-28 |
| Speech-to-text | telnyx | parakeet-stt | any | pay-as-you-go | 0.0015 USD per minute | 2026-10-28 |
| Speech-to-text | telnyx | soniox-stt | any | pay-as-you-go | 0.002 USD per minute | 2026-10-28 |
| Speech-to-text | telnyx | speechmatics-stt | any | pay-as-you-go | 0.0035 USD per minute | 2026-10-28 |
| Speech-to-text | telnyx | telnyx-stt | any | pay-as-you-go | 0.015 USD per minute | 2026-10-28 |
| Speech-to-text | twilio | call-recording-transcription | any | pay-as-you-go | 0.05 USD per minute | 2026-10-28 |
| Speech-to-text | twilio | conversation-intelligence-transcription | batch, real-time | pay-as-you-go | 0.024–0.027 USD per minute | 2026-10-28 |
| Text-to-speech | assemblyai | assemblyai-tts-1 | any | pay-as-you-go | 15 USD per 1e+06 characters | 2026-10-28 |
| Text-to-speech | aws | generative-voices | any | pay-as-you-go | 30 USD per 1e+06 characters | 2026-10-28 |
| Text-to-speech | aws | long-form-voices | any | pay-as-you-go | 100 USD per 1e+06 characters | 2026-10-28 |
| Text-to-speech | aws | neural-voices | any | govcloud-us, pay-as-you-go | 16–19.2 USD per 1e+06 characters | 2026-10-28 |
| Text-to-speech | aws | standard-voices | any | govcloud-us, pay-as-you-go | 4–4.8 USD per 1e+06 characters | 2026-10-28 |
| Text-to-speech | azure | neural | any | pay-as-you-go | 15 USD per 1e+06 characters | 2026-10-28 |
| Text-to-speech | azure | neural-hd | any | pay-as-you-go | 22 USD per 1e+06 characters | 2026-10-28 |
| Text-to-speech | azure | neural-long-audio | batch | pay-as-you-go | 100 USD per 1e+06 characters | 2026-10-28 |
| Text-to-speech | cartesia | sonic-3.6 | any | pro, startup, scale | 38–65 USD per 1e+06 characters | 2026-10-28 |
| Text-to-speech | deepgram | aura-1 | any | growth, pay-as-you-go | 0.0135–0.015 USD per 1,000 characters | 2026-10-28 |
| Text-to-speech | deepgram | aura-2 | any | growth, pay-as-you-go | 0.027–0.03 USD per 1,000 characters | 2026-10-28 |
| Text-to-speech | deepgram | flux-tts | any | growth, pay-as-you-go | 0.0405–0.045 USD per 1,000 characters | 2026-10-28 |
| Text-to-speech | elevenlabs | flash-turbo | any | pay-as-you-go | 0.04 USD per 1,000 characters | 2026-10-28 |
| Text-to-speech | elevenlabs | v2-multilingual | any | pay-as-you-go | 0.08 USD per 1,000 characters | 2026-10-28 |
| Text-to-speech | elevenlabs | v3 | any | pay-as-you-go | 0.08 USD per 1,000 characters | 2026-10-28 |
| Text-to-speech | elevenlabs | v3-conversational | any | pay-as-you-go | 0.04 USD per 1,000 characters | 2026-10-28 |
| Text-to-speech | elevenlabs | v4 | any | pay-as-you-go | 0.08 USD per 1,000 characters | 2026-10-28 |
| Text-to-speech | elevenlabs | v4-turbo | any | pay-as-you-go | 0.04 USD per 1,000 characters | 2026-10-28 |
| Text-to-speech | google | chirp-3-hd | any | pay-as-you-go | 30 USD per 1e+06 characters | 2026-10-28 |
| Text-to-speech | google | gemini-2.5-flash-lite-preview-tts-audio-output | any | pay-as-you-go | 10 USD per 1e+06 tokens | 2026-10-28 |
| Text-to-speech | google | gemini-2.5-flash-lite-preview-tts-text-input | any | pay-as-you-go | 0.5 USD per 1e+06 tokens | 2026-10-28 |
| Text-to-speech | google | gemini-2.5-flash-tts-audio-output | any | pay-as-you-go | 10 USD per 1e+06 tokens | 2026-10-28 |
| Text-to-speech | google | gemini-2.5-flash-tts-text-input | any | pay-as-you-go | 0.5 USD per 1e+06 tokens | 2026-10-28 |
| Text-to-speech | google | gemini-2.5-pro-tts-audio-output | any | pay-as-you-go | 20 USD per 1e+06 tokens | 2026-10-28 |
| Text-to-speech | google | gemini-2.5-pro-tts-text-input | any | pay-as-you-go | 1 USD per 1e+06 tokens | 2026-10-28 |
| Text-to-speech | google | gemini-3.1-flash-tts-preview-audio-output | any | pay-as-you-go | 20 USD per 1e+06 tokens | 2026-10-28 |
| Text-to-speech | google | gemini-3.1-flash-tts-preview-text-input | any | pay-as-you-go | 1 USD per 1e+06 tokens | 2026-10-28 |
| Text-to-speech | google | gemini-3.8-flash-lite-tts-preview-audio-output | any | pay-as-you-go | 6 USD per 1e+06 tokens | 2026-10-28 |
| Text-to-speech | google | gemini-3.8-flash-lite-tts-preview-text-input | any | pay-as-you-go | 0.5 USD per 1e+06 tokens | 2026-10-28 |
| Text-to-speech | google | gemini-3.8-flash-tts-preview-audio-output | any | pay-as-you-go | 9 USD per 1e+06 tokens | 2026-10-28 |
| Text-to-speech | google | gemini-3.8-flash-tts-preview-text-input | any | pay-as-you-go | 0.5 USD per 1e+06 tokens | 2026-10-28 |
| Text-to-speech | google | instant-custom | any | pay-as-you-go | 60 USD per 1e+06 characters | 2026-10-28 |
| Text-to-speech | google | neural2 | any | pay-as-you-go | 16 USD per 1e+06 characters | 2026-10-28 |
| Text-to-speech | google | polyglot-preview | any | pay-as-you-go | 16 USD per 1e+06 characters | 2026-10-28 |
| Text-to-speech | google | standard | any | pay-as-you-go | 4 USD per 1e+06 characters | 2026-10-28 |
| Text-to-speech | google | studio | any | pay-as-you-go | 160 USD per 1e+06 characters | 2026-10-28 |
| Text-to-speech | google | wavenet | any | pay-as-you-go | 4 USD per 1e+06 characters | 2026-10-28 |
| Text-to-speech | inworld | tts-2 | real-time | enterprise, on-demand, creator, builder, developer, growth | 5–25 USD per 1e+06 characters | 2026-10-28 |
| Text-to-speech | inworld | tts-2-flash | real-time | on-demand, creator, builder, developer, growth | 7–15 USD per 1e+06 characters | 2026-10-28 |
| Text-to-speech | retell | cartesia-voices | any | pay-as-you-go | 0.015 USD per minute | 2026-10-28 |
| Text-to-speech | retell | elevenlabs-flash | any | pay-as-you-go | 0.04 USD per minute | 2026-10-28 |
| Text-to-speech | retell | elevenlabs-multilingual-v2 | any | pay-as-you-go | 0.06 USD per minute | 2026-10-28 |
| Text-to-speech | retell | elevenlabs-v3 | any | pay-as-you-go | 0.1 USD per minute | 2026-10-28 |
| Text-to-speech | retell | elevenlabs-v3-conversational | any | pay-as-you-go | 0.08 USD per minute | 2026-10-28 |
| Text-to-speech | retell | elevenlabs-v4 | any | pay-as-you-go | 0.1 USD per minute | 2026-10-28 |
| Text-to-speech | retell | elevenlabs-v4-turbo | any | pay-as-you-go | 0.08 USD per minute | 2026-10-28 |
| Text-to-speech | retell | fish-voices | any | pay-as-you-go | 0.015 USD per minute | 2026-10-28 |
| Text-to-speech | retell | inworld-voices | any | pay-as-you-go | 0.015 USD per minute | 2026-10-28 |
| Text-to-speech | retell | minimax-voices | any | pay-as-you-go | 0.015 USD per minute | 2026-10-28 |
| Text-to-speech | retell | openai-voices | any | pay-as-you-go | 0.015 USD per minute | 2026-10-28 |
| Text-to-speech | retell | retell-platform-voices | any | pay-as-you-go | 0.015 USD per minute | 2026-10-28 |
| Text-to-speech | rime | coda-v2 | any | pay-as-you-go | 0.05 USD per minute | 2026-10-28 (scraper broken) |
| Text-to-speech | rime | mist-v3 | any | pay-as-you-go | 0.03 USD per minute | 2026-10-28 (scraper broken) |
| Text-to-speech | sarvam | bulbul-v3 | real-time, streaming, websocket | pay-as-you-go, pro, growth, business | 2.6–3 INR per 1,000 characters | 2026-10-28 |
| Text-to-speech | sarvam | bulbul-v4-flash | real-time, streaming, websocket | pay-as-you-go, pro, growth, business | 0.8–1 INR per 1,000 characters | 2026-10-28 |
| Text-to-speech | sarvam | voice-cloning | real-time | pay-as-you-go, pro, growth, business | 2 INR per 1,000 characters | 2026-10-28 |
| Text-to-speech | smallestai | lightning-v3.1 | any | pay-as-you-go | 0.175 USD per 10,000 characters | 2026-10-28 |
| Text-to-speech | smallestai | lightning-v3.1-pro | any | pay-as-you-go | 0.195 USD per 10,000 characters | 2026-10-28 |
| Text-to-speech | soniox | tts-input-text-tokens | real-time | pay-as-you-go | 4 USD per 1e+06 tokens | 2026-10-28 |
| Text-to-speech | soniox | tts-output-audio-tokens | real-time | pay-as-you-go | 21.5 USD per 1e+06 tokens | 2026-10-28 |
| Text-to-speech | speechmatics | text-to-speech | any | pay-as-you-go | 0.011 USD per 1,000 characters | 2026-10-28 |
| Text-to-speech | telnyx | inworld-max-tts | any | pay-as-you-go | 1e-05 USD per character | 2026-10-28 |
| Text-to-speech | telnyx | inworld-mini-tts | any | pay-as-you-go | 5.5e-06 USD per character | 2026-10-28 |
| Text-to-speech | telnyx | minimax-speech-2.8-turbo-tts | any | pay-as-you-go | 3.4e-05 USD per character | 2026-10-28 |
| Text-to-speech | telnyx | neural-voices-tts-amazon-polly | any | pay-as-you-go | 2.4e-05 USD per character | 2026-10-28 |
| Text-to-speech | telnyx | qwen3tts | any | pay-as-you-go | 3.2e-05 USD per character | 2026-10-28 |
| Text-to-speech | telnyx | resemble-tts | any | pay-as-you-go | 8e-06 USD per character | 2026-10-28 |
| Text-to-speech | telnyx | rime-tts | any | pay-as-you-go | 2e-05 USD per character | 2026-10-28 |
| Text-to-speech | telnyx | standard-tts-amazon-polly | any | pay-as-you-go | 9e-06 USD per character | 2026-10-28 |
| Text-to-speech | telnyx | telnyx-hd-voices-tts | any | pay-as-you-go | 4.8e-05 USD per character | 2026-10-28 |
| Text-to-speech | telnyx | telnyx-tts | any | pay-as-you-go | 3e-06 USD per character | 2026-10-28 |
| Text-to-speech | telnyx | telnyx-ultra | any | pay-as-you-go | 3.2e-05 USD per character | 2026-10-28 |
| Text-to-speech | twilio | premium-generative | any | pay-as-you-go | 0.013 USD per 100 characters | 2026-10-28 |
| Text-to-speech | twilio | premium-neural | any | pay-as-you-go | 0.0032 USD per 100 characters | 2026-10-28 |
| Text-to-speech | twilio | premium-standard | any | pay-as-you-go | 0.0008 USD per 100 characters | 2026-10-28 |
| Telephony | cartesia | cartesia-provided-number | any | pay-as-you-go | 0.014 USD per minute | 2026-10-28 |
| Telephony | knowlarity | missed-call-number | any | monthly-plan | 5000 INR per month | 2026-10-28 |
| Telephony | knowlarity | toll-free-number | inbound | basic, advance, premium | 1.05 INR per minute | 2026-10-28 |
| Telephony | plivo | answering-machine-detection | any | pay-as-you-go | 0 INR per minute | 2026-10-28 |
| Telephony | plivo | automatic-speech-recognition | any | pay-as-you-go | 1.7 INR per 15 seconds | 2026-10-28 |
| Telephony | plivo | browser-sdks-and-webrtc | inbound, outbound | pay-as-you-go | 0.25 INR per minute | 2026-10-28 |
| Telephony | plivo | call-recording | any | pay-as-you-go | 0 INR per minute | 2026-10-28 |
| Telephony | plivo | call-transcription | any | pay-as-you-go | 0.81 INR per minute | 2026-10-28 |
| Telephony | plivo | conference-calls | any | pay-as-you-go | 0 INR per minute | 2026-10-28 |
| Telephony | plivo | domestic-calls | inbound, outbound | pay-as-you-go | 0.38 INR per minute | 2026-10-28 |
| Telephony | plivo | multilingual-text-to-speech | any | pay-as-you-go | 0 INR per minute | 2026-10-28 |
| Telephony | plivo | noise-cancellation | any | pay-as-you-go | 0.12 INR per minute | 2026-10-28 |
| Telephony | plivo | phone-number | any | pay-as-you-go | 200 INR per month | 2026-10-28 |
| Telephony | retell | retell-twilio | any | pay-as-you-go | 0.015 USD per minute | 2026-10-28 |
| Telephony | telnyx | browser-app-calling | any | pay-as-you-go | 0.002 USD per minute | 2026-10-28 |
| Telephony | telnyx | call-recording | any | pay-as-you-go | 0.002 USD per minute | 2026-10-28 |
| Telephony | telnyx | call-recording-storage | any | pay-as-you-go | 0 USD per minute | 2026-10-28 |
| Telephony | telnyx | conference-calls | any | pay-as-you-go | 0.002 USD per minute | 2026-10-28 |
| Telephony | telnyx | conversation-relay | any | pay-as-you-go | 0.05 USD per minute | 2026-10-28 |
| Telephony | telnyx | decrypted-forking | any | pay-as-you-go | 0.0025 USD per minute | 2026-10-28 |
| Telephony | telnyx | local-number | inbound | pay-as-you-go | 0.002 USD per minute | 2026-10-28 |
| Telephony | telnyx | make-outbound-calls | outbound | pay-as-you-go | 0.002 USD per minute | 2026-10-28 |
| Telephony | telnyx | media-streaming-over-websockets | any | pay-as-you-go | 0.0035 USD per minute | 2026-10-28 |
| Telephony | telnyx | noise-suppression | any | pay-as-you-go | 0.002 USD per minute | 2026-10-28 |
| Telephony | telnyx | noise-suppression-aicoustics | any | pay-as-you-go | 0.003 USD per minute | 2026-10-28 |
| Telephony | telnyx | noise-suppression-krisp | any | pay-as-you-go | 0.005 USD per minute | 2026-10-28 |
| Telephony | telnyx | phone-numbers | any | pay-as-you-go | 1 USD per month | 2026-10-28 |
| Telephony | telnyx | premium-answering-machine-detection | any | pay-as-you-go | 0.0065 USD per call | 2026-10-28 |
| Telephony | telnyx | sip-interface | any | pay-as-you-go | 0.002 USD per minute | 2026-10-28 |
| Telephony | telnyx | standard-answering-machine-detection | any | pay-as-you-go | 0.002 USD per call | 2026-10-28 |
| Telephony | telnyx | toll-free-number | inbound | pay-as-you-go | 0.002 USD per minute | 2026-10-28 |
| Telephony | telnyx | toll-free-numbers | any | pay-as-you-go | 1 USD per month | 2026-10-28 |
| Telephony | twilio | browser-app | inbound, outbound | pay-as-you-go | 0.004 USD per minute | 2026-10-28 |
| Telephony | twilio | byoc-trunking | inbound, outbound | pay-as-you-go | 0.004 USD per minute | 2026-10-28 |
| Telephony | twilio | call-recording | any | pay-as-you-go | 0.0025 USD per minute | 2026-10-28 |
| Telephony | twilio | local-calls | inbound, outbound | pay-as-you-go | 0.0085–0.014 USD per minute | 2026-10-28 |
| Telephony | twilio | local-numbers | any | pay-as-you-go | 1.15 USD per month | 2026-10-28 |
| Telephony | twilio | media-streams | any | pay-as-you-go | 0.0044 USD per minute | 2026-10-28 |
| Telephony | twilio | sip-interface | inbound, outbound | pay-as-you-go | 0.004 USD per minute | 2026-10-28 |
| Telephony | twilio | siprec | any | pay-as-you-go | 0.0044 USD per minute | 2026-10-28 |
| Telephony | twilio | toll-free-calls | inbound, outbound | pay-as-you-go | 0.014–0.022 USD per minute | 2026-10-28 |
| Telephony | twilio | toll-free-numbers | any | pay-as-you-go | 2.15 USD per month | 2026-10-28 |
| Voice agent | bland | bland-agent | any | start, build | 0.12–0.14 USD per minute | 2026-10-28 |
| Voice agent | bland | bland-agent-transfer | any | start, build | 0.04–0.05 USD per minute | 2026-10-28 |
| Voice agent | bolna | bolna-ai | any | pay-as-you-go, pilot-300, pilot-500 | 0.06–500 USD per minute | 2026-10-28 |
| Voice agent | retell | advanced-denoising | any | pay-as-you-go | 0.005 USD per minute | 2026-10-28 |
| Voice agent | retell | ai-quality-assurance | any | pay-as-you-go | 0.1 USD per minute | 2026-10-28 |
| Voice agent | retell | batch-call | any | pay-as-you-go | 0.005 USD per call | 2026-10-28 |
| Voice agent | retell | branded-call | any | pay-as-you-go | 0.1 USD per call | 2026-10-28 |
| Voice agent | retell | knowledge-base | any | pay-as-you-go | 0.005 USD per minute | 2026-10-28 |
| Voice agent | retell | pii-removal | any | pay-as-you-go | 0.01 USD per minute | 2026-10-28 |
| Voice agent | retell | retell-voice-infra | any | pay-as-you-go | 0.055 USD per minute | 2026-10-28 |
| Voice agent | retell | safety-guardrails | any | pay-as-you-go | 0.005 USD per minute | 2026-10-28 |
| Voice agent | retell | voice-agent | any | pay-as-you-go | 0.07 USD per minute | 2026-10-28 |
| Voice agent | vapi | vapi | any | no-success-package | 0.05 USD per minute | 2026-10-28 |
<!-- coverage:end -->

### Not public

These are tracked but publish no price we can read, so they have no
rows. The reason says what would unlock them; `sign-in-required` and
`contact-sales` prices may later come from contributors. Generated from
`data/unavailable.json`.

<!-- not-public:start -->
| Provider | Category | Why | Page | Checked |
|---|---|---|---|---|
| airtel-iq | Telephony | rendered-by-javascript: The page is a script shell ('Loading… Please Wait') with no text. | https://www.airtel.in/business/b2b/airtel-iq/voice | 2026-10-28 |
| bandwidth | Telephony | blocked: Returns 403 Forbidden to automated fetches. | https://www.bandwidth.com/pricing/ | 2026-10-28 |
| exotel | Telephony | contact-sales: Plans page with 'Talk to Sales' and custom plans; no per-minute price in the page text. | https://exotel.com/pricing/ | 2026-10-28 |
| gnani | Speech-to-text, Text-to-speech | sign-in-required: The public page offers demos and custom plans only; prices are shown inside the signed-in dashboard. | https://www.gnani.ai/pricing | 2026-10-28 |
| hume | Text-to-speech | rendered-by-javascript: Pricing page text has no prices. | https://www.hume.ai/pricing | 2026-10-28 |
| murf | Text-to-speech | rendered-by-javascript: The page returns almost no text without a browser. | https://murf.ai/api/pricing | 2026-10-28 |
| ozonetel | Telephony | blocked: Times out or redirects with an empty body for automated fetches. | https://ozonetel.com/pricing/ | 2026-10-28 |
| playht | Text-to-speech | fetch-failed: The site's certificate chain is incomplete, and with that skipped the server disconnects without a response. | https://playht.com/pricing/ | 2026-10-28 |
| resemble | Text-to-speech | pricing-page-not-found: The pricing page lists only detection services; no text-to-speech price on it, and no other pricing page was searched. | https://www.resemble.ai/pricing/ | 2026-10-28 |
| reverie | Speech-to-text, Text-to-speech | pricing-page-not-found: /pricing returns 404 and the homepage links to no pricing page. | https://reverieinc.com/pricing/ | 2026-10-28 |
| synthflow | Voice agent | rendered-by-javascript: The pricing page text holds almost no prices; plans load in the browser. | https://synthflow.ai/pricing | 2026-10-28 |
| tatatele | Telephony | pricing-page-not-found: Smartflo /pricing returns 404; the homepage links only to Microsoft 365 plan pricing. | https://www.tatateleservices.com/ | 2026-10-28 |
| vobiz | Telephony | contact-sales: The pricing data marks India {code:"IN", contactSalesOnly:true}; extra capacity is priced per account in the console. | https://www.vobiz.ai/pricing/?country=IN | 2026-10-28 |
| vonage | Telephony | rendered-by-javascript: Per-minute prices load by country selector; not in the page text. | https://www.vonage.com/communications-apis/voice/pricing/ | 2026-10-28 |
<!-- not-public:end -->

## The files

| File | What is in it |
|---|---|
| `data/stt.json` | Speech-to-text prices, per provider, model, mode and plan |
| `data/tts.json` | Text-to-speech prices |
| `data/agent.json` | Voice-agent platforms, per minute of conversation |
| `data/telephony.json` | Call prices: per country, inbound or outbound, pulse, minimums |
| `data/unavailable.json` | Providers tracked but not priced, and the reason |
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
- **`mode` is one of a fixed list:** `real-time`, `streaming`,
  `websocket`, `batch`, `batch-with-diarization`, `inbound`,
  `outbound`, or `any` when one price covers every mode. Scrapers map
  each page's own words onto it; a word not mapped yet fails that
  provider's run until someone adds it.
- **A volume tier is its own row**, with `volume`: `{"min": 0, "max":
  250000, "unit": "minute"}` (no `max` for the last tier). Its id ends
  in the range, for example `.../pay-as-you-go/0-250000`.
- **A fixed charge is a row whose unit is a period:** renting one phone
  number is a price per 1 `month`.
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
