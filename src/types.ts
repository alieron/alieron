export type ProjectLanguage = {
  name: string;
  color?: string | null;
  share: number;
};

export type Project = {
  name: string;
  description: string | null;
  url: string | null;
  isPrivate: boolean;
  languages?: ProjectLanguage[];
  topics?: string[];
  language: string | null;
};

export type ProjectsData = {
  username: string;
  categories: Record<string, string[]>;
  repos: Record<string, Project>;
};
