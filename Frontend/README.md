# Voice Agent Assignment

## Setup
1. Start Redis
2. Run backend with FastAPI
3. Run frontend with Vite

## Features
- Appointment booking
- Conflict checking
- Session memory
- Cross-session memory
- Multilingual detection
- Trace output

## Latency
Log:
- speech_end
- stt_done
- llm_done
- tts_done

Target:
- under 450 ms from speech end to first audio response