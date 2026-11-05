import {useCallback,useEffect,useState} from 'react';
import type {DocumentResult,DocumentSummary} from '../types/documents';
import * as api from '../services/documents';
export function useDocuments(){
 const [documents,setDocuments]=useState<DocumentSummary[]>([]);
 const [document,setDocument]=useState<DocumentResult|null>(null);
 const [selectedId,setSelectedId]=useState('');
 const [loading,setLoading]=useState(true);
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState('');
 const refresh=useCallback(async()=>{try{setDocuments(await api.listDocuments());setError('')}catch(e){setError(String(e))}finally{setLoading(false)}},[]);
 useEffect(()=>{void refresh()},[refresh]);
 useEffect(()=>{if(!selectedId){setDocument(null);return}let active=true;setDocument(null);api.getDocument(selectedId).then(d=>{if(active)setDocument(d)}).catch(e=>{if(active)setError(String(e))});return()=>{active=false}},[selectedId]);
 const upload=async(file:File)=>{setBusy(true);setError('');try{const d=await api.uploadDocument(file);await refresh();setSelectedId(d.document_id);setDocument(d);return d}catch(e){setError(String(e));return null}finally{setBusy(false)}};
 const review=async(index:number,decision:'verified'|'rejected',corrected?:string,note?:string)=>{if(!document)return false;setBusy(true);setError('');try{setDocument(await api.reviewEntity(document.document_id,index,decision,corrected,note));await refresh();return true}catch(e){setError(String(e));return false}finally{setBusy(false)}};
 const finalize=async(decision:'approved'|'rejected')=>{if(!document)return false;setBusy(true);setError('');try{setDocument(await api.finalizeDocument(document.document_id,decision));await refresh();return true}catch(e){setError(String(e));return false}finally{setBusy(false)}};
 const rename=async(filename:string)=>{if(!document)return false;setBusy(true);setError('');try{setDocument(await api.renameDocument(document.document_id,filename));await refresh();return true}catch(e){setError(String(e));return false}finally{setBusy(false)}};
 const requestReview=async()=>{if(!document)return false;setBusy(true);setError('');try{setDocument(await api.requestDocumentReview(document.document_id));await refresh();return true}catch(e){setError(String(e));return false}finally{setBusy(false)}};
 const remove=async()=>{if(!document)return false;setBusy(true);setError('');try{await api.deleteDocument(document.document_id);setDocument(null);setSelectedId('');await refresh();return true}catch(e){setError(String(e));return false}finally{setBusy(false)}};
 return {rename,requestReview,remove,documents,document,selectedId,setSelectedId,loading,busy,error,setError,refresh,upload,review,finalize};
}
