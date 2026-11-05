import {useEffect,useRef,useState} from 'react';
import {Eye,FileSearch,Layers} from 'lucide-react';
import type {DocumentResult,SourceBlock} from '../types/documents';
import {isPdf} from '../utils/format';
import PdfPreview from '../PdfPreview';

type Props={document:DocumentResult;focusBlock?:string};
function ReadablePage({blocks}: {blocks:SourceBlock[]}) {
 // OCR can return one block per word. Merge the words into readable text
 // while retaining each original block and its provenance in the evidence view.
 const text=blocks.map(b=>b.text.trim()).filter(Boolean).join(' ').replace(/\s+([,.;:!?])/g,'$1');
 return <div className="readableText">{text||'No readable text on this page.'}</div>;
}
export default function SourceViewer({document,focusBlock=''}:Props){
 const [tab,setTab]=useState<'pdf'|'ocr'>(isPdf(document)?'pdf':'ocr');
 const [showBlocks,setShowBlocks]=useState(false);
 const refs=useRef<Record<string,HTMLDivElement|null>>({});
 useEffect(()=>{setTab(isPdf(document)?'pdf':'ocr');setShowBlocks(false)},[document.document_id]);
 useEffect(()=>{if(!focusBlock)return;setTab('ocr');setShowBlocks(true);const timer=window.setTimeout(()=>refs.current[focusBlock]?.scrollIntoView({behavior:'smooth',block:'center'}),80);return()=>window.clearTimeout(timer)},[focusBlock]);
 return <div className="sourceShell"><div className="sourceTabs"><button className={tab==='pdf'?'active':''} disabled={!isPdf(document)} onClick={()=>setTab('pdf')}><Eye size={15}/> Original PDF</button><button className={tab==='ocr'?'active':''} onClick={()=>setTab('ocr')}><FileSearch size={15}/> Extracted text</button>{tab==='ocr'&&<button className={showBlocks?'active':''} onClick={()=>setShowBlocks(!showBlocks)}><Layers size={15}/> {showBlocks?'Readable view':'Evidence blocks'}</button>}</div>{tab==='pdf'&&isPdf(document)?<PdfPreview documentId={document.document_id}/>:<div className="sourceScroll">{document.pages.map(page=><div className="page" key={page.page_number}><div className="pageLabel">PAGE {page.page_number}</div>{showBlocks?page.blocks.map(block=><div key={block.block_id} ref={node=>{refs.current[block.block_id]=node}} className={`sourceBlock ${focusBlock===block.block_id?'highlight':''}`}><span>{block.text}</span><small>{block.block_id} | {block.source_method||'source'}{block.confidence!=null?` | ${Math.round(block.confidence*100)}%`:''}{block.type?` | ${block.type}`:''}{block.coordinate_system?` | ${block.coordinate_system}`:''}{block.bbox?` | bbox: ${block.bbox.map(n=>n.toFixed(1)).join(', ')}`:''}{Object.keys(block.source_location||{}).length?` | ${JSON.stringify(block.source_location)}`:''}</small></div>):<ReadablePage blocks={page.blocks}/>}</div>)}{document.pages.some(page=>page.warnings?.length)&&<div className="warning">{document.pages.flatMap(page=>(page.warnings||[]).map(w=>`Page ${page.page_number}: ${w}`)).map((w,i)=><p key={i}>{w}</p>)}</div>}{!document.pages.length&&<p className="muted">No extracted text available.</p>}</div>}</div>;
}
