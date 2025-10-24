import React from 'react';
import { Prompt } from '../types';

interface PromptFormProps {
  prompt?: Prompt | null;
  onSave: (prompt: Omit<Prompt, 'id' | 'createdAt' | 'updatedAt'>) => void;
  onCancel: () => void;
}

export const PromptForm: React.FC<PromptFormProps> = ({ prompt, onSave, onCancel }) => {
  // This is a placeholder - the actual form logic is in PromptStudio
  // This component exists for compatibility with existing imports
  return (
    <div className="main-content">
      <div className="max-w-2xl mx-auto">
        <div className="card">
          <div className="card-body text-center py-12">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Redirecting to Prompt Studio...
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              The form functionality has been moved to the Prompt Studio for a better experience.
            </p>
            <button onClick={onCancel} className="btn btn-primary">
              Go to Studio
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};