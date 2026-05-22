import json
import random
import re
import time
import urllib.request
from datetime import datetime, timedelta

URL = 'http://127.0.0.1:8000/agent/message'
HEALTH_URL = 'http://127.0.0.1:8000/health'
LOG_FILE = 'automated_tests.log'
SESSION_ID = f'auto-session-{int(time.time())}'


def wait_for_server(retries=5, delay=1):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(HEALTH_URL)
            with urllib.request.urlopen(req, timeout=5):
                return True
        except Exception:
            if attempt < retries - 1:
                time.sleep(delay)
    return False


def post(text):
    payload = {'session_id': SESSION_ID, 'patient_id': 1, 'text': text}
    req = urllib.request.Request(URL, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as res:
        return json.load(res)


def extract_booking_id(reply_text):
    m = re.search(r"(\d+)", reply_text)
    return int(m.group(1)) if m else None


def log(message):
    timestamp = datetime.utcnow().isoformat() + 'Z'
    line = f'[{timestamp}] {message}'
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def assert_equal(value, expected, message):
    if value != expected:
        raise AssertionError(f'{message}: expected {expected!r}, got {value!r}')


def make_datetime(days_offset: int, hour: int, minute: int = 0):
    base_date = datetime.utcnow().date() + timedelta(days=3650 + days_offset)
    return f'{base_date.isoformat()}T{hour:02d}:{minute:02d}'

random_base = random.randint(3, 30)
book_time = make_datetime(random_base, 9, 0)
book_conflict_time = book_time
book_time2 = make_datetime(random_base + 1, 10, 0)
hin_book_time = make_datetime(random_base + 2, 9, 30)
tam_book_time = make_datetime(random_base + 3, 11, 30)
reschedule_time = make_datetime(random_base + 4, 15, 0)


tests = [
    ('book_en', f'I want to book an appointment with doctor 2 at {book_time}', 'book_success', 'en'),
    ('book_conflict', f'I want to book an appointment with doctor 2 at {book_conflict_time}', 'book_failed:slot_conflict', 'en'),
    ('book_en2', f'I want to book an appointment with doctor 2 at {book_time2}', 'book_success', 'en'),
    ('hin_book', f'मैं अपॉइंटमेंट बुक करना चाहता हूँ doctor 2 {hin_book_time}', 'book_success', 'hi'),
    ('tam_book', f'நான் நியமனம் செய்ய விரும்புகிறேன் doctor 2 {tam_book_time}', 'book_success', 'ta'),
    ('fallback', 'hello what is up', 'fallback', 'en'),
]

created_ids = []
results = []

with open(LOG_FILE, 'w', encoding='utf-8') as f:
    f.write(f'Automated test run started at {datetime.utcnow().isoformat()}Z\n')

if not wait_for_server():
    raise SystemExit('Backend did not respond to health checks. Start the server and retry.')

for name, text, expected_trace, expected_language in tests:
    log(f'---')
    log(f'Test: {name}')
    log(f'Request: {text}')
    try:
        res = post(text)
    except Exception as e:
        log(f'Request failed: {e}')
        results.append((name, False, str(e)))
        continue

    log(f'Response: {json.dumps(res, indent=2, ensure_ascii=False)}')
    trace = res.get('trace', [])
    language = res.get('language')
    reply = res.get('reply', '')

    assert_equal(language, expected_language, f'{name} language mismatch')

    if expected_trace == 'fallback':
        assert_equal(reply, 'Sorry, I didn’t understand. Please say book, cancel, or reschedule.', f'{name} fallback reply')
        assert_equal(trace, ['fallback'], f'{name} trace mismatch')
    elif expected_trace.startswith('book_success'):
        assert 'Appointment booked successfully' in reply, f'{name} expected booking success'
        assert expected_language == language, f'{name} expected language {expected_language}'
        booking_id = extract_booking_id(reply)
        if booking_id is None:
            raise AssertionError(f'{name} booking id not found in reply')
        created_ids.append(booking_id)
    elif expected_trace == 'book_failed:slot_conflict':
        assert 'That slot is already booked' in reply, f'{name} expected slot conflict reply'
        assert trace == ['book_failed:slot_conflict'], f'{name} trace mismatch: {trace}'
    else:
        raise AssertionError(f'Unknown expected_trace for {name}: {expected_trace}')

    results.append((name, True, 'ok'))

if created_ids:
    first = created_ids[0]
    log('---')
    log(f'Test: cancel created booking {first}')
    try:
        res = post(f'cancel appointment {first}')
        log(f'Response: {json.dumps(res, indent=2, ensure_ascii=False)}')
        assert_equal(res.get('trace'), ['cancel_success'], 'cancel trace mismatch')
        assert 'Appointment' in res.get('reply', ''), 'cancel reply invalid'
        results.append(('cancel', True, 'ok'))
    except Exception as e:
        log(f'Cancel failed: {e}')
        results.append(('cancel', False, str(e)))

if len(created_ids) > 1:
    second = created_ids[1]
    log('---')
    log(f'Test: reschedule created booking {second}')
    try:
        res = post(f'reschedule appointment {second} to {reschedule_time}')
        log(f'Response: {json.dumps(res, indent=2, ensure_ascii=False)}')
        assert_equal(res.get('trace'), ['reschedule_success'], 'reschedule trace mismatch')
        results.append(('reschedule', True, 'ok'))
    except Exception as e:
        log(f'Reschedule failed: {e}')
        results.append(('reschedule', False, str(e)))

success = all(status for _, status, _ in results)
log('---')
log(f'Automated tests finished. Success={success}')
for name, status, details in results:
    log(f'{name}: {status} {details}')

if not success:
    raise SystemExit('Some automated tests failed. See automated_tests.log for details.')
