#!/usr/bin/env python3
"""
DataHub Governance Hooks
Integrates The_Bridge with DataHub for data governance and lineage
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import requests

# Configuration
DATAHUB_CONFIG = {
    'gms_server': os.getenv('DATAHUB_GMS_SERVER', 'http://localhost:8080'),
    'token': os.getenv('DATAHUB_ACCESS_TOKEN'),
    'enabled': os.getenv('DATAHUB_ENABLED', 'false').lower() == 'true'
}

logger = logging.getLogger('datahub_hooks')

class DataHubIntegration:
    """DataHub integration for governance and lineage tracking"""
    
    def __init__(self):
        self.gms_server = DATAHUB_CONFIG['gms_server']
        self.token = DATAHUB_CONFIG['token']
        self.enabled = DATAHUB_CONFIG['enabled']
        self.session = requests.Session()
        
        if self.token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            })
    
    def _emit_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Emit metadata to DataHub"""
        if not self.enabled:
            logger.debug("DataHub integration disabled, skipping metadata emission")
            return True
        
        try:
            response = self.session.post(
                f"{self.gms_server}/entities?action=ingest",
                json=metadata,
                timeout=10
            )
            
            response.raise_for_status()
            logger.info(f"Successfully emitted metadata to DataHub")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to emit metadata to DataHub: {e}")
            return False
    
    def register_dataset(self, dataset_urn: str, dataset_info: Dict[str, Any]) -> bool:
        """Register a dataset in DataHub"""
        metadata = {
            "entityType": "dataset",
            "entityUrn": dataset_urn,
            "aspectName": "datasetProperties",
            "aspect": {
                "description": dataset_info.get('description', ''),
                "customProperties": {
                    "tenant_id": dataset_info.get('tenant_id', ''),
                    "project_tag": dataset_info.get('project_tag', ''),
                    "created_by": "the_bridge_foundation",
                    "governance_level": dataset_info.get('governance_level', 'standard')
                },
                "tags": dataset_info.get('tags', [])
            }
        }
        
        return self._emit_metadata(metadata)
    
    def register_data_job(self, job_urn: str, job_info: Dict[str, Any]) -> bool:
        """Register a data processing job (dbt model, ETL, etc.)"""
        metadata = {
            "entityType": "dataJob",
            "entityUrn": job_urn,
            "aspectName": "dataJobInfo",
            "aspect": {
                "name": job_info['name'],
                "description": job_info.get('description', ''),
                "type": job_info.get('type', 'DBT'),
                "customProperties": {
                    "model_type": job_info.get('model_type', ''),
                    "materialization": job_info.get('materialization', ''),
                    "tenant_scope": job_info.get('tenant_scope', 'multi'),
                    "bridge_component": job_info.get('component', 'dbt')
                }
            }
        }
        
        return self._emit_metadata(metadata)
    
    def register_lineage(self, upstream_urns: list, downstream_urn: str, job_urn: str) -> bool:
        """Register data lineage between datasets"""
        metadata = {
            "entityType": "dataJob",
            "entityUrn": job_urn,
            "aspectName": "dataJobInputOutput",
            "aspect": {
                "inputDatasets": [{"string": urn} for urn in upstream_urns],
                "outputDatasets": [{"string": downstream_urn}]
            }
        }
        
        return self._emit_metadata(metadata)

