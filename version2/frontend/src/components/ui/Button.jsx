import React from 'react'

export default function Button({children, className = '', ...props}){
  return (
    <button {...props} className={`inline-flex items-center gap-2 px-4 py-2 rounded-2xl text-sm font-medium shadow-sm ${className}`}>
      {children}
    </button>
  )
}
