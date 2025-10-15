import { useState, useEffect } from 'react';
import {
  collection,
  addDoc,
  updateDoc,
  deleteDoc,
  doc,
  query,
  orderBy,
  onSnapshot,
  Timestamp,
} from 'firebase/firestore';
import { db } from '../firebase';
import { Book, BookFormData } from '../types/Book';
import { useAuth } from '../contexts/AuthContext';

export function useBooks() {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const { currentUser } = useAuth();

  useEffect(() => {
    const q = query(collection(db, 'books'), orderBy('createdAt', 'desc'));
    
    const unsubscribe = onSnapshot(q, (querySnapshot) => {
      const booksData: Book[] = [];
      querySnapshot.forEach((doc) => {
        const data = doc.data();
        booksData.push({
          id: doc.id,
          title: data.title,
          description: data.description,
          userId: data.userId,
          userEmail: data.userEmail,
          createdAt: data.createdAt?.toDate() || new Date(),
          updatedAt: data.updatedAt?.toDate() || new Date(),
        });
      });
      setBooks(booksData);
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const addBook = async (bookData: BookFormData) => {
    if (!currentUser) throw new Error('User must be logged in');
    
    const newBook = {
      ...bookData,
      userId: currentUser.uid,
      userEmail: currentUser.email || '',
      createdAt: Timestamp.now(),
      updatedAt: Timestamp.now(),
    };

    await addDoc(collection(db, 'books'), newBook);
  };

  const updateBook = async (bookId: string, bookData: BookFormData) => {
    if (!currentUser) throw new Error('User must be logged in');
    
    const bookRef = doc(db, 'books', bookId);
    await updateDoc(bookRef, {
      ...bookData,
      updatedAt: Timestamp.now(),
    });
  };

  const deleteBook = async (bookId: string) => {
    if (!currentUser) throw new Error('User must be logged in');
    
    const bookRef = doc(db, 'books', bookId);
    await deleteDoc(bookRef);
  };

  const getUserBooks = () => {
    if (!currentUser) return [];
    return books.filter(book => book.userId === currentUser.uid);
  };

  const getPublicBooks = () => {
    return books;
  };

  return {
    books,
    loading,
    addBook,
    updateBook,
    deleteBook,
    getUserBooks,
    getPublicBooks,
  };
}
