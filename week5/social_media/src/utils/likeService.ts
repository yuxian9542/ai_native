import {
  collection,
  addDoc,
  deleteDoc,
  query,
  where,
  getDocs,
  onSnapshot,
  serverTimestamp
} from 'firebase/firestore';
import { db } from '../firebase';
import { LikeStats } from '../types/Like';

const LIKES_COLLECTION = 'likes';

export const toggleLike = async (
  messageId: string,
  userId: string,
  userName: string,
  hasLiked: boolean
): Promise<void> => {
  const likesRef = collection(db, LIKES_COLLECTION);
  const likeQuery = query(likesRef, where('messageId', '==', messageId), where('userId', '==', userId));
  const snapshot = await getDocs(likeQuery);

  if (hasLiked) {
    // User has liked, so unlike
    snapshot.forEach(async (doc) => {
      await deleteDoc(doc.ref);
    });
  } else {
    // User has not liked, so like
    await addDoc(likesRef, {
      messageId,
      userId,
      userName,
      createdAt: serverTimestamp(),
    });
  }
};

export const getLikeStatus = async (messageId: string, userId: string): Promise<boolean> => {
  const likesRef = collection(db, LIKES_COLLECTION);
  const likeQuery = query(likesRef, where('messageId', '==', messageId), where('userId', '==', userId));
  const snapshot = await getDocs(likeQuery);
  return !snapshot.empty;
};

export const subscribeToLikeStats = (
  messageId: string,
  userId: string | null,
  callback: (stats: LikeStats) => void
): (() => void) => {
  const likesQuery = query(
    collection(db, LIKES_COLLECTION),
    where('messageId', '==', messageId)
  );
  
  return onSnapshot(likesQuery, (querySnapshot) => {
    const likes = querySnapshot.docs.map(doc => ({
      id: doc.id,
      messageId: doc.data().messageId,
      userId: doc.data().userId,
      userName: doc.data().userName,
      createdAt: doc.data().createdAt?.toDate() || new Date(),
    }));
    
    const hasLiked = userId ? likes.some(like => like.userId === userId) : false;
    const likedBy = likes.map(like => like.userName);
    
    callback({
      count: likes.length,
      likedBy,
      hasLiked
    });
  });
};
