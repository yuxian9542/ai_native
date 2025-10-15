import { useState } from 'react';
import { Book } from '../types/Book';
import { useAuth } from '../contexts/AuthContext';
import { useBooks } from '../hooks/useBooks';
import { BookForm } from './BookForm';
import { Edit, Trash2, User, Calendar } from 'lucide-react';

interface BookCardProps {
  book: Book;
}

export function BookCard({ book }: BookCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const { currentUser } = useAuth();
  const { updateBook, deleteBook } = useBooks();

  const isOwner = currentUser && book.userId === currentUser.uid;

  const handleUpdate = async (bookData: any) => {
    await updateBook(book.id, bookData);
    setIsEditing(false);
  };

  const handleDelete = async () => {
    if (window.confirm('确定要删除这本图书吗？')) {
      await deleteBook(book.id);
    }
  };

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  if (isEditing) {
    return (
      <BookForm
        onSubmit={handleUpdate}
        onCancel={() => setIsEditing(false)}
        initialData={{ title: book.title, description: book.description }}
        isEditing={true}
      />
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-xl font-semibold text-gray-900 line-clamp-2">
          {book.title}
        </h3>
        {isOwner && (
          <div className="flex space-x-2 ml-4">
            <button
              onClick={() => setIsEditing(true)}
              className="text-indigo-600 hover:text-indigo-800 p-1"
              title="编辑"
            >
              <Edit className="h-4 w-4" />
            </button>
            <button
              onClick={handleDelete}
              className="text-red-600 hover:text-red-800 p-1"
              title="删除"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        )}
      </div>

      <p className="text-gray-700 mb-4 line-clamp-3">
        {book.description}
      </p>

      <div className="flex items-center justify-between text-sm text-gray-500">
        <div className="flex items-center">
          <User className="h-4 w-4 mr-1" />
          <span>{book.userEmail}</span>
        </div>
        <div className="flex items-center">
          <Calendar className="h-4 w-4 mr-1" />
          <span>{formatDate(book.createdAt)}</span>
        </div>
      </div>
    </div>
  );
}
