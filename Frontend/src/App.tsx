import { useState } from "react";
import { sendMessage } from "./api";

export default function App() {
  const [text, setText] = useState("");
  const [reply, setReply] = useState<any>(null);

  const onSend = async () => {
    const data = await sendMessage(text);
    setReply(data);
  };

  return (
    <div style={{ padding: 20, fontFamily: "Arial" }}>
      <h2>Voice Agent Demo</h2>
      <input value={text} onChange={(e) => setText(e.target.value)} style={{ width: 400 }} />
      <button onClick={onSend}>Send</button>
      {reply && (
        <pre style={{ marginTop: 20 }}>{JSON.stringify(reply, null, 2)}</pre>
      )}
    </div>
  );
}