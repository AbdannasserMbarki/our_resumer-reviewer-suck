import React from 'react'
import './JobDescriptionInput.css'

function JobDescriptionInput({ value, onChange, placeholder }) {
  return (
    <div className="job-description-input">
      <label htmlFor="job-description">Job Description</label>
      <textarea
        id="job-description"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder || "Paste the job description here..."}
        rows={12}
      />
      <p className="input-hint">Copy and paste the full job description to get targeted recommendations</p>
    </div>
  )
}

export default JobDescriptionInput
