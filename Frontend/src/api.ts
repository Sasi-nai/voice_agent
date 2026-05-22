export async function sendMessage(text: string) {
  const res = await fetch("http://localhost:8000/agent/message", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: "demo-session", patient_id: 1, text }),
  });
  return res.json();
}