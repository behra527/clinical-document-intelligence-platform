export type Entity = {label:string;text:string;block_id:string;start:number;end:number;status:'candidate'|'verified'|'rejected';normalized?:Record<string,unknown>|null;corrected_text?:string|null;reviewer_note?:string|null};
export type SourceBlock = {block_id:string;text:string;confidence?:number|null;source_method?:string;type?:string;page_number?:number;bbox?:number[]|null;coordinate_system?:string|null;source_location?:Record<string,unknown>};
export type DocumentResult = {document_id:string;filename:string;created_at?:string;extraction_version?:string;mime_type?:string;status:string;review_status:string;size_bytes?:number;sha256?:string;metadata?:Record<string,unknown>;pages:{page_number:number;blocks:SourceBlock[];warnings?:string[]}[];clinical_entities:Entity[];warnings:string[]};
export type DocumentSummary = {document_id:string;filename:string;status:string;review_status:string};
export type View = 'documents'|'overview'|'review';
