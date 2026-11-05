import type {DocumentResult} from '../types/documents';
export const pretty=(s:string)=>s.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase());
export const isPdf=(d:DocumentResult)=>d.mime_type==='application/pdf'||d.filename.toLowerCase().endsWith('.pdf');
