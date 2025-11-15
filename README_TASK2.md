Project Task 2 — AI Insights Layer
==================================

Objective
---------
Enhance **AI Connector Plus** by introducing an AI Insights Layer that fuses real-time weather data, user mood, and preferred activities to craft natural, friendly, and context-aware recommendations.


Overview
--------
The existing platform already:
- Fetches live weather data from the Open-Meteo API via `WeatherService`.
- Uses `AIService` (OpenAI) to summarize text or describe weather.

Task 2 builds on this foundation with a new recommendation layer that turns raw data into human-like suggestions such as _“It’s a lovely day for a walk in Riyadh 🌤️.”_


Core Features
-------------
1. **Weather Insights**
   - Endpoint: `/insight/weather`
   - Input: `city`
   - Flow: Pull current weather ➜ craft a short, emoji-rich paragraph in a conversational tone.
   - Example: _“It’s a sunny afternoon in Jeddah ☀️ — perfect for a beach walk or an iced coffee!”_

2. **Mood-Based Insights**
   - Endpoint: `/insight/mood`
   - Inputs: `city`, `mood` (e.g., happy, tired, stressed)
   - Flow: Merge weather context with the mood to return empathetic tips.
   - Example: _“You’re feeling tired and it’s a cozy 22°C in Cairo 🌙 — maybe grab a warm drink and unwind indoors.”_

3. **Activity Suggestions**
   - Endpoint: `/insight/activity`
   - Inputs: `city`, `activity_type` (outdoor, workout, shopping, etc.)
   - Flow: Use weather and activity intent to suggest smart plans or alternatives.
   - Example: _“It’s quite warm in Riyadh 🏃 — try an early-morning jog instead of mid-day exercise.”_


Key Deliverables
----------------
- `AIInsightsService`: new layer orchestrating `WeatherService` + `AIService`.
- Three REST endpoints: `/insight/weather`, `/insight/mood`, `/insight/activity`.
- Extended Pydantic schemas covering new request/response fields.
- Structured JSON payloads with clear logging around each request.


Response Format
---------------
Every endpoint should respond with:
- `city`
- `temperature` (and unit)
- AI-generated `insight`, `recommendation`, or `suggestion`
- Optional fields such as `mood`, `activity_type`, or `language`

Example:
```
{
  "city": "Dubai",
  "temperature": 30.5,
  "unit": "°C",
  "activity_type": "outdoor",
  "suggestion": "A sunny day in Dubai ☀️ — ideal for a beach walk before noon!"
}
```


Bonus Enhancements (Implemented)
--------------------------------
1. **Voice Generation** ✅  
   `TTSService` (gTTS) can convert any insight into audio. Responses include the audio filename, and `/audio/{filename}` streams the MP3.

2. **History Tracking** ✅  
   `HistoryManager` persists the latest 10 insights in `history/insights_history.json`, surfaced via `/insight/history` and `/insight/history/stats`.

3. **Multilingual Support** ✅  
   Insights accept a `lang` parameter (`en`, `ar`, `es`, `fr`, etc.), and `AIInsightsService` injects language hints so OpenAI replies in the requested language.


Testing
-------
- Run the FastAPI server (`uvicorn main:app --reload`).
- Visit the interactive docs at `http://localhost:8000/docs` to exercise the new endpoints.
- For audio-enabled responses, ensure `audio_files/` is writable and review the filename returned (e.g., `tts_cb28f1992922ad2ee643cad9e454d308.mp3`).



