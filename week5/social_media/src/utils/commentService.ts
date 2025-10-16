import {
  collection,
  addDoc,
  updateDoc,
  deleteDoc,
  doc,
  query,
  orderBy,
  where,
  onSnapshot,
  getDocs,
  serverTimestamp,
  increment
} from 'firebase/firestore';
import { db } from '../firebase';
import { Comment, CreateCommentData, UpdateCommentData } from '../types/Comment';

const COMMENTS_COLLECTION = 'comments';

export const createComment = async (
  messageId: string,
  data: CreateCommentData,
  authorId: string,
  authorName: string
): Promise<void> => {
  console.log('Creating comment in Firestore:', {
    messageId,
    content: data.content,
    authorId,
    authorName
  });
  
  try {
    // Create the comment
    const docRef = await addDoc(collection(db, COMMENTS_COLLECTION), {
      messageId,
      ...data,
      authorId,
      authorName,
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp(),
    });
    console.log('Comment created with ID:', docRef.id);
    
    // Update the message's comment count
    const messageRef = doc(db, 'messages', messageId);
    await updateDoc(messageRef, {
      commentCount: increment(1)
    });
    console.log('Updated message comment count');
  } catch (error) {
    console.error('Error creating comment:', error);
    throw error;
  }
};

export const updateComment = async (commentId: string, data: UpdateCommentData): Promise<void> => {
  const commentRef = doc(db, COMMENTS_COLLECTION, commentId);
  await updateDoc(commentRef, {
    ...data,
    updatedAt: serverTimestamp(),
  });
};

export const deleteComment = async (commentId: string, messageId: string): Promise<void> => {
  const commentRef = doc(db, COMMENTS_COLLECTION, commentId);
  await deleteDoc(commentRef);
  
  // Update the message's comment count
  const messageRef = doc(db, 'messages', messageId);
  await updateDoc(messageRef, {
    commentCount: increment(-1)
  });
};

export const getComments = async (messageId: string): Promise<Comment[]> => {
  const commentsQuery = query(
    collection(db, COMMENTS_COLLECTION),
    where('messageId', '==', messageId),
    orderBy('createdAt', 'asc')
  );
  const querySnapshot = await getDocs(commentsQuery);
  
  return querySnapshot.docs.map(doc => {
    const data = doc.data();
    return {
      id: doc.id,
      messageId: data.messageId,
      content: data.content,
      authorId: data.authorId,
      authorName: data.authorName,
      createdAt: data.createdAt?.toDate() || new Date(),
      updatedAt: data.updatedAt?.toDate() || new Date(),
    };
  });
};

export const subscribeToComments = (
  messageId: string,
  callback: (comments: Comment[]) => void
): (() => void) => {
  console.log('Setting up comment subscription for messageId:', messageId);
  
  const commentsQuery = query(
    collection(db, COMMENTS_COLLECTION),
    where('messageId', '==', messageId),
    orderBy('createdAt', 'asc')
  );
  
  return onSnapshot(commentsQuery, (querySnapshot) => {
    console.log('Comment snapshot received, docs count:', querySnapshot.docs.length);
    
    const comments: Comment[] = querySnapshot.docs.map(doc => {
      const data = doc.data();
      console.log('Comment data:', data);
      return {
        id: doc.id,
        messageId: data.messageId,
        content: data.content,
        authorId: data.authorId,
        authorName: data.authorName,
        createdAt: data.createdAt?.toDate() || new Date(),
        updatedAt: data.updatedAt?.toDate() || new Date(),
      };
    });
    
    console.log('Processed comments:', comments);
    callback(comments);
  }, (error) => {
    console.error('Comment subscription error:', error);
  });
};

// Debug function to manually check comments
export const debugGetComments = async (messageId: string): Promise<void> => {
  console.log('=== DEBUG: Getting comments for messageId:', messageId);
  
  try {
    const commentsQuery = query(
      collection(db, COMMENTS_COLLECTION),
      where('messageId', '==', messageId)
    );
    
    const querySnapshot = await getDocs(commentsQuery);
    console.log('DEBUG: Found', querySnapshot.docs.length, 'comments');
    
    querySnapshot.docs.forEach((doc, index) => {
      console.log(`DEBUG: Comment ${index + 1}:`, {
        id: doc.id,
        data: doc.data()
      });
    });
  } catch (error) {
    console.error('DEBUG: Error getting comments:', error);
  }
};
