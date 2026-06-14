import { useMemo, useState } from 'react';
import { getCurrentUser } from '../api';

type MessageThread = {
  id: string;
  name: string;
  lastMessage: string;
  lastTime: string;
  unread: number;
  messages: { sender: 'me' | 'them'; text: string; time: string }[];
};

const defaultThreads: MessageThread[] = [
  {
    id: 'm1',
    name: 'Shruthi Raj',
    lastMessage: 'Tomorrow 8:15 AM works for me.',
    lastTime: '11:54',
    unread: 0,
    messages: [
      { sender: 'them', text: 'Tomorrow 8:15 AM works for me.', time: '11:54' },
      { sender: 'me', text: 'Perfect, see you then!', time: '11:51' },
    ],
  },
  {
    id: 'm2',
    name: 'Arjun Pai',
    lastMessage: 'Sure, I can share the pickup details.',
    lastTime: '10:22',
    unread: 1,
    messages: [
      { sender: 'them', text: 'Sure, I can share the pickup details.', time: '10:22' },
      { sender: 'me', text: 'Can you confirm the route?', time: '10:18' },
    ],
  },
  {
    id: 'm3',
    name: 'Neha Bose',
    lastMessage: 'Yes, I will join the seminar carpool.',
    lastTime: '09:42',
    unread: 0,
    messages: [
      { sender: 'them', text: 'Yes, I will join the seminar carpool.', time: '09:42' },
      { sender: 'me', text: 'Great, I will reserve a seat.', time: '09:39' },
    ],
  },
];

const MessagesPage = () => {
  const user = getCurrentUser();
  const [threads, setThreads] = useState<MessageThread[]>(defaultThreads);
  const [activeThreadId, setActiveThreadId] = useState(defaultThreads[0].id);
  const [draft, setDraft] = useState('');

  const activeThread = useMemo(
    () => threads.find((thread) => thread.id === activeThreadId) ?? defaultThreads[0],
    [activeThreadId, threads]
  );

  const handleSend = () => {
    if (!draft.trim()) return;
    setThreads((current) =>
      current.map((thread) =>
        thread.id === activeThreadId
          ? {
              ...thread,
              lastMessage: draft.trim(),
              lastTime: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              unread: 0,
              messages: [...thread.messages, { sender: 'me', text: draft.trim(), time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }],
            }
          : thread
      )
    );
    setDraft('');
  };

  return (
    <main className="page-shell animate-fade-in">
      <section className="card wide-card">
        <div className="page-title-row">
          <div>
            <h1>Messages</h1>
            <p>Chat with your ride partners and keep plans organized.</p>
          </div>
        </div>
        <div className="connect-layout">
          <aside className="threads-list">
            <div className="list-heading">Recent conversations</div>
            {threads.map((thread) => (
              <button
                key={thread.id}
                className={`thread-card ${thread.id === activeThreadId ? 'active' : ''}`}
                onClick={() => setActiveThreadId(thread.id)}
              >
                <div>
                  <h3>{thread.name}</h3>
                  <p>{thread.lastMessage}</p>
                </div>
                <div className="thread-meta">
                  <span>{thread.lastTime}</span>
                  {thread.unread > 0 && <span className="badge">{thread.unread}</span>}
                </div>
              </button>
            ))}
          </aside>
          <div className="chat-panel">
            <div className="chat-header">
              <div>
                <h2>{activeThread.name}</h2>
                <p>{activeThread.lastMessage}</p>
              </div>
            </div>
            <div className="message-stream">
              {activeThread.messages.map((message, index) => (
                <div key={index} className={`message-bubble ${message.sender === 'me' ? 'sent' : 'received'}`}>
                  <p>{message.text}</p>
                  <span>{message.time}</span>
                </div>
              ))}
            </div>
            <div className="message-input-row">
              <input
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                placeholder="Send a quick update..."
              />
              <button onClick={handleSend} disabled={!draft.trim()}>
                Send
              </button>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
};

export default MessagesPage;
