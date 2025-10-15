import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Message } from '../types/Message';
import { subscribeToMessages } from '../utils/messageService';
import Navbar from '../components/Navbar';
import MessageForm from '../components/MessageForm';
import MessageCard from '../components/MessageCard';
import { RefreshCw } from 'lucide-react';

const HomePage: React.FC = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = subscribeToMessages((newMessages) => {
      setMessages(newMessages);
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const handleMessageUpdate = () => {
    // Messages will be updated automatically via the subscription
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="flex items-center justify-center">
            <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
            <span className="ml-2 text-gray-600">Loading messages...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="space-y-6">
          {/* Message Form - only show if user is logged in */}
          {user && (
            <MessageForm onMessageCreated={handleMessageUpdate} />
          )}
          
          {/* Messages List */}
          <div className="space-y-4">
            <h2 className="text-2xl font-bold text-gray-900">
              {messages.length === 0 ? 'No messages yet' : 'All Messages'}
            </h2>
            
            {messages.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">
                  {user ? 'Be the first to post a message!' : 'Sign in to post messages and see what others are sharing.'}
                </p>
              </div>
            ) : (
              messages.map((message) => (
                <MessageCard
                  key={message.id}
                  message={message}
                  onUpdate={handleMessageUpdate}
                />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
