import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { toggleLike, subscribeToLikeStats } from '../utils/likeService';
import { Heart } from 'lucide-react';

interface LikeButtonProps {
  messageId: string;
  onLikeUpdate: () => void;
}

const LikeButton: React.FC<LikeButtonProps> = ({ messageId, onLikeUpdate }) => {
  const { user } = useAuth();
  const [likeCount, setLikeCount] = useState(0);
  const [hasLiked, setHasLiked] = useState(false);
  const [loading, setLoading] = useState(false);
  const [likedByNames, setLikedByNames] = useState<string[]>([]);

  useEffect(() => {
    const unsubscribe = subscribeToLikeStats(messageId, user?.uid || null, (stats) => {
      setLikeCount(stats.count);
      setHasLiked(stats.hasLiked);
      setLikedByNames(stats.likedBy);
    });
    return () => unsubscribe();
  }, [messageId, user?.uid]);

  const handleToggleLike = async () => {
    if (!user) {
      alert('Please sign in to like posts.');
      return;
    }
    
    setLoading(true);
    try {
      await toggleLike(messageId, user.uid, user.displayName || user.email || 'Anonymous', hasLiked);
      onLikeUpdate(); // Notify parent to refresh message data
    } catch (error) {
      console.error('Failed to toggle like:', error);
    } finally {
      setLoading(false);
    }
  };

  const getLikedByText = () => {
    if (likeCount === 0) return '';
    if (likedByNames.length === 0) return `${likeCount} likes`; // Fallback if names not loaded yet

    const uniqueNames = Array.from(new Set(likedByNames)); // Ensure unique names
    if (uniqueNames.length === 1) {
      return `${uniqueNames[0]} liked this`;
    } else if (uniqueNames.length === 2) {
      return `${uniqueNames[0]} and ${uniqueNames[1]} liked this`;
    } else {
      return `${uniqueNames[0]}, ${uniqueNames[1]} and ${likeCount - 2} others liked this`;
    }
  };

  return (
    <div className="flex items-center space-x-1 group relative">
      <button
        onClick={handleToggleLike}
        disabled={loading || !user}
        className={`flex items-center space-x-1 transition-colors ${
          hasLiked ? 'text-red-500 hover:text-red-600' : 'text-gray-400 hover:text-red-500'
        } disabled:opacity-50 disabled:cursor-not-allowed`}
      >
        <Heart className={`h-4 w-4 ${hasLiked ? 'fill-current' : ''}`} />
        <span className="text-sm">{likeCount}</span>
      </button>
      {likeCount > 0 && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-1 bg-gray-800 text-white text-xs rounded-md opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap pointer-events-none">
          {getLikedByText()}
        </div>
      )}
    </div>
  );
};

export default LikeButton;
