/**
 * Form Auto-save Utility - High Impact UX Enhancement
 *
 * Provides automatic form data persistence with recovery capabilities
 */

export interface AutoSaveConfig {
  key: string;
  debounceMs?: number;
  excludeFields?: string[];
  onSave?: (data: AutoSaveData) => void;
  onRestore?: (data: AutoSaveData) => void;
}

export interface AutoSaveData {
  timestamp: number;
  data: Record<string, unknown>;
  userAgent: string;
}

export class FormAutoSave {
  private config: AutoSaveConfig;
  private saveTimeout: number | null = null;
  private lastSavedData: string = '';

  constructor(config: AutoSaveConfig) {
    this.config = {
      debounceMs: 2000,
      excludeFields: ['password'],
      ...config,
    };
  }

  /**
   * Save form data to localStorage with debouncing
   */
  save(formData: Record<string, unknown>): void {
    // Clear existing timeout
    if (this.saveTimeout) {
      clearTimeout(this.saveTimeout);
    }

    // Filter out excluded fields
    const filteredData = this.filterData(formData);
    const dataString = JSON.stringify(filteredData);

    // Skip save if data hasn't changed
    if (dataString === this.lastSavedData) {
      return;
    }

    // Debounced save
    this.saveTimeout = window.setTimeout(() => {
      const saveData: AutoSaveData = {
        timestamp: Date.now(),
        data: filteredData,
        userAgent: navigator.userAgent,
      };

      try {
        localStorage.setItem(this.config.key, JSON.stringify(saveData));
        this.lastSavedData = dataString;
        this.config.onSave?.(saveData);
      } catch {
        // Failed to auto-save form data
      }
    }, this.config.debounceMs);
  }

  /**
   * Restore form data from localStorage
   */
  restore(): Record<string, unknown> | null {
    try {
      const savedItem = localStorage.getItem(this.config.key);
      if (!savedItem) return null;

      const saveData: AutoSaveData = JSON.parse(savedItem);

      // Check if data is not too old (24 hours)
      const twentyFourHours = 24 * 60 * 60 * 1000;
      if (Date.now() - saveData.timestamp > twentyFourHours) {
        this.clear();
        return null;
      }

      this.config.onRestore?.(saveData);
      return saveData.data;
    } catch {
      // Failed to restore form data
      return null;
    }
  }

  /**
   * Check if there's saved data available
   */
  hasSavedData(): boolean {
    try {
      const savedItem = localStorage.getItem(this.config.key);
      if (!savedItem) return false;

      const saveData: AutoSaveData = JSON.parse(savedItem);
      const twentyFourHours = 24 * 60 * 60 * 1000;

      return Date.now() - saveData.timestamp <= twentyFourHours;
    } catch {
      return false;
    }
  }

  /**
   * Get the timestamp of the last save
   */
  getLastSaveTime(): Date | null {
    try {
      const savedItem = localStorage.getItem(this.config.key);
      if (!savedItem) return null;

      const saveData: AutoSaveData = JSON.parse(savedItem);
      return new Date(saveData.timestamp);
    } catch {
      return null;
    }
  }

  /**
   * Clear saved data
   */
  clear(): void {
    localStorage.removeItem(this.config.key);
    this.lastSavedData = '';
    if (this.saveTimeout) {
      clearTimeout(this.saveTimeout);
      this.saveTimeout = null;
    }
  }

  /**
   * Filter out excluded fields
   */
  private filterData(data: Record<string, unknown>): Record<string, unknown> {
    const filtered: Record<string, unknown> = {};

    for (const [key, value] of Object.entries(data)) {
      if (!this.config.excludeFields?.includes(key)) {
        // Only save non-empty values
        if (value !== '' && value !== null && value !== undefined) {
          filtered[key] = value;
        }
      }
    }

    return filtered;
  }

  /**
   * Destroy the instance and clean up
   */
  destroy(): void {
    if (this.saveTimeout) {
      clearTimeout(this.saveTimeout);
    }
  }
}

/**
 * Create and configure an auto-save instance
 */
export function createAutoSave(config: AutoSaveConfig): FormAutoSave {
  return new FormAutoSave(config);
}

/**
 * Format time ago string for recovery notice
 */
export function formatTimeAgo(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins} minute${diffMins === 1 ? '' : 's'} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours === 1 ? '' : 's'} ago`;

  return date.toLocaleDateString();
}
