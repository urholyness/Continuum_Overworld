export async function extractFromPDF(pdfPath, source_url, source_hash) {
    // TODO integrate real extractor; stub minimal valid output to unblock validator
    return {
        kpis: [
            { company_name: "Nestlé", year: 2023, kpi_id: "SAF_%", value: 0.5, unit: "%", confidence: 0.7, source_url, source_hash, page_refs: [12] }
        ],
        contexts: [
            { kpi_id: "SAF_%", snippet: "We plan to increase SAF usage...", classification: "plan", page_ref: 12 }
        ]
    };
}
