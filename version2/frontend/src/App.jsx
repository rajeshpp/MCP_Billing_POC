import React from 'react'
import InvoiceList from './components/InvoiceList'

export default function App(){
  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-6xl mx-auto">
        <header className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">MCP Billing — Demo</h1>
            <p className="text-slate-600">Agent-to-Agent communication demo with MCP · Polished UI</p>
          </div>
          <div>
            <button className="px-4 py-2 rounded-2xl border">Repo</button>
          </div>
        </header>

        <main>
          <InvoiceList />
        </main>
      </div>
    </div>
  )
}
