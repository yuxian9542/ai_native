import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { createComment } from '../utils/commentService';
import { Send } from 'lucide-react';

interface CommentFormProps {
  messageId: string;
  onCommentCreated: () => void;
}

const CommentForm: React.FC<CommentFormProps> = ({ messageId, onCommentCreated }) => {
  const { user } = useAuth();
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    console.log('Comment form submitted:', { content, user: user?.uid, messageId });
    
    if (!content.trim() || !user) {
      console.log('Validation failed:', { content: content.trim(), user: !!user });
      return;
    }
    
    setLoading(true);
    try {
      console.log('Creating comment...');
      await createComment(
        messageId,
        { content: content.trim() },
        user.uid,
        user.displayName || user.email || 'Anonymous'
      );
      console.log('Comment created successfully');
      setContent('');
      onCommentCreated();
    } catch (error) {
      console.error('Failed to create comment:', error);
      alert(`Failed to create comment: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-center">
        <p className="text-blue-800 text-sm">Please sign in to post comments.</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none text-sm"
          placeholder="Write a comment..."
          required
        />
      </div>
      
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={loading || !content.trim()}
          className="flex items-center space-x-1 px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send className="h-3 w-3" />
          <span>{loading ? 'Posting...' : 'Comment'}</span>
        </button>
      </div>
    </form>
  );
};

export default CommentForm;
