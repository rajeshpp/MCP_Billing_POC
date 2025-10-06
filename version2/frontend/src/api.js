import axios from 'axios'

const BASE = (import.meta.env.VITE_BACKEND_URL) ? import.meta.env.VITE_BACKEND_URL : 'http://127.0.0.1:8000'

export const callTool = async (tool, args) => {
  const res = await axios.post(`${BASE}/mcp_call`, {tool, arguments: args})
  return res.data
}

export const listInvoices = async (customer_id) => callTool('list_invoices', {customer_id})
export const createInvoice = async (payload) => callTool('create_invoice_tool', payload)
export const getInvoice = async (invoice_id) => callTool('get_invoice', {invoice_id})
export const searchInvoices = async (q) => callTool('search_invoices_tool', {q})
export const updateInvoice = async (invoice_id, fields) => callTool('update_invoice_tool', {invoice_id, fields})
export const deleteInvoice = async (invoice_id) => callTool('delete_invoice_tool', {invoice_id})

export const downloadInvoicePDF = async (invoice_id) => {
  const res = await callTool('download_invoice_pdf', {invoice_id})
  return res.url || res.pdf_url || ''
}

export const runAgent = async (prompt) => {
  const res = await axios.post(`${BASE}/run_agent`, { prompt })
  return res.data
}

