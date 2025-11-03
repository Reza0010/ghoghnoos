import React, { useState } from 'react';
import { Clipboard } from 'lucide-react';
import { useProxyStore } from '../store';
import { parseConfig } from '../services/configParser';

const MultiInputSmartBox: React.FC = () => {
  const [text, setText] = useState('');
  const addConfig = useProxyStore((state) => state.addConfig);

  const handleInputChange = (newText: string) => {
    setText(newText);
    const config = parseConfig(newText);
    if (config) {
      addConfig(config);
      setText(''); // Clear the input on successful parse
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    const pastedText = e.clipboardData.getData('text');
    handleInputChange(pastedText);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        handleInputChange(event.target?.result as string);
      };
      reader.readAsText(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const importFromClipboard = async () => {
    const clipboardText = await navigator.clipboard.readText();
    handleInputChange(clipboardText);
  };

  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md">
      <textarea
        className="w-full h-40 p-2 border rounded-md bg-gray-100 dark:bg-gray-700"
        placeholder="Paste config link, drag & drop file, or paste config text here..."
        value={text}
        onChange={(e) => handleInputChange(e.target.value)}
        onPaste={handlePaste}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      />
      <button
        className="mt-2 flex items-center px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
        onClick={importFromClipboard}
      >
        <Clipboard size={18} className="mr-2" />
        Import From Clipboard
      </button>
    </div>
  );
};

export default MultiInputSmartBox;
