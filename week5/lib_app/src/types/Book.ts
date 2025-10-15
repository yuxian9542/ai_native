export interface Book {
  id: string;
  title: string;
  description: string;
  userId: string;
  userEmail: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface BookFormData {
  title: string;
  description: string;
}
