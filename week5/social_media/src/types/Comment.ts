export interface Comment {
  id: string;
  messageId: string;
  authorId: string;
  authorName: string;
  content: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateCommentData {
  content: string;
}

export interface UpdateCommentData {
  content: string;
}
