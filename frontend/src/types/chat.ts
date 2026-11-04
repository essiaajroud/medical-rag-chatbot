
export type Source = {
  name?: string;
  title?: string;
  label?: string;
  url?: string;
  href?: string;
};

export type Message = {
  id: number;
  sender: "bot" | "user";
  message: string;
  time: string;
  sources?: Source[];
};
