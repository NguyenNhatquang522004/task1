import { Dropzone, Flex, SpotlightTarget, Typography, Button } from '@neo4j-ndl/react';
import { useState, FunctionComponent, useEffect, useRef } from 'react';
import Loader from '../../../utils/Loader';
import { v4 as uuidv4 } from 'uuid';
import { useCredentials } from '../../../context/UserCredentials';
import { useFileContext } from '../../../context/UsersFiles';
import { CustomFile, CustomFileBase } from '../../../types';
import { chunkSize } from '../../../utils/Constants';
import { InformationCircleIconOutline } from '@neo4j-ndl/react/icons';
import { IconButtonWithToolTip } from '../../UI/IconButtonToolTip';
import { showErrorToast, showSuccessToast } from '../../../utils/Toasts';

interface FileWithMetadata extends File {
  folderPath: string;
  courseCode?: string;
  folderName: string;
}

const FolderDropZone: FunctionComponent = () => {
  const { filesData, setFilesData, model } = useFileContext();
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isClicked, setIsClicked] = useState<boolean>(false);
  const { userCredentials } = useCredentials();
  const [selectedFiles, setSelectedFiles] = useState<FileWithMetadata[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Extract course code from filename pattern [XXX] YYY
  const extractCourseCode = (filename: string): string | null => {
    const match = filename.match(/^\[([A-Z0-9]+)\]/);
    return match ? match[1] : null;
  };

  // Process dropped items recursively to find all PDF and DOCX files
  const processDroppedItems = async (items: DataTransferItemList): Promise<FileWithMetadata[]> => {
    const files: FileWithMetadata[] = [];
    
    const processEntry = async (entry: FileSystemEntry, currentPath: string, immediateParent: string): Promise<void> => {
      console.log(`🔍 Processing ${entry.isFile ? 'FILE' : 'DIR'}: ${entry.name}, path: "${currentPath}", parent: "${immediateParent}"`);
      
      if (entry.isFile) {
        const fileEntry = entry as FileSystemFileEntry;
        const fileName = fileEntry.name.toLowerCase();
        
        // Only process PDF and DOCX files
        if (fileName.endsWith('.pdf') || fileName.endsWith('.docx')) {
          return new Promise((resolve) => {
            fileEntry.file((file) => {
              try {
                const fullPath = currentPath + file.name;
                const courseCode = extractCourseCode(currentPath || file.name);
                const folderName = immediateParent; // This is the key fix!
                
                console.log(`📄 FILE RESULT: ${file.name} -> folderName: "${folderName}"`);
                
                const fileWithMetadata: FileWithMetadata = Object.assign(file, {
                  folderPath: fullPath,
                  courseCode: courseCode || undefined,
                  folderName: folderName
                });
                
                files.push(fileWithMetadata);
                resolve();
              } catch (error) {
                console.warn('Error processing file:', file.name, error);
                resolve();
              }
            });
          });
        }
      } else if (entry.isDirectory) {
        const dirEntry = entry as FileSystemDirectoryEntry;
        const dirReader = dirEntry.createReader();
        
        return new Promise((resolve) => {
          dirReader.readEntries(async (entries) => {
            try {
              // Key point: current directory becomes the immediate parent for its children
              const newPath = currentPath + dirEntry.name + '/';
              const newParent = dirEntry.name; // THIS directory is the parent for children
              
              console.log(`📁 DIR "${dirEntry.name}" will pass "${newParent}" as parent to ${entries.length} children`);
              
              const promises = entries.map(childEntry => 
                processEntry(childEntry, newPath, newParent)
              );
              await Promise.all(promises);
              resolve();
            } catch (error) {
              console.warn('Error processing directory:', dirEntry.name, error);
              resolve();
            }
          });
        });
      }
    };

    // Start processing from root level
    const promises: Promise<void>[] = [];
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (item.kind === 'file') {
        const entry = item.webkitGetAsEntry();
        if (entry) {
          console.log(`🎯 ROOT ENTRY: ${entry.name} (${entry.isDirectory ? 'DIR' : 'FILE'})`);
          // Start with empty path and empty parent (root level)
          promises.push(processEntry(entry, '', ''));
        }
      }
    }

    await Promise.all(promises);
    
    console.log('🎯 FINAL RESULTS:', files.map(f => `${f.name} -> "${f.folderName}"`));
    return files;
  };

  const onDropHandler = async (acceptedFiles: File[], _fileRejections: any[], event: any) => {
    setIsClicked(true);
    setIsLoading(true);
    
    try {
      let processedFiles: FileWithMetadata[] = [];
      
      // Check if this is a folder drop (using dataTransfer items)
      if (event.dataTransfer && event.dataTransfer.items) {
        // Check if any item is a directory
        const hasDirectories = Array.from(event.dataTransfer.items).some(
          (item: any) => item.webkitGetAsEntry && item.webkitGetAsEntry()?.isDirectory
        );
        
        if (hasDirectories) {
          console.log('Processing folder drop...');
          processedFiles = await processDroppedItems(event.dataTransfer.items);
          
          if (processedFiles.length === 0) {
            showErrorToast('No PDF or DOCX files found in the dropped folder(s). Please make sure your folders contain PDF or DOCX files.');
            setIsLoading(false);
            setIsClicked(false);
            return;
          }
        } else {
          // Regular file drop
          processedFiles = acceptedFiles.filter(file => {
            const fileName = file.name.toLowerCase();
            return fileName.endsWith('.pdf') || fileName.endsWith('.docx');
          }).map(file => {
            const courseCode = extractCourseCode(file.name);
            return Object.assign(file, {
              folderPath: file.name,
              courseCode: courseCode || undefined,
              folderName: ''
            });
          });
        }
      }

      setSelectedFiles(processedFiles);
      
      if (processedFiles.length > 0) {
        const defaultValues: CustomFileBase = {
          processingTotalTime: 0,
          status: 'None',
          nodesCount: 0,
          relationshipsCount: 0,
          model: model,
          fileSource: 'local file',
          uploadProgress: 0,
          processingProgress: undefined,
          retryOptionStatus: false,
          retryOption: '',
          chunkNodeCount: 0,
          chunkRelCount: 0,
          entityNodeCount: 0,
          entityEntityRelCount: 0,
          communityNodeCount: 0,
          communityRelCount: 0,
          createdAt: new Date(),
        };

        const copiedFilesData: CustomFile[] = [...filesData];
        
        processedFiles.forEach(file => {
          const filedataIndex = copiedFilesData.findIndex((filedataitem) => filedataitem?.name === file?.name);
          if (filedataIndex === -1) {
            copiedFilesData.unshift({
              name: file.name,
              type: `${file.name.substring(file.name.lastIndexOf('.') + 1, file.name.length).toUpperCase()}`,
              size: file.size,
              uploadProgress: file.size && file?.size < chunkSize ? 100 : 0,
              id: uuidv4(),
              ...defaultValues,
              courseCode: file.courseCode,
              folderName: file.folderName
            });
          }
        });
        
        setFilesData(copiedFilesData);
        showSuccessToast(`Found ${processedFiles.length} PDF/DOCX files in the folder(s)`);
      } else {
        showErrorToast('No PDF or DOCX files found in the selected folder(s)');
      }
    } catch (error) {
      console.error('Error processing dropped folder:', error);
      showErrorToast('Error processing dropped folder');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  // Handle file input change (for Browse button)
  const handleFileInputChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setIsClicked(true);
    setIsLoading(true);

    try {
      // Convert FileList to array and process as folder structure
      const fileArray = Array.from(files);
      const processedFiles: FileWithMetadata[] = [];

      for (const file of fileArray) {
        const fileName = file.name.toLowerCase();
        
        // Only process PDF and DOCX files
        if (fileName.endsWith('.pdf') || fileName.endsWith('.docx')) {
          // Extract folder structure from webkitRelativePath
          const relativePath = (file as any).webkitRelativePath || file.name;
          const pathParts = relativePath.split('/');
          
          // Get immediate parent folder (last folder before file)
          let folderName = '';
          if (pathParts.length > 1) {
            folderName = pathParts[pathParts.length - 2]; // Parent folder
          }
          
          const courseCode = extractCourseCode(relativePath || file.name);
          
          console.log(`📁 Browse file: ${file.name}, relativePath: ${relativePath}, folderName: "${folderName}"`);
          
          const fileWithMetadata: FileWithMetadata = Object.assign(file, {
            folderPath: relativePath,
            courseCode: courseCode || undefined,
            folderName: folderName
          });
          
          processedFiles.push(fileWithMetadata);
        }
      }

      setSelectedFiles(processedFiles);
      
      if (processedFiles.length > 0) {
        const defaultValues: CustomFileBase = {
          processingTotalTime: 0,
          status: 'None',
          nodesCount: 0,
          relationshipsCount: 0,
          model: model,
          fileSource: 'local file',
          uploadProgress: 0,
          processingProgress: undefined,
          retryOptionStatus: false,
          retryOption: '',
          chunkNodeCount: 0,
          chunkRelCount: 0,
          entityNodeCount: 0,
          entityEntityRelCount: 0,
          communityNodeCount: 0,
          communityRelCount: 0,
          createdAt: new Date(),
        };

        const copiedFilesData: CustomFile[] = [...filesData];
        
        processedFiles.forEach(file => {
          const filedataIndex = copiedFilesData.findIndex((filedataitem) => filedataitem?.name === file?.name);
          if (filedataIndex === -1) {
            copiedFilesData.unshift({
              name: file.name,
              type: `${file.name.substring(file.name.lastIndexOf('.') + 1, file.name.length).toUpperCase()}`,
              size: file.size,
              uploadProgress: file.size && file?.size < chunkSize ? 100 : 0,
              id: uuidv4(),
              ...defaultValues,
              courseCode: file.courseCode,
              folderName: file.folderName
            });
          }
        });
        
        setFilesData(copiedFilesData);
        showSuccessToast(`Selected ${processedFiles.length} PDF/DOCX files from folder(s)`);
      } else {
        showErrorToast('No PDF or DOCX files found in the selected folder(s)');
      }
    } catch (error) {
      console.error('Error processing selected files:', error);
      showErrorToast('Error processing files. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (selectedFiles.length > 0) {
      selectedFiles.forEach((file, index) => {
        if (filesData[index]?.status === 'None' && isClicked) {
          uploadFileInChunks(file);
        }
      });
    }
  }, [selectedFiles]);

  const uploadFileInChunks = (file: FileWithMetadata) => {
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
        
        console.log(`🚀 UPLOADING: ${file.name}, folderName: "${file.folderName}"`);
        
        if (file.courseCode) {
          formData.append('course_code', file.courseCode);
        }
        
        if (file.folderName && file.folderName.trim() !== '') {
          formData.append('folder_name', file.folderName.trim());
        } else {
          // This should not happen with our new logic, but just in case
          formData.append('folder_name', 'unknown_folder');
        }
        
        for (const key in userCredentials) {
          formData.append(key, userCredentials[key]);
        }

        setIsLoading(true);
        setFilesData((prevfiles) =>
          prevfiles.map((curfile) => {
            if (curfile.name === file.name) {
              return { ...curfile, status: 'Uploading' };
            }
            return curfile;
          })
        );

        try {
          const response = await fetch(`${import.meta.env.VITE_BACKEND_API_URL}/upload`, {
            method: 'POST',
            body: formData,
          });
          
          const apiResponse = await response.json();
          
          if (apiResponse?.status === 'Failed') {
            throw new Error(`message:${apiResponse.message},fileName:${apiResponse.file_name}`);
          } else {
            setFilesData((prevfiles) =>
              prevfiles.map((curfile) => {
                if (curfile.name === file.name) {
                  return {
                    ...curfile,
                    uploadProgress: Math.ceil(chunkNumber * chunkProgressIncrement),
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
            showErrorToast(`Error Occurred: ${error.message}`, true);
          }
          setFilesData((prevfiles) =>
            prevfiles.map((curfile) => {
              if (curfile.name === file.name) {
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
            if (curfile.name === file.name) {
              return {
                ...curfile,
                status: 'New',
                uploadProgress: 100,
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

  return (
    <>
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".pdf,.docx"
        style={{ display: 'none' }}
        onChange={handleFileInputChange}
        {...({ webkitdirectory: '' } as any)}
      />
      
      <SpotlightTarget
        id='folder-dropzone'
        hasPulse={true}
        indicatorVariant='border'
        hasAnchorPortal={false}
        borderRadius={11}
      >
        <Dropzone
          loadingComponent={isLoading && <Loader title='Processing Folder...' />}
          isTesting={true}
          className='bg-none! dropzoneContainer folder-dropzone'
          supportedFilesDescription={
            <Typography variant='body-small'>
              <Flex flexDirection="column" gap="2">
                <span>📁 <strong>Drag & Drop folders here</strong> or use Browse button below.</span>
                <Button 
                  size="small" 
                  onClick={handleBrowseClick}
                  className="max-w-fit"
                >
                  📂 Browse Folders & Files
                </Button>
                <div className='align-self-center'>
                  <IconButtonWithToolTip
                    label='Folder processing info'
                    clean
                    text={
                      <Typography variant='body-small'>
                        <Flex gap='3' alignItems='flex-start'>
                          <span>• Recursively scans all subfolders</span>
                          <span>• Extracts course codes from filenames [XXX] pattern</span>
                          <span>• Preserves folder structure information</span>
                          <span>• Only processes PDF (.pdf) and Word (.docx) files</span>
                        </Flex>
                      </Typography>
                    }
                  >
                    <InformationCircleIconOutline className='w-[22px] h-[22px]' />
                  </IconButtonWithToolTip>
                </div>
              </Flex>
            </Typography>
          }
          dropZoneOptions={{
            accept: {
              'application/pdf': ['.pdf'],
              'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
            },
            onDrop: onDropHandler,
            onDropRejected: (e) => {
              if (e.length) {
                showErrorToast('Only PDF and DOCX files are supported for folder upload');
              }
            },
          }}
        />
      </SpotlightTarget>
    </>
  );
};

export default FolderDropZone;
