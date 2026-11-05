import type {DocumentResult,DocumentSummary} from '../types/documents';
const base='/api/v1/documents';
async function request<T>(url:string,options:RequestInit={}):Promise<T>{
 const response=await fetch(url,{...options,credentials:'same-origin',cache:'no-store'});
 if(!response.ok){let detail='';try{const data:unknown=await response.json();detail=typeof data==='object'&&data!==null&&'detail' in data?String((data as {detail:unknown}).detail):JSON.stringify(data)}catch{detail=response.statusText}throw new Error(`HTTP ${response.status}: ${detail}`)}
 return response.json() as Promise<T>;
}
export const listDocuments=()=>request<DocumentSummary[]>(base);
export const getDocument=(id:string)=>request<DocumentResult>(`${base}/${encodeURIComponent(id)}`);
export async function uploadDocument(file:File){const body=new FormData();body.append('file',file);return request<DocumentResult>(base,{method:'POST',body})}
export function reviewEntity(id:string,index:number,decision:'verified'|'rejected',corrected_text?:string,note?:string){return request<DocumentResult>(`${base}/${encodeURIComponent(id)}/entities/${index}`,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({decision,corrected_text:corrected_text||undefined,note:note||undefined})})}
export function finalizeDocument(id:string,decision:'approved'|'rejected'){return request<DocumentResult>(`${base}/${encodeURIComponent(id)}/review?decision=${decision}`,{method:'POST'})}

export function renameDocument(id:string,filename:string){return request<DocumentResult>(`${base}/${encodeURIComponent(id)}/metadata`,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({filename})})}
export function requestDocumentReview(id:string){return request<DocumentResult>(`${base}/${encodeURIComponent(id)}/review-status`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({status:'pending'})})}
export const listArchived=()=>request<DocumentSummary[]>(`${base}/archived/list`);
export const restoreDocument=(id:string)=>request<DocumentResult>(`${base}/${encodeURIComponent(id)}/restore`,{method:'POST'});
export async function deleteDocument(id:string){const response=await fetch(`${base}/${encodeURIComponent(id)}`,{method:'DELETE',credentials:'same-origin',cache:'no-store'});if(!response.ok)throw new Error(`Archive failed: HTTP ${response.status}`)}
