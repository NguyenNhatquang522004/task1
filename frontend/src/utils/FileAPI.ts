import { Method } from 'axios';
import { url } from './Utils';
import { ExtractParams } from '../types';
import { apiCall } from '../services/CommonAPI';
import api from '../API/Index';

// Get Available Folders Call
export const getFoldersAPI = async (): Promise<any> => {
  const baseUrl = `${url()}/folders`;
  
  // Use hardcoded credentials for now to ensure it works
  const hardcodedCredentials = {
    uri: 'neo4j+s://013fb011.databases.neo4j.io',
    userName: 'neo4j',
    password: 'NH43Qy392yswBCfUFNrjYjIIvr4B_LcJB4eMRNzHrp4',
    database: 'neo4j'
  };
  
  console.log('🔧 getFoldersAPI called');
  console.log('🔧 Using hardcoded credentials');
  console.log('🔧 Base URL:', baseUrl);
  
  // Build query string with hardcoded credentials
  const queryParams = new URLSearchParams();
  queryParams.append('uri', hardcodedCredentials.uri);
  queryParams.append('userName', hardcodedCredentials.userName);
  queryParams.append('password', hardcodedCredentials.password);
  queryParams.append('database', hardcodedCredentials.database);
  
  const urlFolders = `${baseUrl}?${queryParams.toString()}`;
  console.log('🔧 Final URL:', urlFolders);
  
  try {
    // Use axios directly for GET request
    const response = await api({
      method: 'get',
      url: urlFolders,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    console.log('🔧 API Response:', response.data);
    return response.data;
  } catch (error) {
    console.error('🔧 API Error:', error);
    throw error;
  }
};

// Upload Call
export const uploadAPI = async (
  file: Blob,
  model: string,
  chunkNumber: number,
  totalChunks: number,
  originalname: string,
  course_code?: string,
  folder_name?: string
): Promise<any> => {
  const urlUpload = `${url()}/upload`;
  const method: Method = 'post';
  
  // Create FormData and add hardcoded credentials
  const formData = new FormData();
  formData.append('file', file);
  formData.append('model', model);
  formData.append('chunkNumber', chunkNumber.toString());
  formData.append('totalChunks', totalChunks.toString());
  formData.append('originalname', originalname);
  
  // Add course_code and folder_name if provided
  if (course_code) {
    formData.append('course_code', course_code);
  }
  if (folder_name) {
    formData.append('folder_name', folder_name);
  }
  
  // Add hardcoded Neo4j credentials
  formData.append('uri', 'neo4j+s://013fb011.databases.neo4j.io');
  formData.append('userName', 'neo4j');
  formData.append('password', 'NH43Qy392yswBCfUFNrjYjIIvr4B_LcJB4eMRNzHrp4');
  formData.append('database', 'neo4j');
  
  console.log('🔧 Upload API called with folder_name:', folder_name, 'course_code:', course_code);
  
  try {
    const response = await api({
      method: method,
      url: urlUpload,
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('🔧 Upload API Error:', error);
    throw error;
  }
};

// Extract call
export const extractAPI = async (
  model: string,
  source_type: string,
  retry_condition: string,
  source_url?: string,
  aws_access_key_id?: string | null,
  aws_secret_access_key?: string | null,
  file_name?: string,
  gcs_bucket_name?: string,
  gcs_bucket_folder?: string,
  allowedNodes?: string[],
  allowedRelationship?: string[],
  token_chunk_size?: number,
  chunk_overlap?: number,
  chunks_to_combine?: number,
  gcs_project_id?: string,
  language?: string,
  access_token?: string,
  additional_instructions?: string
): Promise<any> => {
  const urlExtract = `${url()}/extract`;
  const method: Method = 'post';
  let additionalParams: ExtractParams;
  if (source_type === 's3 bucket') {
    additionalParams = {
      model,
      source_url,
      aws_secret_access_key,
      aws_access_key_id,
      source_type,
      file_name,
      allowedNodes,
      allowedRelationship,
      token_chunk_size,
      chunk_overlap,
      chunks_to_combine,
      retry_condition,
      additional_instructions,
    };
  } else if (source_type === 'Wikipedia') {
    additionalParams = {
      model,
      wiki_query: file_name,
      source_type,
      file_name,
      allowedNodes,
      allowedRelationship,
      token_chunk_size,
      chunk_overlap,
      chunks_to_combine,
      language,
      retry_condition,
      additional_instructions,
    };
  } else if (source_type === 'gcs bucket') {
    additionalParams = {
      model,
      gcs_blob_filename: file_name,
      gcs_bucket_folder,
      gcs_bucket_name,
      source_type,
      file_name,
      allowedNodes,
      allowedRelationship,
      token_chunk_size,
      chunk_overlap,
      chunks_to_combine,
      gcs_project_id,
      access_token,
      retry_condition,
      additional_instructions,
    };
  } else if (source_type === 'youtube') {
    additionalParams = {
      model,
      source_url,
      source_type,
      file_name,
      allowedNodes,
      allowedRelationship,
      token_chunk_size,
      chunk_overlap,
      chunks_to_combine,
      retry_condition,
      additional_instructions,
    };
  } else if (source_type === 'web-url') {
    additionalParams = {
      model,
      source_url,
      source_type,
      file_name,
      allowedNodes,
      allowedRelationship,
      token_chunk_size,
      chunk_overlap,
      chunks_to_combine,
      retry_condition,
      additional_instructions,
    };
  } else {
    additionalParams = {
      model,
      source_type,
      file_name,
      allowedNodes,
      allowedRelationship,
      token_chunk_size,
      chunk_overlap,
      chunks_to_combine,
      retry_condition,
      additional_instructions,
    };
  }
  const response = await apiCall(urlExtract, method, additionalParams);
  return response;
};
