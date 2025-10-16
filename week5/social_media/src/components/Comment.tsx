import React, { useState } from 'react';
import { Comment as CommentType } from '../types/Comment';
import { useAuth } from '../contexts/AuthContext';
import { Edit2, Trash2, Save, X } from 'lucide-react';
import { updateComment, deleteComment } from '../utils/commentService';

interface CommentProps {
  comment: CommentType;
  onUpdate: () => void;
}

const Comment: React.FC<CommentProps> = ({ comment, onUpdate }) => {
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(comment.content);
  const [loading, setLoading] = useState(false);

  const isOwner = user?.uid === comment.authorId;

  const handleUpdate = async () => {
    if (!editContent.trim()) return;

    setLoading(true);
    try {
      await updateComment(comment.id, { content: editContent.trim() });
      setIsEditing(false);
      onUpdate();
    } catch (error) {
      console.error('Failed to update comment:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this comment?')) return;

    setLoading(true);
    try {
      await deleteComment(comment.id, comment.messageId);
      onUpdate();
    } catch (error) {
      console.error('Failed to delete comment:', error);
    } finally {
      setLoading(false);
    }
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
    <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
      <div className="flex justify-between items-start mb-2">
        <div className="flex-1">
          {isEditing ? (
            <textarea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              className="w-full text-sm border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              rows={2}
              placeholder="Edit comment"
            />
          ) : (
            <p className="text-sm text-gray-800">{comment.content}</p>
          )}
          <div className="flex items-center space-x-2 mt-1 text-xs text-gray-500">
            <span className="font-medium">{comment.authorName}</span>
            <span>•</span>
            <span>{formatDate(comment.createdAt)}</span>
            {comment.updatedAt.getTime() !== comment.createdAt.getTime() && (
              <>
                <span>•</span>
                <span className="text-blue-600">Edited</span>
              </>
            )}
          </div>
        </div>
        
        {isOwner && (
          <div className="flex space-x-1">
            {isEditing ? (
              <>
                <button
                  onClick={handleUpdate}
                  disabled={loading}
                  className="text-green-600 hover:text-green-800 disabled:opacity-50"
                  title="Save"
                >
                  <Save className="h-4 w-4" />
                </button>
                <button
                  onClick={() => {
                    setIsEditing(false);
                    setEditContent(comment.content);
                  }}
                  disabled={loading}
                  className="text-red-600 hover:text-red-800 disabled:opacity-50"
                  title="Cancel"
                >
                  <X className="h-4 w-4" />
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => setIsEditing(true)}
                  disabled={loading}
                  className="text-blue-600 hover:text-blue-800 disabled:opacity-50"
                  title="Edit"
                >
                  <Edit2 className="h-4 w-4" />
                </button>
                <button
                  onClick={handleDelete}
                  disabled={loading}
                  className="text-red-600 hover:text-red-800 disabled:opacity-50"
                  title="Delete"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Comment;
