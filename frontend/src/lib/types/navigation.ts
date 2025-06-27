// Navigation types for mobile-first interface
export interface NavItem {
  path: string;
  label: string;
  icon: string;
}

export interface NavContext {
  currentPath: string;
  isActive: (path: string) => boolean;
}
