import {
  collection,
  addDoc,
  updateDoc,
  deleteDoc,
  doc,
  getDocs,
  query,
  orderBy,
  onSnapshot,
  serverTimestamp
} from 'firebase/firestore';
import { db } from '../firebase';
import { Message, CreateMessageData, UpdateMessageData } from '../types/Message';

const MESSAGES_COLLECTION = 'messages';

export const createMessage = async (data: CreateMessageData, authorId: string, authorName: string): Promise<void> => {
  await addDoc(collection(db, MESSAGES_COLLECTION), {
    ...data,
    authorId,
    authorName,
    createdAt: serverTimestamp(),
    updatedAt: serverTimestamp(),
    commentCount: 0,
    likeCount: 0,
  });
};

export const updateMessage = async (messageId: string, data: UpdateMessageData): Promise<void> => {
  const messageRef = doc(db, MESSAGES_COLLECTION, messageId);
  await updateDoc(messageRef, {
    ...data,
    updatedAt: serverTimestamp(),
  });
};

export const deleteMessage = async (messageId: string): Promise<void> => {
  const messageRef = doc(db, MESSAGES_COLLECTION, messageId);
  await deleteDoc(messageRef);
};

export const getMessages = async (): Promise<Message[]> => {
  const messagesQuery = query(collection(db, MESSAGES_COLLECTION), orderBy('createdAt', 'desc'));
  const querySnapshot = await getDocs(messagesQuery);
  
  return querySnapshot.docs.map(doc => {
    const data = doc.data();
    return {
      id: doc.id,
      title: data.title,
      content: data.content,
      authorId: data.authorId,
      authorName: data.authorName,
      createdAt: data.createdAt?.toDate() || new Date(),
      updatedAt: data.updatedAt?.toDate() || new Date(),
      commentCount: data.commentCount || 0,
      likeCount: data.likeCount || 0,
    };
  });
};

export const subscribeToMessages = (callback: (messages: Message[]) => void): (() => void) => {
  const messagesQuery = query(collection(db, MESSAGES_COLLECTION), orderBy('createdAt', 'desc'));
  
  return onSnapshot(messagesQuery, (querySnapshot) => {
    const messages: Message[] = querySnapshot.docs.map(doc => {
      const data = doc.data();
      return {
        id: doc.id,
        title: data.title,
        content: data.content,
        authorId: data.authorId,
        authorName: data.authorName,
        createdAt: data.createdAt?.toDate() || new Date(),
        updatedAt: data.updatedAt?.toDate() || new Date(),
        commentCount: data.commentCount || 0,
      likeCount: data.likeCount || 0,
      };
    });
    callback(messages);
  });
};
