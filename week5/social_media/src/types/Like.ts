export interface Like {
  id: string;
  messageId: string;
  userId: string;
  userName: string;
  createdAt: Date;
}

export interface LikeStats {
  count: number;
  likedBy: string[]; // Array of user names or UIDs
  hasLiked: boolean; // Whether the current user has liked it
}
