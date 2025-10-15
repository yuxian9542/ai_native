export interface Message {
  id: string;
  title: string;
  content: string;
  authorId: string;
  authorName: string;
  createdAt: Date;
  updatedAt: Date;
  commentCount: number;
  likeCount: number;
}

export interface CreateMessageData {
  title: string;
  content: string;
}

export interface UpdateMessageData {
  title?: string;
  content?: string;
}
