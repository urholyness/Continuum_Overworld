// Adapter: call old Rank_AI (Ariadne_Weaver) or stub return for validator
export type KPI = { company_name:string; year:number; kpi_id:string; value:number; unit:string; confidence:number; source_url:string; source_hash:string; page_refs:number[]; basis?:string };
export type ContextSpan = { kpi_id:string; snippet:string; classification:"plan"|"pledge"|"progress"|"pr"; page_ref:number };

export async function extractFromPDF(pdfPath: string, source_url: string, source_hash: string): Promise<{kpis:KPI[], contexts:ContextSpan[]}>{
  // TODO integrate real extractor; stub minimal valid output to unblock validator
  return {
    kpis:[
      { company_name:"Nestlé", year:2023, kpi_id:"SAF_%", value:0.5, unit:"%", confidence:0.7, source_url, source_hash, page_refs:[12] }
    ],
    contexts:[
      { kpi_id:"SAF_%", snippet:"We plan to increase SAF usage...", classification:"plan", page_ref:12 }
    ]
  };
}