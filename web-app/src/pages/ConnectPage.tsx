import { useMemo, useState } from 'react';
import { getCurrentUser } from '../api';

type Contact = {
  id: string;
  name: string;
  email: string;
  year: string;
  branch: string;
  mutualRides: number;
  rating: number;
  verified: boolean;
  bio: string;
};

type ChatMessage = {
  sender: 'me' | 'them';
  text: string;
  time: string;
};

const sampleContacts: Contact[] = [
  {
    id: 'c1',
    name: 'Shruthi Raj',
    email: 'shruthi@rvce.edu.in',
    year: '3rd',
    branch: 'CSE',
    mutualRides: 4,
    rating: 4.9,
    verified: true,
    bio: 'Driver with daily Koramangala commute and a friendly music playlist.',
  },
  {
    id: 'c2',
    name: 'Arjun Pai',
    email: 'arjun@rvce.edu.in',
    year: '2nd',
    branch: 'ISE',
    mutualRides: 2,
    rating: 4.7,
    verified: true,
    bio: 'Passenger looking for safe and punctual rides to campus.',
  },
  {
    id: 'c3',
    name: 'Neha Bose',
    email: 'neha@rvce.edu.in',
    year: '4th',
    branch: 'ECE',
    mutualRides: 6,
    rating: 4.8,
    verified: false,
    bio: 'Weekend rider interested in study-group and campus events.',
  },
];

const defaultThreads: Record<string, ChatMessage[]> = {
  c1: [
    { sender: 'them', text: 'Hey! I usually leave around 8:15 AM from Koramangala.', time: '09:10' },
    { sender: 'me', text: 'That sounds perfect. Can I join tomorrow?', time: '09:12' },
  ],
  c2: [
    { sender: 'them', text: 'I need a seat for the 7 AM ride to campus.', time: '08:45' },
    { sender: 'me', text: 'I can share a spot, let me know the pickup.', time: '08:46' },
  ],
  c3: [
    { sender: 'them', text: 'Do you want to carpool for the seminar on Friday?', time: '10:15' },
    { sender: 'me', text: 'Yes, I am in. Let’s coordinate the route.', time: '10:17' },
  ],
};

const storageKey = 'campuspooler_messages';

const ConnectPage = () => {
  const user = getCurrentUser();
  const [activeContactId, setActiveContactId] = useState(sampleContacts[0].id);
  const [messageText, setMessageText] = useState('');
  const [connected, setConnected] = useState<string[]>(() => {
    const saved = localStorage.getItem('campuspooler_connected');
    return saved ? JSON.parse(saved) : [];
  });
  const [threads, setThreads] = useState<Record<string, ChatMessage[]>>(() => {
    const saved = localStorage.getItem(storageKey);
    return saved ? JSON.parse(saved) : defaultThreads;
  });

  const activeContact = useMemo(
    () => sampleContacts.find((contact) => contact.id === activeContactId) ?? sampleContacts[0],
    [activeContactId]
  );

  const handleConnectToggle = (id: string) => {
    const updated = connected.includes(id) ? connected.filter((item) => item !== id) : [...connected, id];
    setConnected(updated);
    localStorage.setItem('campuspooler_connected', JSON.stringify(updated));
  };

  const handleSend = () => {
    if (!messageText.trim()) return;
    const nextMessage: ChatMessage = {
      sender: 'me',
      text: messageText.trim(),
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    const updatedThreads = {
      ...threads,
      [activeContactId]: [...(threads[activeContactId] || []), nextMessage],
    };
    setThreads(updatedThreads);
    localStorage.setItem(storageKey, JSON.stringify(updatedThreads));
    setMessageText('');
  };

  return (
    <main className="page-shell animate-fade-in">
      <section className="card wide-card">
        <div className="page-title-row">
          <div>
            <h1>Connect with riders</h1>
            <p>Build trusted campus connections and chat instantly.</p>
          </div>
        </div>
        <div className="connect-layout">
          <div className="contacts-list">
            <div className="list-heading">Suggested Contacts</div>
            {sampleContacts.map((contact) => (
              <div
                key={contact.id}
                className={`contact-card ${activeContactId === contact.id ? 'active' : ''}`}
                onClick={() => setActiveContactId(contact.id)}
              >
                <div>
                  <h3>{contact.name}</h3>
                  <p>{contact.year} · {contact.branch}</p>
                </div>
                <div className="contact-meta">
                  <span className="tag">{contact.verified ? 'Verified' : 'New'}</span>
                  <span className="small-text">{contact.mutualRides} trips</span>
                </div>
              </div>
            ))}
          </div>

          <div className="chat-panel">
            <div className="chat-header">
              <div>
                <h2>{activeContact.name}</h2>
                <p>{activeContact.bio}</p>
              </div>
              <button className={connected.includes(activeContact.id) ? 'secondary' : ''} onClick={() => handleConnectToggle(activeContact.id)}>
                {connected.includes(activeContact.id) ? 'Connected' : 'Connect'}
              </button>
            </div>
            <div className="chat-score">
              <div><strong>Rating</strong> {activeContact.rating.toFixed(1)}</div>
              <div><strong>Email</strong> {activeContact.email}</div>
            </div>
            <div className="message-stream">
              {(threads[activeContact.id] || []).map((message, index) => (
                <div key={`${activeContact.id}-${index}`} className={`message-bubble ${message.sender === 'me' ? 'sent' : 'received'}`}>
                  <p>{message.text}</p>
                  <span>{message.time}</span>
                </div>
              ))}
            </div>
            <div className="message-input-row">
              <input
                value={messageText}
                onChange={(e) => setMessageText(e.target.value)}
                placeholder={`Write to ${activeContact.name}...`}
              />
              <button onClick={handleSend} disabled={!messageText.trim()}>
                Send
              </button>
            </div>
          </div>
        </div>
      </section>
      <section className="card small-highlight-card">
        <div className="home-header">
          <div>
            <h2>Quick tips</h2>
            <p>Use the chat to coordinate pickups, share ride plans, and keep your campus commute smooth.</p>
          </div>
        </div>
      </section>
    </main>
  );
};

export default ConnectPage;
