import {useState} from 'react';
import {AlertCircle} from 'lucide-react';
import Sidebar from './components/Sidebar';
import PageHeader from './components/PageHeader';
import DocumentsPage from './pages/DocumentsPage';
import OverviewPage from './pages/OverviewPage';
import ReviewPage from './pages/ReviewPage';
import {useDocuments} from './hooks/useDocuments';
import type {View} from './types/documents';
export default function App(){const [view,setView]=useState<View>('documents');const {documents,document,selectedId,setSelectedId,loading,busy,error,setError,refresh,upload,review,finalize,rename,requestReview,remove}=useDocuments();const pending=document?.clinical_entities.filter(e=>e.status==='candidate').length||0;return <div className="app"><Sidebar view={view} setView={setView} hasDocument={Boolean(selectedId)} pending={pending}/><main className="main"><PageHeader view={view}/>{error&&<div className="error" role="alert"><AlertCircle size={18}/><span>{error}</span><button onClick={()=>setError('')}>Dismiss</button></div>}{view==='documents'&&<DocumentsPage documents={documents} loading={loading} busy={busy} refresh={refresh} upload={async file=>{const d=await upload(file);if(d)setView('overview')}} open={id=>{setSelectedId(id);setView('overview')}}/>}{view!=='documents'&&!document&&<div className="empty">{error?'Unable to load document.':'Loading document...'}</div>}{view==='overview'&&document&&<OverviewPage document={document} back={()=>setView('documents')} goReview={()=>setView('review')} busy={busy} rename={rename} requestReview={requestReview} remove={async()=>{const ok=await remove();if(ok)setView('documents');return ok}}/ >}{view==='review'&&document&&<ReviewPage document={document} busy={busy} back={()=>setView('overview')} review={review} finalize={finalize}/>}</main></div>}
