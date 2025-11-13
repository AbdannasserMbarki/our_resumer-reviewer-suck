import React, { useRef, useState } from 'react'
import { Upload } from 'lucide-react'
import './FileUpload.css'

function FileUpload({ onFileSelect, accept = ".pdf,.docx" }) {
  const [dragActive, setDragActive] = useState(false)
  const [fileName, setFileName] = useState('')
  const inputRef = useRef(null)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = (file) => {
    setFileName(file.name)
    onFileSelect(file)
  }

  const onButtonClick = () => {
    inputRef.current.click()
  }

  return (
    <div className="file-upload-container">
      <div
        className={`file-upload-area ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={onButtonClick}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={handleChange}
          style={{ display: 'none' }}
        />
        
        <Upload className="upload-icon" size={48} />
        
        {fileName ? (
          <div className="file-selected">
            <p className="file-name">{fileName}</p>
            <p className="file-hint">Click or drag to replace</p>
          </div>
        ) : (
          <div className="file-prompt">
            <p className="upload-text">Drop your resume here or click to browse</p>
            <p className="upload-hint">PDF or DOCX • Max 2MB</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default FileUpload
