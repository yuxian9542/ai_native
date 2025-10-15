import React, { useState, useEffect } from 'react';
import { Message } from '../types/Message';
import { Comment } from '../types/Comment';
import { useAuth } from '../contexts/AuthContext';
import { Edit2, Trash2, Save, X, MessageCircle } from 'lucide-react';
import { updateMessage, deleteMessage } from '../utils/messageService';
import { subscribeToComments } from '../utils/commentService';
import CommentForm from './CommentForm';
import CommentComponent from './Comment';
import LikeButton from './LikeButton';

interface MessageCardProps {
  message: Message;
  onUpdate: () => void;
}

const MessageCard: React.FC<MessageCardProps> = ({ message, onUpdate }) => {
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(message.title);
  const [editContent, setEditContent] = useState(message.content);
  const [loading, setLoading] = useState(false);
  const [showComments, setShowComments] = useState(false);
  const [comments, setComments] = useState<Comment[]>([]);

  const isOwner = user?.uid === message.authorId;

  useEffect(() => {
    if (!showComments) return;

    const unsubscribe = subscribeToComments(message.id, (newComments) => {
      setComments(newComments);
    });

    return () => unsubscribe();
  }, [message.id, showComments]);

  const handleUpdate = async () => {
    if (!editTitle.trim() || !editContent.trim()) return;
    
    setLoading(true);
    try {
      await updateMessage(message.id, {
        title: editTitle.trim(),
        content: editContent.trim(),
      });
      setIsEditing(false);
      onUpdate();
    } catch (error) {
      console.error('Failed to update message:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this message?')) return;
    
    setLoading(true);
    try {
      await deleteMessage(message.id);
      onUpdate();
    } catch (error) {
      console.error('Failed to delete message:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setEditTitle(message.title);
    setEditContent(message.content);
    setIsEditing(false);
  };

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          {isEditing ? (
            <input
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              className="w-full text-xl font-semibold text-gray-900 border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Message title"
            />
          ) : (
            <h3 className="text-xl font-semibold text-gray-900">{message.title}</h3>
          )}
          <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
            <span className="font-medium">{message.authorName}</span>
            <span>•</span>
            <span>{formatDate(message.createdAt)}</span>
            {message.updatedAt.getTime() !== message.createdAt.getTime() && (
              <>
                <span>•</span>
                <span className="text-blue-600">Edited</span>
              </>
            )}
          </div>
        </div>
        
        {isOwner && (
          <div className="flex space-x-2">
            {isEditing ? (
              <>
                <button
                  onClick={handleUpdate}
                  disabled={loading || !editTitle.trim() || !editContent.trim()}
                  className="p-2 text-green-600 hover:text-green-700 disabled:opacity-50"
                >
                  <Save className="h-4 w-4" />
                </button>
                <button
                  onClick={handleCancel}
                  disabled={loading}
                  className="p-2 text-gray-500 hover:text-gray-700"
                >
                  <X className="h-4 w-4" />
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => setIsEditing(true)}
                  className="p-2 text-blue-600 hover:text-blue-700"
                >
                  <Edit2 className="h-4 w-4" />
                </button>
                <button
                  onClick={handleDelete}
                  disabled={loading}
                  className="p-2 text-red-600 hover:text-red-700 disabled:opacity-50"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </>
            )}
          </div>
        )}
      </div>
      
      <div className="text-gray-700">
        {isEditing ? (
          <textarea
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            rows={4}
            placeholder="Message content"
          />
        ) : (
          <p className="whitespace-pre-wrap">{message.content}</p>
        )}
      </div>

      {/* Like and Comment Actions */}
      <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center space-x-4">
          <LikeButton messageId={message.id} onLikeUpdate={onUpdate} />
          
          <button
            onClick={() => setShowComments(!showComments)}
            className="flex items-center space-x-1 text-gray-400 hover:text-blue-600 transition-colors"
          >
            <MessageCircle className="h-4 w-4" />
            <span className="text-sm">{message.commentCount} comments</span>
          </button>
        </div>
      </div>

      {/* Comments Section */}
      {showComments && (
        <div className="mt-4 space-y-3">
          <CommentForm 
            messageId={message.id} 
            onCommentCreated={() => {
              onUpdate();
            }} 
          />
          
          <div className="text-sm text-gray-500">
            {comments.length === 0 ? 'No comments yet' : `${comments.length} comment${comments.length === 1 ? '' : 's'}`}
          </div>
          
          {comments.length > 0 && (
            <div className="space-y-2">
              {comments.map((comment) => (
                <CommentComponent
                  key={comment.id}
                  comment={comment}
                  onUpdate={() => {
                    onUpdate();
                  }}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MessageCard;