class BridgeGovernanceHooks:
    """Governance hooks for The_Bridge foundation"""
    
    def __init__(self):
        self.datahub = DataHubIntegration()
    
    def on_document_ingested(self, tenant_id: str, doc_id: str, doc_type: str, metadata: Dict[str, Any]):
        """Hook called when a document is ingested"""
        dataset_urn = f"urn:li:dataset:(urn:li:dataPlatform:the_bridge,{tenant_id}.core.document,PROD)"
        
        dataset_info = {
            'description': f'Document store for tenant {tenant_id}',
            'tenant_id': tenant_id,
            'project_tag': metadata.get('project_tag', ''),
            'governance_level': 'high' if doc_type == 'csr_report' else 'standard',
            'tags': [
                'the_bridge',
                'multi_tenant',
                doc_type,
                f'tenant:{tenant_id}'
            ]
        }
        
        self.datahub.register_dataset(dataset_urn, dataset_info)
        logger.info(f"Registered document dataset for tenant {tenant_id}")
    
    def on_esg_metric_extracted(self, tenant_id: str, doc_id: str, metrics_count: int):
        """Hook called when ESG metrics are extracted"""
        dataset_urn = f"urn:li:dataset:(urn:li:dataPlatform:the_bridge,{tenant_id}.core.esg_metric,PROD)"
        job_urn = f"urn:li:dataJob:(urn:li:dataFlow:(the_bridge,esg_extraction,PROD),esg_calculator)"
        
        # Register ESG metrics dataset
        dataset_info = {
            'description': f'ESG metrics extracted from documents for tenant {tenant_id}',
            'tenant_id': tenant_id,
            'governance_level': 'high',
            'tags': ['esg', 'metrics', 'sustainability', f'tenant:{tenant_id}']
        }
        
        self.datahub.register_dataset(dataset_urn, dataset_info)
        
        # Register extraction job
        job_info = {
            'name': 'ESG Metric Extraction',
            'description': 'Extracts ESG metrics from CSR documents using regex patterns',
            'type': 'PYTHON',
            'component': 'oracle_calculator'
        }
        
        self.datahub.register_data_job(job_urn, job_info)
        logger.info(f"Registered ESG extraction job for tenant {tenant_id}, {metrics_count} metrics")
    
    def on_memory_doc_created(self, tenant_id: str, doc_id: str, scope: str):
        """Hook called when a memory document is created"""
        dataset_urn = f"urn:li:dataset:(urn:li:dataPlatform:the_bridge,{tenant_id}.core.memory_doc,PROD)"
        
        dataset_info = {
            'description': f'Agent memory bank for tenant {tenant_id}',
            'tenant_id': tenant_id,
            'governance_level': 'standard',
            'tags': ['memory_bank', 'vector_search', 'agent_memory', f'tenant:{tenant_id}', f'scope:{scope}']
        }
        
        self.datahub.register_dataset(dataset_urn, dataset_info)
        logger.info(f"Registered memory document for tenant {tenant_id}, scope {scope}")
    
    def on_dbt_model_run(self, model_name: str, model_type: str, tenant_scope: str = 'multi'):
        """Hook called when dbt models are executed"""
        job_urn = f"urn:li:dataJob:(urn:li:dataFlow:(the_bridge,dbt_transformations,PROD),{model_name})"
        dataset_urn = f"urn:li:dataset:(urn:li:dataPlatform:the_bridge,{model_name},PROD)"
        
        # Register dbt model as a job
        job_info = {
            'name': model_name,
            'description': f'dbt {model_type} model for multi-tenant data transformations',
            'type': 'DBT',
            'model_type': model_type,
            'materialization': 'table' if model_type in ['silver', 'gold'] else 'view',
            'tenant_scope': tenant_scope,
            'component': 'dbt'
        }
        
        self.datahub.register_data_job(job_urn, job_info)
        
        # Register output dataset
        dataset_info = {
            'description': f'Transformed data from dbt {model_type} layer',
            'governance_level': 'high' if model_type == 'gold' else 'standard',
            'tags': ['dbt', model_type, 'transformed_data', 'multi_tenant']
        }
        
        self.datahub.register_dataset(dataset_urn, dataset_info)
        logger.info(f"Registered dbt model {model_name} ({model_type})")
    
    def register_bridge_platform(self):
        """Register The_Bridge as a platform in DataHub"""
        platform_metadata = {
            "entityType": "dataPlatform",
            "entityUrn": "urn:li:dataPlatform:the_bridge",
            "aspectName": "dataPlatformInfo",
            "aspect": {
                "name": "The_Bridge",
                "displayName": "The_Bridge Data Foundation",
                "description": "Multi-tenant data foundation with agent memory bank and event streaming",
                "logoUrl": "",
                "type": "OTHERS"
            }
        }
        
        self.datahub._emit_metadata(platform_metadata)
        logger.info("Registered The_Bridge platform in DataHub")

# Global instance
governance_hooks = BridgeGovernanceHooks()

def setup_governance_logging():
    """Setup logging for governance hooks"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_datahub_integration():
    """Test DataHub integration"""
    print("🔄 Testing DataHub integration...")
    
    if not DATAHUB_CONFIG['enabled']:
        print("⚠️ DataHub integration is disabled (set DATAHUB_ENABLED=true to enable)")
        return True
    
    try:
        # Test basic connectivity
        datahub = DataHubIntegration()
        
        # Register test dataset
        test_urn = "urn:li:dataset:(urn:li:dataPlatform:the_bridge,test.dataset,PROD)"
        test_info = {
            'description': 'Test dataset for DataHub integration',
            'tenant_id': 'TEST',
            'project_tag': 'GOVERNANCE-TEST',
            'tags': ['test', 'governance']
        }
        
        success = datahub.register_dataset(test_urn, test_info)
        
        if success:
            print("✅ DataHub integration test passed")
        else:
            print("❌ DataHub integration test failed")
        
        return success
        
    except Exception as e:
        print(f"❌ DataHub integration error: {e}")
        return False

if __name__ == "__main__":
    # Setup logging
    setup_governance_logging()
    
    # Test integration
    test_datahub_integration()
    
    # Register platform
    try:
        governance_hooks.register_bridge_platform()
        print("✅ DataHub governance hooks initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize governance hooks: {e}")