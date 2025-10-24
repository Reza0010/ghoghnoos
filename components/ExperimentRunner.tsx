import React from 'react';
import { Prompt } from '../types';
import { Beaker, ArrowRight } from './icons';

interface ExperimentRunnerProps {
  prompts: Prompt[];
}

export const ExperimentRunner: React.FC<ExperimentRunnerProps> = ({ prompts }) => {
  return (
    <div className="main-content">
      <div className="max-w-4xl mx-auto">
        <div className="card">
          <div className="card-body text-center py-12">
            <div className="flex items-center justify-center w-16 h-16 bg-gradient-to-br from-green-500 to-blue-600 rounded-full mx-auto mb-4">
              <Beaker size={24} className="text-white" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Experiment Runner
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              This feature has been integrated into the Prompt Lab for a better experience.
            </p>
            <button className="btn btn-primary">
              <ArrowRight size={16} />
              <span className="ml-2">Go to Prompt Lab</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};