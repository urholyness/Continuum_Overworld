import ExcelJS from 'exceljs';
import fs from 'node:fs/promises';
import path from 'node:path';

export interface ExportData {
  run_id: string;
  timestamp: string;
  mode: 'real' | 'sim';
  data: any[];
  provenance?: {
    url: string;
    hash: string;
    api_version?: string;
  };
}

export async function exportToExcel(data: ExportData, outputPath?: string): Promise<string> {
  const workbook = new ExcelJS.Workbook();
  
  // Metadata sheet
  const metaSheet = workbook.addWorksheet('Metadata');
  metaSheet.addRow(['Field', 'Value']);
  metaSheet.addRow(['Run ID', data.run_id]);
  metaSheet.addRow(['Timestamp', data.timestamp]);
  metaSheet.addRow(['Mode', data.mode]);
  metaSheet.addRow(['Record Count', data.data.length]);
  
  if (data.provenance) {
    metaSheet.addRow(['Source URL', data.provenance.url]);
    metaSheet.addRow(['Source Hash', data.provenance.hash]);
    if (data.provenance.api_version) {
      metaSheet.addRow(['API Version', data.provenance.api_version]);
    }
  }
  
  // Data sheet
  const dataSheet = workbook.addWorksheet('Cargo Data');
  
  if (data.data.length > 0) {
    // Headers from first record
    const headers = Object.keys(data.data[0]);
    dataSheet.addRow(headers);
    
    // Data rows
    data.data.forEach(record => {
      const row = headers.map(header => record[header]);
      dataSheet.addRow(row);
    });
    
    // Format headers
    const headerRow = dataSheet.getRow(1);
    headerRow.font = { bold: true };
    headerRow.fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FFE0E0E0' }
    };
  }
  
  // Auto-fit columns
  dataSheet.columns.forEach(column => {
    if (column.header) {
      column.width = Math.max(column.header.toString().length + 2, 12);
    }
  });
  
  // Save file
  const filename = outputPath || `/tmp/lufthansa_cargo_${data.run_id}_${Date.now()}.xlsx`;
  await workbook.xlsx.writeFile(filename);
  
  return filename;
}