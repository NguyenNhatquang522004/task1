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
    
    const processEntry = async (entry: FileSystemEntry, currentPath = '', immediateParentFolder = ''): Promise<void> => {
      try {
        console.log('🔍 PROCESSING ENTRY:', {
          entryName: entry.name,
          entryType: entry.isFile ? 'FILE' : 'DIRECTORY',
          currentPath,
          immediateParentFolder
        });

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
                  
                  // The folder_name is the immediateParentFolder parameter
                  const folderName = immediateParentFolder || '';
                  
                  console.log('📄 FILE PROCESSING COMPLETE:', {
                    fileName: file.name,
                    fullPath,
                    currentPath,
                    immediateParentFolder,
                    determinedFolderName: folderName,
                    courseCode,
                    finalResult: {
                      name: file.name,
                      folderName: folderName,
                      courseCode: courseCode || undefined
                    }
                  });
                  
                  const fileWithMetadata: FileWithMetadata = Object.assign(file, {
                    folderPath: fullPath,
                    courseCode: courseCode || undefined,
                    folderName: folderName // Keep exactly as determined
                  });
                  
                  files.push(fileWithMetadata);
                  resolve();
                } catch (error) {
                  console.warn('Error processing file:', file.name, error);
                  resolve();
                }
              }, (error) => {
                console.warn('Error reading file:', fileEntry.name, error);
                resolve();
              });
            });
          }
        } else if (entry.isDirectory) {
          const dirEntry = entry as FileSystemDirectoryEntry;
          
          console.log('� DIRECTORY PROCESSING DEBUG:', {
            dirName: dirEntry.name,
            currentPath: path,
            currentParentFolderName: parentFolderName,
            isRootLevel: path === '',
            willPassAsParent: dirEntry.name
          });
          
          const dirReader = dirEntry.createReader();
          
          return new Promise((resolve) => {
            dirReader.readEntries(async (entries) => {
              try {
                // CRITICAL: The current directory becomes the parent folder for its children
                const nextParentName = dirEntry.name;
                const nextPath = path + dirEntry.name + '/';
                
                console.log('📂 RECURSION PARAMETERS:', {
                  currentDir: dirEntry.name,
                  nextPath,
                  nextParentName,
                  childrenCount: entries.length
                });
                
                // Process all children with this directory as their parent
                const promises = entries.map(childEntry => 
                  processEntry(childEntry, nextPath, nextParentName)
                );
                await Promise.all(promises);
                resolve();
              } catch (error) {
                console.warn('Error processing directory:', dirEntry.name, error);
                resolve();
              }
            }, (error) => {
              console.warn('Error reading directory:', dirEntry.name, error);
              resolve();
            });
          });
        }
      } catch (error) {
        console.warn('Error processing entry:', entry.name, error);
        return Promise.resolve();
      }
    };

    const promises: Promise<void>[] = [];
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (item.kind === 'file') {
        const entry = item.webkitGetAsEntry();
        if (entry) {
          if (entry.isDirectory) {
            // If it's a directory, start processing from root level
            console.log('🎯 ROOT DIRECTORY PROCESSING:', {
              rootDirName: entry.name,
              explanation: 'Starting recursive processing, parentFolderName will be set by subdirectories'
            });
            // For root directory, don't pass it as parentFolderName
            // Let the subdirectories determine the correct parentFolderName
            promises.push(processEntry(entry, '', ''));
          } else {
            // If it's a file at root level, no parent folder
            console.log('🎯 ROOT FILE PROCESSING:', {
              fileName: entry.name,
              explanation: 'File dropped directly at root level'
            });
            promises.push(processEntry(entry, '', ''));
          }
        }
      }
    }

    await Promise.all(promises);
    console.log('🎯 FINAL PROCESSED FILES DEBUG:', files.map(f => ({
      name: f.name,
      folderName: f.folderName,
      courseCode: f.courseCode,
      folderPath: f.folderPath,
      folderNameType: typeof f.folderName,
      folderNameValue: f.folderName,
      hasValidFolderName: !!(f.folderName && f.folderName.trim() !== '')
    })));
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
          // Regular file drop - process individual files
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
      } else {
        // File input selection - process individual files
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
              // Add metadata
              courseCode: file.courseCode,
              folderName: file.folderName
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

  // Handle file input change (for Browse button)
  const handleFileInputChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setIsClicked(true);
    setIsLoading(true);

    try {
      const processedFiles: FileWithMetadata[] = Array.from(files)
        .filter(file => {
          const fileName = file.name.toLowerCase();
          return fileName.endsWith('.pdf') || fileName.endsWith('.docx');
        })
        .map(file => {
          const courseCode = extractCourseCode(file.name);
          return Object.assign(file, {
            folderPath: file.name,
            courseCode: courseCode || undefined,
            folderName: ''
          });
        });

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
        showSuccessToast(`Selected ${processedFiles.length} PDF/DOCX files`);
      } else {
        showErrorToast('No PDF or DOCX files found in the selection');
      }
    } catch (error) {
      console.error('Error processing selected files:', error);
      showErrorToast('Error processing files. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  // Debug method to test folder processing
  const testFolderProcessing = () => {
    console.log('🧪 TESTING FOLDER PROCESSING LOGIC');
    
    // Simulate file structure
    const testFiles = [
      {
        name: '[CMP177] beginningflutter.pdf',
        folderName: 'tham khảo nội bộ',
        courseCode: 'CMP177'
      }
    ];
    
    testFiles.forEach(file => {
      console.log('🧪 Test file:', {
        name: file.name,
        folderName: file.folderName,
        courseCode: file.courseCode,
        hasValidFolderName: !!(file.folderName && file.folderName.trim() !== ''),
        willSendToBackend: file.folderName && file.folderName.trim() !== '' ? file.folderName : 'unknown_folder'
      });
    });
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
        
        // Add metadata for course_code and folder_name
        console.log('🔍 UPLOAD CHUNK DEBUG:', {
          fileName: file.name,
          courseCode: file.courseCode,
          folderName: file.folderName,
          folderNameType: typeof file.folderName,
          folderNameLength: file.folderName ? file.folderName.length : 'N/A',
          folderNameTrimmed: file.folderName ? file.folderName.trim() : 'N/A',
          chunkNumber,
          totalChunks,
          fileKeys: Object.keys(file),
          completeFile: {
            name: file.name,
            folderName: file.folderName,
            courseCode: file.courseCode,
            folderPath: file.folderPath
          }
        });
        
        if (file.courseCode) {
          console.log('✅ Adding course_code to formData:', file.courseCode);
          formData.append('course_code', file.courseCode);
        } else {
          console.log('⚠️ No course_code for file:', file.name);
        }
        
        if (file.folderName && file.folderName.trim() !== '') {
          console.log('✅ Adding folder_name to formData:', file.folderName);
          formData.append('folder_name', file.folderName.trim());
        } else {
          console.log('❌ Warning: file.folderName is empty or undefined for file:', file.name, 'value:', file.folderName);
          // Force add a default folder name if missing
          const defaultFolderName = 'unknown_folder';
          console.log('🔧 Adding default folder_name:', defaultFolderName);
          formData.append('folder_name', defaultFolderName);
        }
        
        for (const key in userCredentials) {
          formData.append(key, userCredentials[key]);
        }

        setIsLoading(true);
        setFilesData((prevfiles) =>
          prevfiles.map((curfile) => {
            if (curfile.name === file.name) {
              return {
                ...curfile,
                status: 'Uploading',
              };
            }
            return curfile;
          })
        );

        try {
          // Send the formData directly instead of using uploadAPI
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
      {/* Hidden file input for Browse functionality */}
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
                <span>⚠️ <em>If drag & drop doesn't work, please use the Browse button.</em></span>
                <Button 
                  size="small" 
                  onClick={handleBrowseClick}
                  className="max-w-fit"
                >
                  📂 Browse Folders & Files
                </Button>
                <Button 
                  size="small" 
                  onClick={testFolderProcessing}
                  className="max-w-fit"
                >
                  🧪 Test Debug
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
