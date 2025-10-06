import React, {useEffect, useState} from 'react'
import {listInvoices, createInvoice, searchInvoices, deleteInvoice, getInvoice, updateInvoice, downloadInvoicePDF, runAgent} from '../api'
import InvoiceForm from './InvoiceForm'
import Card from './ui/Card'
import Button from './ui/Button'
import { IconSearch, IconDelete, IconEye } from './ui/Icons'
import { motion } from 'framer-motion'

export default function InvoiceList(){
  const [customerId, setCustomerId] = useState('CUST-1')
  const [invoices, setInvoices] = useState([])
  const [q, setQ] = useState('')
  const [selected, setSelected] = useState(null)
  const [agentPrompt, setAgentPrompt] = useState('Find unpaid invoices for CUST-1')
  const [agentResp, setAgentResp] = useState(null)
  const [agentLoading, setAgentLoading] = useState(false)
  const [editing, setEditing] = useState(null)
  const [editAmount, setEditAmount] = useState('')
  const [editCurrency, setEditCurrency] = useState('USD')

  const fetch = async ()=>{
    const res = await listInvoices(customerId)
    // Defensive: ensure we always set an array to avoid .map errors
    if (!Array.isArray(res)) {
      console.warn('listInvoices returned non-array:', res)
      setInvoices(Array.isArray(res?.result) ? res.result : [])
    } else {
      setInvoices(res)
    }
  }

  useEffect(()=>{ fetch() }, [customerId])

  const onCreate = async (payload)=>{
    await createInvoice(payload)
    fetch()
  }

  const onSearch = async ()=>{
    if(!q){ fetch(); return }
    const res = await searchInvoices(q)
    if (!Array.isArray(res)) {
      console.warn('searchInvoices returned non-array:', res)
      setInvoices(Array.isArray(res?.result) ? res.result : [])
    } else {
      setInvoices(res)
    }
  }

  const onDelete = async (id)=>{
    await deleteInvoice(id)
    fetch()
  }

  const showDetails = async (id)=>{
    const res = await getInvoice(id)
    setSelected(res)
  }

  const startEdit = (inv) => {
    setEditing(inv.invoice_id)
    setEditAmount(inv.amount)
    setEditCurrency(inv.currency)
  }

  const submitEdit = async (e) => {
    e.preventDefault()
    await updateInvoice(editing, {amount: parseFloat(editAmount), currency: editCurrency})
    setEditing(null)
    fetch()
  }

  const handleDownloadPDF = async (invoice_id) => {
    const url = await downloadInvoicePDF(invoice_id)
    window.open(url, '_blank')
  }

  return (
    <div className="grid grid-cols-3 gap-6">
      <div className="col-span-2">
        <Card>
          <div className="flex items-center gap-3 mb-4">
            <input value={customerId} onChange={e=>setCustomerId(e.target.value)} className="p-2 border rounded" />
            <Button className="bg-slate-100">Load</Button>
            <input value={q} onChange={e=>setQ(e.target.value)} placeholder="Search" className="p-2 border rounded flex-1" />
            <Button onClick={onSearch} className="bg-emerald-600 text-white"><IconSearch size={16}/> Search</Button>
          </div>

          <InvoiceForm onCreate={onCreate} customer_id={customerId} />

          <div className="mt-4 space-y-3">
            {invoices.map(inv => (
              <motion.div key={inv.invoice_id} initial={{opacity:0, y:6}} animate={{opacity:1, y:0}} className="p-3 border rounded flex justify-between items-center">
                <div>
                  <div className="text-lg font-semibold">{inv.invoice_id} — {inv.customer_id}</div>
                  <div className="text-sm text-slate-600">{inv.amount} {inv.currency} • {inv.status}</div>
                </div>
                <div className="flex gap-2">
                  <Button onClick={()=>showDetails(inv.invoice_id)} className="border"><IconEye size={16}/> Details</Button>
                  <Button onClick={()=>startEdit(inv)} className="bg-yellow-500 text-white">Edit</Button>
                  <Button onClick={()=>onDelete(inv.invoice_id)} className="bg-red-600 text-white"><IconDelete size={16}/> Delete</Button>
                </div>
                {editing === inv.invoice_id && (
                  <form onSubmit={submitEdit} className="flex gap-2 mt-2">
                    <input value={editAmount} onChange={e=>setEditAmount(e.target.value)} className="p-1 border rounded w-20" />
                    <select value={editCurrency} onChange={e=>setEditCurrency(e.target.value)} className="p-1 border rounded">
                      <option>USD</option>
                      <option>INR</option>
                    </select>
                    <Button type="submit" className="bg-emerald-600 text-white">Save</Button>
                    <Button type="button" onClick={()=>setEditing(null)} className="bg-slate-400 text-white">Cancel</Button>
                  </form>
                )}
              </motion.div>
            ))}
          </div>
        </Card>
      </div>

      <div>
        <Card>
          <h3 className="text-lg font-semibold mb-2">Invoice Details</h3>
          {selected ? (
            <div>
              <div className="mb-1"><strong>ID:</strong> {selected.invoice_id}</div>
              <div className="mb-1"><strong>Customer:</strong> {selected.customer_id}</div>
              <div className="mb-1"><strong>Amount:</strong> {selected.amount} {selected.currency}</div>
              <div className="mb-1"><strong>Status:</strong> {selected.status}</div>
              <div className="mt-3 flex gap-2">
                <a href={selected.pdf_url} target="_blank" rel="noreferrer" className="text-sky-600">Open PDF</a>
                <Button onClick={()=>handleDownloadPDF(selected.invoice_id)} className="bg-sky-600 text-white">Download PDF</Button>
              </div>
            </div>
          ) : (
            <div className="text-slate-500">Select an invoice to view details</div>
          )}
          <hr className="my-3" />
          <div className="mb-2">
            <h4 className="font-semibold">Ask the Billing Agent</h4>
            <textarea value={agentPrompt} onChange={e=>setAgentPrompt(e.target.value)} className="w-full p-2 border rounded" rows={3} />
            <div className="flex gap-2 mt-2">
              <Button onClick={async ()=>{
                setAgentLoading(true); setAgentResp(null);
                try {
                  const res = await runAgent(agentPrompt)
                  setAgentResp(res)
                } catch (e) {
                  setAgentResp({error: e.message || String(e)})
                } finally { setAgentLoading(false) }
              }} className="bg-indigo-600 text-white">Run Agent</Button>
              {agentLoading && <div className="text-sm self-center">Running...</div>}
            </div>
            {agentResp && (
              <pre className="mt-3 p-2 bg-slate-100 rounded text-sm max-h-48 overflow-auto">{JSON.stringify(agentResp, null, 2)}</pre>
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}
