import React, {useState} from 'react'
import Button from './ui/Button'
import { IconPlus } from './ui/Icons'

export default function InvoiceForm({onCreate, customer_id}){
  const [amount, setAmount] = useState('')
  const [currency, setCurrency] = useState('USD')

  const submit = async (e)=>{
    e.preventDefault()
    if(!amount) return
    await onCreate({customer_id, amount: parseFloat(amount), currency})
    setAmount('')
  }

  return (
    <form onSubmit={submit} className="flex gap-2 mb-4">
      <input value={amount} onChange={e=>setAmount(e.target.value)} placeholder="Amount" className="p-2 border rounded w-28" />
      <select value={currency} onChange={e=>setCurrency(e.target.value)} className="p-2 border rounded">
        <option>USD</option>
        <option>INR</option>
      </select>
      <Button className="bg-sky-600 text-white"><IconPlus size={16}/> Create</Button>
    </form>
  )
}
