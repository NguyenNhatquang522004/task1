import { DocumentPlusIconSolid } from '@neo4j-ndl/react/icons';
import { useDropzone } from 'react-dropzone';
import { useFileContext } from '../../../context/UsersFiles';
import { useEffect, useState } from 'react';
import { useCredentials } from '../../../context/UserCredentials';
import { CustomFile, CustomFileBase } from '../../../types';
import { chunkSize } from '../../../utils/Constants';
import { uploadAPI } from '../../../utils/FileAPI';
import { v4 as uuidv4 } from 'uuid';
import { LoadingSpinner } from '@neo4j-ndl/react';
import { showErrorToast, showSuccessToast } from '../../../utils/Toasts';
import FolderSelectionModal from './FolderSelectionModal';

export default function DropZoneForSmallLayouts() {
  const { filesData, setFilesData, model } = useFileContext();
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isClicked, setIsClicked] = useState<boolean>(false);
  const { connectionStatus, isReadOnlyUser } = useCredentials();
  const [showFolderModal, setShowFolderModal] = useState<boolean>(false);
  const [currentFile, setCurrentFile] = useState<File | null>(null);
  const [uploadQueue, setUploadQueue] = useState<Array<{file: File, course_code: string, folder_name: string}>>([]);

  const uploadFileInChunks = (file: File, course_code?: string, folder_name?: string) => {
    const totalChunks = Math.ceil(file.size / chunkSize);
    const chunkProgressIncrement = 100 / totalChunks;
    let chunkNumber = 1;
    let start = 0;
    let end = chunkSize;
    const uploadNextChunk = async () => {
      if (chunkNumber <= totalChunks) {
        const chunk = file.slice(start, end);
        const formData = new FormData();
        formData.append('file', chunk);
        formData.append('chunkNumber', chunkNumber.toString());
        formData.append('totalChunks', totalChunks.toString());
        formData.append('originalname', file.name);
        formData.append('model', model);
        
        // Credentials are now handled in uploadAPI function
        
        setIsLoading(true);
        setFilesData((prevfiles) =>
          prevfiles.map((curfile) => {
            if (curfile.name == file.name) {
              return {
                ...curfile,
                status: 'Uploading',
              };
            }
            return curfile;
          })
        );
        try {
          const apiResponse = await uploadAPI(chunk, model, chunkNumber, totalChunks, file.name, course_code, folder_name);
          if (apiResponse?.status === 'Failed') {
            throw new Error(`message:${apiResponse.data.message},fileName:${apiResponse.data.file_name}`);
          } else {
            if (apiResponse.data) {
              setFilesData((prevfiles) =>
                prevfiles.map((curfile) => {
                  if (curfile.name == file.name) {
                    return {
                      ...curfile,
                      uploadprogess: chunkNumber * chunkProgressIncrement,
                    };
                  }
                  return curfile;
                })
              );
            }
            setFilesData((prevfiles) =>
              prevfiles.map((curfile) => {
                if (curfile.name == file.name) {
                  return {
                    ...curfile,
                    uploadprogess: chunkNumber * chunkProgressIncrement,
                  };
                }
                return curfile;
              })
            );
            chunkNumber++;
            start = end;
            if (start + chunkSize < file.size) {
              end = start + chunkSize;
            } else {
              end = file.size + 1;
            }
            uploadNextChunk();
          }
        } catch (error) {
          setIsLoading(false);
          if (error instanceof Error) {
            showErrorToast('Error  Occurred');
          }
          setFilesData((prevfiles) =>
            prevfiles.map((curfile) => {
              if (curfile.name == file.name) {
                return {
                  ...curfile,
                  status: 'Upload Failed',
                  type: `${file.name.substring(file.name.lastIndexOf('.') + 1, file.name.length).toUpperCase()}`,
                };
              }
              return curfile;
            })
          );
        }
      } else {
        setFilesData((prevfiles) =>
          prevfiles.map((curfile) => {
            if (curfile.name == file.name) {
              return {
                ...curfile,
                status: 'New',
                uploadprogess: 100,
                createdAt: new Date(),
              };
            }
            return curfile;
          })
        );
        setIsClicked(false);
        setIsLoading(false);
        showSuccessToast(`${file.name} uploaded successfully`);
      }
    };

    uploadNextChunk();
  };
  const { getRootProps, getInputProps } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.jpeg', '.jpg', '.png', '.svg'],
      'text/html': ['.html'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'application/vnd.ms-powerpoint': ['.pptx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/markdown': ['.md'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    },
    onDrop: (f: Partial<globalThis.File>[]) => {
      onDropHandler(f);
    },
    onDropRejected: (e) => {
      if (e.length) {
        showErrorToast('Failed To Upload, Unsupported file extention');
      }
    },
    disabled: isLoading,
  });

  const onDropHandler = (f: Partial<globalThis.File>[]) => {
    if (f.length > 0) {
      // Open folder selection modal for the first file
      const firstFile = f[0] as File;
      setCurrentFile(firstFile);
      setShowFolderModal(true);
    }
  };

  const handleFolderSelection = (course_code: string, folder_name: string) => {
    if (currentFile) {
      // Add file to upload queue with folder info
      const fileWithMetadata = {
        file: currentFile,
        course_code,
        folder_name
      };
      setUploadQueue([fileWithMetadata]);
      
      // Initialize file data
      const defaultValues: CustomFileBase = {
        processingTotalTime: 0,
        status: 'None',
        nodesCount: 0,
        relationshipsCount: 0,
        model: model,
        fileSource: 'local file',
        uploadProgress: 0,
        processingProgress: undefined,
        retryOption: '',
        retryOptionStatus: false,
        chunkNodeCount: 0,
        chunkRelCount: 0,
        entityNodeCount: 0,
        entityEntityRelCount: 0,
        communityNodeCount: 0,
        communityRelCount: 0,
        createdAt: new Date(),
      };

      const copiedFilesData: CustomFile[] = [...filesData];
      const file = currentFile;
      const filedataIndex = copiedFilesData.findIndex((filedataitem) => filedataitem?.name === file?.name);
      
      if (filedataIndex == -1) {
        copiedFilesData.unshift({
          name: file.name,
          type: `${file.name.substring(file.name.lastIndexOf('.') + 1, file.name.length).toUpperCase()}`,
          size: file.size,
          uploadProgress: file.size && file?.size < chunkSize ? 100 : 0,
          id: uuidv4(),
          ...defaultValues,
        });
      } else {
        const tempFileData = copiedFilesData[filedataIndex];
        copiedFilesData.splice(filedataIndex, 1);
        copiedFilesData.unshift({
          ...tempFileData,
          status: defaultValues.status,
          nodesCount: defaultValues.nodesCount,
          relationshipsCount: defaultValues.relationshipsCount,
          processingTotalTime: defaultValues.processingTotalTime,
          model: defaultValues.model,
          fileSource: defaultValues.fileSource,
          processingProgress: defaultValues.processingProgress,
        });
      }
      
      setFilesData(copiedFilesData);
      setIsClicked(true);
    }
  };
  
  useEffect(() => {
    if (uploadQueue.length > 0) {
      for (let index = 0; index < uploadQueue.length; index++) {
        const { file, course_code, folder_name } = uploadQueue[index];
        const fileData = filesData.find(f => f.name === file.name);
        if (fileData?.status == 'None' && isClicked) {
          uploadFileInChunks(file, course_code, folder_name);
        }
      }
    }
  }, [uploadQueue, filesData, isClicked]);

  return (
    <>
      <div {...getRootProps({ className: 'dropzone' })}>
        <input {...getInputProps()} aria-label='dropzone' disabled={isReadOnlyUser || !connectionStatus} />
        {isLoading ? <LoadingSpinner size='medium' /> : <DocumentPlusIconSolid className='n-size-token-7' />}
      </div>
      
      <FolderSelectionModal
        isOpen={showFolderModal}
        onClose={() => setShowFolderModal(false)}
        onConfirm={handleFolderSelection}
        fileName={currentFile?.name || ''}
      />
    </>
  );
}
