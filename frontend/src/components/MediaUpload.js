import React, { useState, useCallback } from 'react';
import {
  Box,
  Button,
  IconButton,
  Typography,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Paper,
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DeleteIcon from '@mui/icons-material/Delete';
import ImageIcon from '@mui/icons-material/Image';
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary';
import AudiotrackIcon from '@mui/icons-material/Audiotrack';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import { useNotification } from '../contexts/NotificationContext';

const ALLOWED_TYPES = {
  'image/*': {
    icon: ImageIcon,
    label: 'Image',
  },
  'video/*': {
    icon: VideoLibraryIcon,
    label: 'Video',
  },
  'audio/*': {
    icon: AudiotrackIcon,
    label: 'Audio',
  },
  'application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain': {
    icon: InsertDriveFileIcon,
    label: 'Document',
  },
};

function MediaUpload({ value = [], onChange, maxFiles = 5, maxSize = 10485760 }) {
  const [uploading, setUploading] = useState(false);
  const { showNotification } = useNotification();

  const onDrop = useCallback(async (acceptedFiles) => {
    if (value.length + acceptedFiles.length > maxFiles) {
      showNotification(`Maximum ${maxFiles} files allowed`, 'error');
      return;
    }

    setUploading(true);
    const newFiles = [];

    try {
      for (const file of acceptedFiles) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/media/upload', {
          method: 'POST',
          headers: {
            'x-access-token': localStorage.getItem('token'),
          },
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Failed to upload ${file.name}`);
        }

        const data = await response.json();
        newFiles.push({
          url: data.url,
          name: file.name,
          type: data.media_type,
          mime_type: data.mime_type,
        });
      }

      onChange([...value, ...newFiles]);
      showNotification('Files uploaded successfully', 'success');
    } catch (error) {
      console.error('Upload error:', error);
      showNotification('Failed to upload files', 'error');
    } finally {
      setUploading(false);
    }
  }, [value, maxFiles, onChange, showNotification]);

  const handleDelete = async (index) => {
    try {
      const file = value[index];
      const response = await fetch('/api/media', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'x-access-token': localStorage.getItem('token'),
        },
        body: JSON.stringify({ url: file.url }),
      });

      if (!response.ok) {
        throw new Error('Failed to delete file');
      }

      const newFiles = value.filter((_, i) => i !== index);
      onChange(newFiles);
      showNotification('File deleted successfully', 'success');
    } catch (error) {
      console.error('Delete error:', error);
      showNotification('Failed to delete file', 'error');
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: Object.keys(ALLOWED_TYPES).join(','),
    maxSize,
    disabled: uploading || value.length >= maxFiles,
  });

  const getFileIcon = (type) => {
    for (const [mimePattern, config] of Object.entries(ALLOWED_TYPES)) {
      if (type.startsWith(mimePattern.replace('/*', ''))) {
        const Icon = config.icon;
        return <Icon />;
      }
    }
    return <InsertDriveFileIcon />;
  };

  return (
    <Box>
      <Paper
        {...getRootProps()}
        sx={{
          p: 3,
          textAlign: 'center',
          backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'divider',
          cursor: 'pointer',
          opacity: (uploading || value.length >= maxFiles) ? 0.5 : 1,
        }}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <CircularProgress />
        ) : (
          <>
            <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
            <Typography variant="h6" gutterBottom>
              {isDragActive
                ? 'Drop files here'
                : value.length >= maxFiles
                ? 'Maximum files reached'
                : 'Drag & drop files here or click to select'}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Allowed types: Images, Videos, Documents, Audio
              <br />
              Maximum size: {Math.round(maxSize / 1024 / 1024)}MB
            </Typography>
          </>
        )}
      </Paper>

      {value.length > 0 && (
        <List sx={{ mt: 2 }}>
          {value.map((file, index) => (
            <ListItem key={file.url}>
              <ListItemText
                primary={file.name}
                secondary={`Type: ${file.type}`}
                sx={{
                  '& .MuiListItemText-primary': {
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                  },
                }}
                primary={
                  <>
                    {getFileIcon(file.mime_type)}
                    <span>{file.name}</span>
                  </>
                }
              />
              <ListItemSecondaryAction>
                <IconButton
                  edge="end"
                  aria-label="delete"
                  onClick={() => handleDelete(index)}
                >
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      )}
    </Box>
  );
}

export default MediaUpload;