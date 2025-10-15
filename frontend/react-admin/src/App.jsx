import React, {useEffect, useState} from 'react'
import axios from 'axios'
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const API = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/v1'

export default function App(){
  const [metrics, setMetrics] = useState(null)
  const [faqs, setFaqs] = useState([])
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  
  useEffect(()=>{ fetchMetrics() }, [])
  async function fetchMetrics(){
    try{
      const res = await axios.get(API + '/metrics', { headers: {'x-api-key': 'admin-secret-key'} })
      setMetrics(res.data)
    }catch(e){
      console.error(e)
    }
  }
  async function createFaq(){
    try{
      await axios.post(API + '/faqs', {title, content}, { headers: {'x-api-key': 'admin-secret-key'} })
      setTitle(''); setContent('')
      alert('FAQ created')
    }catch(e){ alert('error') }
  }
  const chartData = metrics ? [{name:'Sessions', value: metrics.total_sessions}, {name:'Open', value: metrics.open_sessions}, {name:'Escalated', value: metrics.escalated}] : []
  return (<div style={{padding:20,fontFamily:'Arial'}}>
    <h1>Admin Dashboard — Demo</h1>
    {metrics ? <div style={{width:600,height:300}}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="value" />
        </LineChart>
      </ResponsiveContainer>
    </div> : <div>Metrics not loaded</div>}
    <hr/>
    <h2>Create FAQ</h2>
    <input value={title} onChange={e=>setTitle(e.target.value)} placeholder="Title" style={{width:400}}/><br/>
    <textarea value={content} onChange={e=>setContent(e.target.value)} rows={6} cols={80} /><br/>
    <button onClick={createFaq}>Create FAQ</button>
  </div>)
}
