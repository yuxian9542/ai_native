import React, { useState } from 'react';
import { BookFormData } from '../types/Book';
import { Plus, X } from 'lucide-react';

interface BookFormProps {
  onSubmit: (bookData: BookFormData) => Promise<void>;
  onCancel: () => void;
  initialData?: BookFormData;
  isEditing?: boolean;
}

export function BookForm({ onSubmit, onCancel, initialData, isEditing = false }: BookFormProps) {
  const [formData, setFormData] = useState<BookFormData>(
    initialData || { title: '', description: '' }
  );
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title.trim() || !formData.description.trim()) return;

    setLoading(true);
    try {
      await onSubmit(formData);
      setFormData({ title: '', description: '' });
    } catch (error) {
      console.error('Error submitting book:', error);
    }
    setLoading(false);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          {isEditing ? '编辑图书' : '添加新图书'}
        </h3>
        <button
          onClick={onCancel}
          className="text-gray-400 hover:text-gray-600"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
            图书名称 *
          </label>
          <input
            type="text"
            id="title"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            placeholder="请输入图书名称"
            required
          />
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
            图书简介 *
          </label>
          <textarea
            id="description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            placeholder="请输入图书简介"
            required
          />
        </div>

        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            取消
          </button>
          <button
            type="submit"
            disabled={loading || !formData.title.trim() || !formData.description.trim()}
            className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {loading ? (
              '处理中...'
            ) : (
              <>
                <Plus className="h-4 w-4 mr-1" />
                {isEditing ? '更新' : '添加'}
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
