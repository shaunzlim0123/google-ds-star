import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import useAgentStore from '../store/useAgentStore'
import axios from 'axios'
import { Upload, File, X, Check, Loader2, FileText, Database } from 'lucide-react'
import clsx from 'clsx'

const FILE_TYPE_ICONS = {
  csv: Database,
  json: FileText,
  xlsx: Database,
  xls: Database,
  parquet: Database,
  txt: FileText,
  md: FileText,
  xml: FileText,
  yaml: FileText,
  yml: FileText,
}

export default function FileUpload() {
  const { dataFiles, setDataFiles, isExecuting } = useAgentStore()
  const [uploading, setUploading] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState([])

  const onDrop = useCallback(async (acceptedFiles) => {
    setUploading(true)

    try {
      const uploadPromises = acceptedFiles.map(async (file) => {
        const formData = new FormData()
        formData.append('file', file)

        const response = await axios.post('/api/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })

        return {
          ...response.data,
          originalName: file.name,
          uploadedAt: new Date().toISOString(),
        }
      })

      const results = await Promise.all(uploadPromises)
      setUploadedFiles((prev) => [...prev, ...results])

      // Update data files in store
      const newPaths = results.map((r) => r.path)
      setDataFiles([...dataFiles, ...newPaths])
    } catch (error) {
      console.error('Upload failed:', error)
      alert('File upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }, [dataFiles, setDataFiles])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/json': ['.json'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/octet-stream': ['.parquet'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
      'text/xml': ['.xml'],
      'text/yaml': ['.yaml', '.yml'],
    },
    disabled: isExecuting,
  })

  const removeFile = (path) => {
    const newFiles = uploadedFiles.filter((f) => f.path !== path)
    setUploadedFiles(newFiles)
    setDataFiles(newFiles.map((f) => f.path))

    // Optionally delete from server
    const filename = path.split('/').pop()
    axios.delete(`/api/uploads/${filename}`).catch(console.error)
  }

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  return (
    <div className="card">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Data Files</h2>

      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={clsx(
          'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
          isDragActive && 'border-primary-500 bg-primary-50',
          !isDragActive && 'border-gray-300 hover:border-primary-400',
          isExecuting && 'opacity-50 cursor-not-allowed'
        )}
      >
        <input {...getInputProps()} />
        <Upload className="w-10 h-10 text-gray-400 mx-auto mb-3" />
        {uploading ? (
          <div className="flex items-center justify-center gap-2">
            <Loader2 className="w-5 h-5 animate-spin text-primary-600" />
            <p className="text-sm text-gray-700">Uploading files...</p>
          </div>
        ) : isDragActive ? (
          <p className="text-sm text-primary-700 font-medium">Drop the files here</p>
        ) : (
          <div>
            <p className="text-sm text-gray-700 font-medium mb-1">
              Drop files here or click to browse
            </p>
            <p className="text-xs text-gray-500">
              Supports CSV, JSON, Excel, Parquet, and text files
            </p>
          </div>
        )}
      </div>

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="mt-4 space-y-2">
          <h3 className="text-sm font-semibold text-gray-700">
            Uploaded Files ({uploadedFiles.length})
          </h3>
          <div className="space-y-2">
            {uploadedFiles.map((file, idx) => {
              const extension = file.filename.split('.').pop().toLowerCase()
              const FileIcon = FILE_TYPE_ICONS[extension] || File

              return (
                <div
                  key={idx}
                  className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                      <FileIcon className="w-5 h-5 text-primary-600" />
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {file.filename}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatFileSize(file.size)}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-green-500" />
                    <button
                      onClick={() => removeFile(file.path)}
                      disabled={isExecuting}
                      className="p-1 text-gray-400 hover:text-red-600 transition-colors disabled:opacity-50"
                      title="Remove file"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {uploadedFiles.length === 0 && !uploading && (
        <p className="text-xs text-gray-500 mt-4 text-center">
          No files uploaded yet
        </p>
      )}
    </div>
  )
}
