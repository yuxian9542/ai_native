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
  serverTimestamp
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
    const docRef = await addDoc(collection(db, COMMENTS_COLLECTION), {
      messageId,
      ...data,
      authorId,
      authorName,
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp(),
    });
    console.log('Comment created with ID:', docRef.id);
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

export const deleteComment = async (commentId: string): Promise<void> => {
  const commentRef = doc(db, COMMENTS_COLLECTION, commentId);
  await deleteDoc(commentRef);
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
  const commentsQuery = query(
    collection(db, COMMENTS_COLLECTION),
    where('messageId', '==', messageId),
    orderBy('createdAt', 'asc')
  );
  
  return onSnapshot(commentsQuery, (querySnapshot) => {
    const comments: Comment[] = querySnapshot.docs.map(doc => {
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
    callback(comments);
  });
};
