export type Project = {
  name: string;
  description: string | null;
  url: string | null;
  isPrivate: boolean;
  language: string | null;
};

export type ProjectsData = {
  username: string;
  categories: Record<string, string[]>;
  repos: Record<string, Project>;
};
