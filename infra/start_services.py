#!/usr/bin/env python3
"""
Service Startup Script for The_Bridge
Starts Memory Bank API and other key services for testing
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path
from datetime import datetime

# Configuration
SERVICES = {
    'memory_bank': {
        'name': 'Memory Bank API',
        'path': 'The_Bridge/MemoryBank--API__DEV@v0.1.0/app.py',
        'port': 8088,
        'env': {
            'PYTHONPATH': '/mnt/c/users/password/continuum_Overworld',
            'API_PORT': '8088'
        }
    }
}

class ServiceManager:
    def __init__(self):
        self.processes = {}
        self.project_root = Path('/mnt/c/users/password/continuum_Overworld')
        
        # Handle shutdown signals
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received shutdown signal {signum}")
        self.stop_all_services()
        sys.exit(0)
    
    def start_service(self, service_name, config):
        """Start a single service"""
        service_path = self.project_root / config['path']
        
        if not service_path.exists():
            print(f"❌ Service file not found: {service_path}")
            return False
        
        print(f"🚀 Starting {config['name']}...")
        
        # Set up environment
        env = os.environ.copy()
        env.update(config.get('env', {}))
        
        try:
            process = subprocess.Popen(
                [sys.executable, str(service_path)],
                cwd=service_path.parent,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes[service_name] = {
                'process': process,
                'config': config,
                'started_at': datetime.now()
            }
            
            # Give service time to start
            time.sleep(2)
            
            if process.poll() is None:
                print(f"✅ {config['name']} started successfully (PID: {process.pid})")
                if 'port' in config:
                    print(f"   📡 Available at: http://localhost:{config['port']}")
                return True
            else:
                print(f"❌ {config['name']} failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Error starting {config['name']}: {e}")
            return False
    
    def stop_service(self, service_name):
        """Stop a single service"""
        if service_name not in self.processes:
            return
        
        service_info = self.processes[service_name]
        process = service_info['process']
        config = service_info['config']
        
        print(f"🛑 Stopping {config['name']}...")
        
        try:
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=5)
                print(f"✅ {config['name']} stopped gracefully")
            except subprocess.TimeoutExpired:
                print(f"⚡ Force killing {config['name']}...")
                process.kill()
                process.wait()
                
        except Exception as e:
            print(f"❌ Error stopping {config['name']}: {e}")
        
        finally:
            del self.processes[service_name]
    
    def stop_all_services(self):
        """Stop all running services"""
        print("\n🛑 Stopping all services...")
        
        for service_name in list(self.processes.keys()):
            self.stop_service(service_name)
        
        print("✅ All services stopped")
    
    def start_all_services(self):
        """Start all configured services"""
        print("🌉 THE_BRIDGE SERVICE MANAGER")
        print("=" * 50)
        
        started = 0
        failed = 0
        
        for service_name, config in SERVICES.items():
            if self.start_service(service_name, config):
                started += 1
            else:
                failed += 1
        
        print("\n" + "=" * 50)
        print(f"📊 Services: {started} started, {failed} failed")
        
        if started > 0:
            print("\n💡 Services are running. Press Ctrl+C to stop all services.")
            return True
        else:
            print("\n❌ No services started successfully")
            return False
    
    def monitor_services(self):
        """Monitor running services"""
        if not self.processes:
            print("No services running")
            return
        
        try:
            while self.processes:
                # Check service health
                for service_name in list(self.processes.keys()):
                    service_info = self.processes[service_name]
                    process = service_info['process']
                    
                    if process.poll() is not None:
                        print(f"\n❌ {service_info['config']['name']} has stopped unexpectedly")
                        del self.processes[service_name]
                
                if not self.processes:
                    print("\n⚠️ All services have stopped")
                    break
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            pass
    
    def get_service_status(self):
        """Get status of all services"""
        if not self.processes:
            print("No services running")
            return
        
        print("\n📊 SERVICE STATUS")
        print("-" * 30)
        
        for service_name, service_info in self.processes.items():
            process = service_info['process']
            config = service_info['config']
            started_at = service_info['started_at']
            
            uptime = datetime.now() - started_at
            status = "RUNNING" if process.poll() is None else "STOPPED"
            
            print(f"{config['name']}: {status}")
            print(f"  PID: {process.pid}")
            print(f"  Uptime: {uptime}")
            if 'port' in config:
                print(f"  Port: {config['port']}")
            print()

def main():
    """Main entry point"""
    manager = ServiceManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'start':
            if manager.start_all_services():
                manager.monitor_services()
        elif command == 'status':
            manager.get_service_status()
        elif command == 'stop':
            manager.stop_all_services()
        else:
            print("Usage: python start_services.py [start|stop|status]")
            sys.exit(1)
    else:
        # Default: start and monitor
        if manager.start_all_services():
            manager.monitor_services()

if __name__ == "__main__":
    main()