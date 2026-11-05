import {useState} from 'react';
import {Pencil, Trash2, ClipboardList} from 'lucide-react';
import type {DocumentResult} from '../types/documents';

type Props={document:DocumentResult;busy:boolean;rename:(name:string)=>Promise<boolean>;remove:()=>Promise<boolean>;requestReview:()=>Promise<boolean>};
export default function DocumentActions({document,busy,rename,remove,requestReview}:Props){
 const [editing,setEditing]=useState(false);
 const [name,setName]=useState(document.filename);
 const finalized=['approved','rejected'].includes(document.review_status);
 return <div className="documentActions">
  <button className="secondaryBtn" disabled={busy} onClick={()=>{setName(document.filename);setEditing(true)}}><Pencil size={15}/> Rename</button>
  <button className="secondaryBtn" disabled={busy||finalized||document.review_status==='pending'} title={finalized?'Finalized documents cannot be reopened':''} onClick={()=>{if(window.confirm('Mark this document as requiring human review?'))void requestReview()}}><ClipboardList size={15}/> Mark pending</button>
  <button className="secondaryBtn dangerBtn" disabled={busy} onClick={()=>{if(window.confirm(`Archive ${document.filename}? The original and audit history will be retained, and you can restore it later.`))void remove()}}><Trash2 size={15}/> Archive</button>
  {editing&&<div className="modalBackdrop" role="presentation"><form className="dialog" onSubmit={async e=>{e.preventDefault();if(await rename(name))setEditing(false)}}><h3>Rename document</h3><p>Change the display filename. The original stored file stays unchanged.</p><label htmlFor="renameFile">Filename</label><input id="renameFile" value={name} onChange={e=>setName(e.target.value)} required maxLength={255}/><div className="actions"><button type="button" className="secondaryBtn" onClick={()=>setEditing(false)}>Cancel</button><button type="submit" className="primaryBtn" disabled={busy||!name.trim()}>Save name</button></div></form></div>}
 </div>;
}
