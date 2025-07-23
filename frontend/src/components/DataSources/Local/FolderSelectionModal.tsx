import React, { useState, useEffect } from 'react';
import { Dialog, Select, TextInput, Button } from '@neo4j-ndl/react';
import { getFoldersAPI } from '../../../utils/FileAPI';
import { showErrorToast } from '../../../utils/Toasts';
import { logEnvironmentConfig } from '../../../utils/EnvironmentConfig';

interface FolderSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (course_code: string, folder_name: string) => void;
  fileName: string;
}

interface FolderOption {
  label: string;
  value: string;
}

const FolderSelectionModal: React.FC<FolderSelectionModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  fileName
}) => {
  const [availableFolders, setAvailableFolders] = useState<FolderOption[]>([]);
  const [selectedFolder, setSelectedFolder] = useState<string>('');
  const [courseCode, setCourseCode] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    if (isOpen) {
      // Log environment config for debugging
      logEnvironmentConfig();
      loadAvailableFolders();
    }
  }, [isOpen]);

  const loadAvailableFolders = async () => {
    try {
      setIsLoading(true);
      
      console.log('🔧 Loading folders...');
      const response = await getFoldersAPI();
      console.log('🔧 Folders API response:', response);
      
      if (response?.status === 'Success' && response?.data) {
        const folderOptions: FolderOption[] = response.data.map((folder: string) => ({
          label: folder,
          value: folder
        }));
        console.log('🔧 Folder options:', folderOptions);
        setAvailableFolders(folderOptions);
      } else {
        console.error('🔧 Folders API failed:', response);
        showErrorToast('Failed to load available folders');
      }
    } catch (error) {
      console.error('🔧 Error loading folders:', error);
      showErrorToast('Error loading folders');
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirm = () => {
    if (!selectedFolder.trim()) {
      showErrorToast('Please select a folder');
      return;
    }
    
    onConfirm(courseCode.trim(), selectedFolder);
    handleClose();
  };

  const handleClose = () => {
    setSelectedFolder('');
    setCourseCode('');
    onClose();
  };

  const handleFolderChange = (option: any) => {
    setSelectedFolder(option?.value || '');
  };

  return (
    <Dialog isOpen={isOpen} onClose={handleClose}>
      <Dialog.Content>
        <div className="space-y-4">
          <div className="mb-4">
            <h3 className="text-lg font-semibold mb-2">Select Document Organization</h3>
            <div className="bg-blue-50 p-3 rounded-md">
              <p className="text-sm text-blue-800">
                <strong>File:</strong> {fileName}
              </p>
              <p className="text-sm text-blue-700 mt-1">
                Choose how to organize this document in the knowledge graph.
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Course Code (Optional)
              </label>
              <TextInput
                placeholder="e.g., CMP177, CMP3025..."
                value={courseCode}
                onChange={(e) => setCourseCode(e.target.value)}
                isDisabled={isLoading}
                className="w-full"
              />
              <p className="text-xs text-gray-500 mt-1">
                Enter the course code to group related documents
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Folder Category <span className="text-red-500">*</span>
              </label>
              <Select
                type="select"
                selectProps={{
                  placeholder: isLoading ? 'Loading folders...' : 'Select a folder category',
                  options: availableFolders,
                  onChange: handleFolderChange,
                  value: availableFolders.find(option => option.value === selectedFolder) || null,
                  isDisabled: isLoading
                }}
                className="w-full"
              />
              <p className="text-xs text-gray-500 mt-1">
                Choose the document type for appropriate processing rules
              </p>
            </div>

            <div className="bg-blue-50 p-3 rounded-md">
              <h4 className="text-sm font-medium text-blue-800 mb-2">
                Auto-detection will apply:
              </h4>
              <ul className="text-xs text-blue-700 space-y-1">
                <li>• <strong>"đề cương"</strong> → Course outline schema + specialized instructions</li>
                <li>• <strong>"giáo trình"</strong> → Textbook schema + educational content rules</li>
                <li>• <strong>"tham khảo"</strong> → Reference material schema + general processing</li>
                <li>• <strong>Other folders</strong> → Default schema + basic processing</li>
              </ul>
            </div>
          </div>
        </div>
      </Dialog.Content>
      <Dialog.Actions>
        <Button 
          onClick={handleClose} 
          isDisabled={isLoading}
        >
          Cancel
        </Button>
        <Button 
          onClick={handleConfirm}
          isDisabled={isLoading || !selectedFolder.trim()}
        >
          Upload File
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

export default FolderSelectionModal;
