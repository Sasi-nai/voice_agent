from Backend.App.orchestrator import detect_language
samples=["मैं अपॉइंटमेंट बुक करना चाहता हूँ doctor 2 2026-06-13T09:30","நான் நியமனம் செய்ய விரும்புகிறேன் doctor 2 2026-06-14T12:00","I want to book an appointment with doctor 2 at 2026-06-12T10:00"]
for s in samples:
    print(s)
    print(detect_language(s))