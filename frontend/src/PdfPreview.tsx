import { useEffect, useState } from 'react';
type Props={documentId:string};
export default function PdfPreview({documentId}:Props){
 const [url,setUrl]=useState('');const [error,setError]=useState('');const [loading,setLoading]=useState(true);
 useEffect(()=>{const controller=new AbortController();let objectUrl='';setUrl('');setError('');setLoading(true);
 async function load(){try{const res=await fetch(`/api/v1/documents/${encodeURIComponent(documentId)}/original`,{credentials:'same-origin',signal:controller.signal,cache:'no-store'});if(!res.ok)throw new Error(`PDF request failed (HTTP ${res.status})`);const blob=await res.blob();if(!blob.type.includes('pdf'))throw new Error('Response was not a PDF');if(controller.signal.aborted)return;objectUrl=URL.createObjectURL(blob);setUrl(objectUrl)}catch(e){if(!controller.signal.aborted)setError(String(e))}finally{if(!controller.signal.aborted)setLoading(false)}}void load();return()=>{controller.abort();if(objectUrl)URL.revokeObjectURL(objectUrl)}},[documentId]);
 return <div className="pdfPreview">{loading&&<p className="muted">Loading PDF...</p>}{error&&<p className="pdfError">{error}</p>}{url&&<iframe src={url} title="Original PDF document" className="pdfFrame"/>}</div>;
}
