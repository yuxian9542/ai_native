import { useState } from 'react';
import { useBooks } from '../hooks/useBooks';
import { BookCard } from '../components/BookCard';
import { BookOpen, Search, LogIn } from 'lucide-react';

export function PublicHomePage() {
  const { loading, getPublicBooks } = useBooks();
  const [searchTerm, setSearchTerm] = useState('');

  const publicBooks = getPublicBooks();
  const filteredBooks = publicBooks.filter(book =>
    book.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    book.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <BookOpen className="h-12 w-12 text-indigo-600 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            图书管理系统
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto mb-6">
            浏览大家分享的图书收藏，发现更多精彩内容
          </p>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-md mx-auto">
            <div className="flex items-center justify-center text-blue-800">
              <LogIn className="h-5 w-5 mr-2" />
              <span className="text-sm font-medium">
                登录后可以添加和管理您自己的图书
              </span>
            </div>
          </div>
        </div>

        {/* Search Bar */}
        <div className="max-w-md mx-auto mb-8">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="搜索图书名称或简介..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Books Grid */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">
              所有图书 ({filteredBooks.length})
            </h2>
          </div>

          {filteredBooks.length === 0 ? (
            <div className="text-center py-12">
              <BookOpen className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {searchTerm ? '没有找到匹配的图书' : '还没有图书'}
              </h3>
              <p className="text-gray-500">
                {searchTerm 
                  ? '尝试使用不同的搜索词'
                  : '登录后可以添加第一本图书'
                }
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredBooks.map((book) => (
                <BookCard key={book.id} book={book} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
