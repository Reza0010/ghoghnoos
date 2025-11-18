import React from 'react';
import { Trash2, Tags, Star, FileDown, X } from './icons';
import { useTranslation } from '../contexts/LanguageContext';

interface BulkActionBarProps {
  selectedCount: number;
  onDelete: () => void;
  onAddTags: () => void;
  onChangeRating: () => void;
  onExport: () => void;
  onCancel: () => void;
}

const BulkActionBar: React.FC<BulkActionBarProps> = ({ 
    selectedCount, 
    onDelete, 
    onAddTags, 
    onChangeRating,
    onExport,
    onCancel 
}) => {
    const { t } = useTranslation();

    const actionButtons = [
        { label: t('buttons.delete'), icon: Trash2, handler: onDelete, color: 'text-dark-danger hover:bg-dark-danger/10' },
        { label: t('buttons.addTags'), icon: Tags, handler: onAddTags, color: 'text-dark-accent hover:bg-dark-accent/10' },
        { label: t('buttons.changeRating'), icon: Star, handler: onChangeRating, color: 'text-dark-warn hover:bg-dark-warn/10' },
        { label: t('buttons.export'), icon: FileDown, handler: onExport, color: 'text-dark-secondary hover:bg-dark-secondary/10' },
    ];

    return (
        <div className="fixed bottom-5 left-1/2 -translate-x-1/2 bg-white dark:bg-dark-surface shadow-2xl rounded-full p-2 flex items-center gap-2 z-30 animate-slide-in-up">
            <div className="px-4 py-2 bg-dark-primary text-white rounded-full font-semibold text-sm">
                {t('bulkActions.selected', { count: selectedCount })}
            </div>
            <div className="flex items-center gap-1">
                {actionButtons.map(btn => (
                    <button key={btn.label} onClick={btn.handler} title={btn.label} className={`p-3 rounded-full transition-colors ${btn.color}`}>
                        <btn.icon className="w-5 h-5" />
                    </button>
                ))}
            </div>
            <div className="h-8 border-l border-gray-200 dark:border-dark-overlay mx-1"></div>
            <button onClick={onCancel} title={t('buttons.cancelSelection')} className="p-3 rounded-full hover:bg-gray-200 dark:hover:bg-dark-overlay transition-colors">
                <X className="w-5 h-5 text-gray-500 dark:text-dark-subtext" />
            </button>
        </div>
    );
};

export default BulkActionBar;
