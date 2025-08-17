#!/usr/bin/env python3
"""
start_services_enhanced.py

Enhanced service manager for the Local AI Package that supports:
- Service configuration via services.yml
- Dynamic Docker Compose generation
- Configurable port mappings
- Service enable/disable functionality
- Portainer integration

This script replaces the original start_services.py with enhanced configuration capabilities.
"""

import os
import subprocess
import shutil
import time
import argparse
import platform
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

class ServiceManager:
    def __init__(self, config_file: str = "services.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.project_name = self.config.get('global', {}).get('project_name', 'localai')
        self.default_host_ip = self.config.get('global', {}).get('default_host_ip', '127.0.0.1')
        
    def load_config(self) -> Dict[str, Any]:
        """Load service configuration from JSON file."""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Configuration file {self.config_file} not found")
        
        with open(self.config_file, 'r') as file:
            config = json.load(file)
            
        # Substitute variables in the configuration
        self._substitute_variables(config)
        return config
    
    def _substitute_variables(self, config: Dict[str, Any]) -> None:
        """Substitute variables like ${default_host_ip} in the configuration."""
        default_host_ip = config.get('global', {}).get('default_host_ip', '127.0.0.1')
        
        def substitute_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    obj[key] = substitute_recursive(value)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    obj[i] = substitute_recursive(item)
            elif isinstance(obj, str):
                return obj.replace('${default_host_ip}', default_host_ip)
            return obj
        
        substitute_recursive(config)
    
    def validate_config(self) -> bool:
        """Validate the service configuration."""
        required_sections = ['global', 'services', 'profiles']
        for section in required_sections:
            if section not in self.config:
                print(f"Error: Missing required section '{section}' in configuration")
                return False
        
        # Check for port conflicts
        used_ports = {}
        for service_name, service_config in self.config['services'].items():
            if not service_config.get('enabled', False):
                continue
                
            for port_config in service_config.get('ports', []):
                host_port = port_config['host_port']
                host_ip = port_config['host_ip']
                key = f"{host_ip}:{host_port}"
                
                if key in used_ports:
                    print(f"Error: Port conflict! {key} is used by both {used_ports[key]} and {service_name}")
                    return False
                used_ports[key] = service_name
        
        print("✓ Configuration validation passed")
        return True
    
    def get_enabled_services(self, profile: Optional[str] = None) -> List[str]:
        """Get list of enabled services, optionally filtered by profile."""
        enabled_services = []
        
        for service_name, service_config in self.config['services'].items():
            if not service_config.get('enabled', False):
                continue
                
            # Check if service is included in the specified profile
            if profile and profile != 'all':
                service_profiles = service_config.get('profiles', [])
                profile_services = self.config.get('profiles', {}).get(profile, {}).get('included_services', [])
                
                if profile in service_profiles or service_name in profile_services:
                    enabled_services.append(service_name)
            else:
                enabled_services.append(service_name)
        
        return enabled_services
    
    def generate_override_file(self, services: List[str], environment: str = 'private') -> str:
        """Generate dynamic Docker Compose override file for enabled services."""
        override_config = {
            'services': {}
        }
        
        for service_name in services:
            service_config = self.config['services'].get(service_name, {})
            ports = service_config.get('ports', [])
            
            if not ports:
                continue
                
            # Generate port mappings
            port_mappings = []
            for port_config in ports:
                host_ip = port_config['host_ip']
                host_port = port_config['host_port']
                container_port = port_config['container_port']
                protocol = port_config.get('protocol', 'tcp')
                
                # Format: "host_ip:host_port:container_port/protocol"
                if environment == 'private':
                    port_mapping = f"{host_ip}:{host_port}:{container_port}/{protocol}"
                else:  # public environment - only expose necessary ports
                    if service_name in ['caddy']:  # Only expose reverse proxy
                        if host_ip == '0.0.0.0':
                            port_mapping = f"{host_port}:{container_port}/{protocol}"
                        else:
                            continue  # Skip non-public ports in public environment
                    else:
                        continue  # Skip all other services in public environment
                
                port_mappings.append(port_mapping)
            
            if port_mappings:
                override_config['services'][service_name] = {
                    'ports': port_mappings
                }
        
        # Write override file as YAML format (we'll generate YAML manually without PyYAML)
        override_filename = f"docker-compose.override.{environment}.generated.yml"
        
        # Convert to YAML format manually
        yaml_content = self._dict_to_yaml(override_config)
        
        with open(override_filename, 'w') as file:
            file.write(yaml_content)
        
        print(f"✓ Generated override file: {override_filename}")
        return override_filename
    
    def generate_caddyfile(self, services: List[str]) -> None:
        """Generate dynamic Caddyfile for enabled services with reverse_proxy."""
        caddy_config = []
        
        # Global options
        caddy_config.append("{\n    email {$LETSENCRYPT_EMAIL}\n}")
        caddy_config.append("")
        
        # Add reverse proxy entries for enabled services
        for service_name in services:
            service_config = self.config['services'].get(service_name, {})
            
            if not service_config.get('reverse_proxy', False):
                continue
            
            # Get container port (first port in the list)
            ports = service_config.get('ports', [])
            if not ports:
                continue
                
            container_port = ports[0]['container_port']
            
            # Generate hostname variable and proxy entry
            hostname_var = self._get_hostname_variable(service_name)
            caddy_config.append(f"# {service_config.get('description', service_name)}")
            caddy_config.append(f"{{{hostname_var}}} {{")
            caddy_config.append(f"    reverse_proxy {service_name}:{container_port}")
            caddy_config.append("}")
            caddy_config.append("")
        
        # Add custom addon imports
        caddy_config.append("import /etc/caddy/addons/*.conf")
        caddy_config.append("")
        
        # Write Caddyfile
        caddyfile_content = "\n".join(caddy_config)
        with open("Caddyfile.generated", 'w') as file:
            file.write(caddyfile_content)
        
        print("✓ Generated Caddyfile: Caddyfile.generated")
    
    def _get_hostname_variable(self, service_name: str) -> str:
        """Get the hostname environment variable for a service."""
        hostname_map = {
            'n8n': '$N8N_HOSTNAME',
            'open-webui': '$WEBUI_HOSTNAME',
            'flowise': '$FLOWISE_HOSTNAME',
            'langfuse-web': '$LANGFUSE_HOSTNAME',
            'neo4j': '$NEO4J_HOSTNAME',
            'searxng': '$SEARXNG_HOSTNAME',
            'portainer': '$PORTAINER_HOSTNAME'
        }
        return hostname_map.get(service_name, f'${service_name.upper().replace("-", "_")}_HOSTNAME')
    
    def _dict_to_yaml(self, data: Dict[str, Any], indent: int = 0) -> str:
        """Convert dictionary to YAML format without using PyYAML."""
        yaml_lines = []
        indent_str = "  " * indent
        
        for key, value in data.items():
            if isinstance(value, dict):
                yaml_lines.append(f"{indent_str}{key}:")
                yaml_lines.append(self._dict_to_yaml(value, indent + 1))
            elif isinstance(value, list):
                yaml_lines.append(f"{indent_str}{key}:")
                for item in value:
                    if isinstance(item, str):
                        yaml_lines.append(f"{indent_str}  - {item}")
                    else:
                        yaml_lines.append(f"{indent_str}  - {item}")
            else:
                yaml_lines.append(f"{indent_str}{key}: {value}")
        
        return "\n".join(yaml_lines)
    
    def print_service_summary(self, services: List[str], profile: str) -> None:
        """Print a summary of enabled services and their access URLs."""
        print(f"\n🚀 Starting Local AI Package with profile: {profile}")
        print(f"📦 Enabled services ({len(services)}):\n")
        
        categories = {}
        for service_name in services:
            service_config = self.config['services'].get(service_name, {})
            category = service_config.get('category', 'other')
            
            if category not in categories:
                categories[category] = []
            categories[category].append((service_name, service_config))
        
        # Display services by category
        for category, service_list in categories.items():
            print(f"  📁 {category.title()}:")
            for service_name, service_config in service_list:
                description = service_config.get('description', 'No description')
                ports = service_config.get('ports', [])
                if ports:
                    port_info = f":{ports[0]['host_port']}"
                else:
                    port_info = ""
                
                print(f"    ✓ {service_name}{port_info} - {description}")
            print()
        
        print("🌐 Access URLs (after startup):")
        for service_name in services:
            service_config = self.config['services'].get(service_name, {})
            if service_config.get('reverse_proxy') or service_name in ['open-webui', 'n8n', 'flowise']:
                ports = service_config.get('ports', [])
                if ports:
                    host_ip = ports[0]['host_ip']
                    host_port = ports[0]['host_port']
                    if host_ip == '127.0.0.1':
                        print(f"  🔗 {service_name}: http://localhost:{host_port}")
        print()

def run_command(cmd, cwd=None):
    """Run a shell command and print it."""
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)

def clone_supabase_repo():
    """Clone the Supabase repository using sparse checkout if not already present."""
    if not os.path.exists("supabase"):
        print("Cloning the Supabase repository...")
        run_command([
            "git", "clone", "--filter=blob:none", "--no-checkout",
            "https://github.com/supabase/supabase.git"
        ])
        os.chdir("supabase")
        run_command(["git", "sparse-checkout", "init", "--cone"])
        run_command(["git", "sparse-checkout", "set", "docker"])
        run_command(["git", "checkout", "master"])
        os.chdir("..")
    else:
        print("Supabase repository already exists, updating...")
        os.chdir("supabase")
        run_command(["git", "pull"])
        os.chdir("..")

def prepare_supabase_env():
    """Copy .env to .env in supabase/docker."""
    env_path = os.path.join("supabase", "docker", ".env")
    env_example_path = os.path.join(".env")
    print("Copying .env in root to .env in supabase/docker...")
    shutil.copyfile(env_example_path, env_path)

def stop_existing_containers(project_name: str, profile: Optional[str] = None):
    """Stop existing containers for the project."""
    print(f"Stopping and removing existing containers for project '{project_name}'...")
    cmd = ["docker", "compose", "-p", project_name]
    if profile and profile != "none":
        cmd.extend(["--profile", profile])
    cmd.extend(["-f", "docker-compose.yml", "down"])
    run_command(cmd)

def start_supabase(project_name: str, environment: Optional[str] = None):
    """Start the Supabase services."""
    print("Starting Supabase services...")
    cmd = ["docker", "compose", "-p", project_name, "-f", "supabase/docker/docker-compose.yml"]
    if environment and environment == "public":
        cmd.extend(["-f", "docker-compose.override.public.supabase.yml"])
    cmd.extend(["up", "-d"])
    run_command(cmd)

def start_local_ai(project_name: str, profile: Optional[str] = None, 
                  environment: Optional[str] = None, override_file: Optional[str] = None):
    """Start the local AI services."""
    print("Starting local AI services...")
    cmd = ["docker", "compose", "-p", project_name]
    if profile and profile != "none":
        cmd.extend(["--profile", profile])
    cmd.extend(["-f", "docker-compose.yml"])
    
    if override_file and os.path.exists(override_file):
        cmd.extend(["-f", override_file])
    elif environment == "private" and os.path.exists("docker-compose.override.private.yml"):
        cmd.extend(["-f", "docker-compose.override.private.yml"])
    elif environment == "public" and os.path.exists("docker-compose.override.public.yml"):
        cmd.extend(["-f", "docker-compose.override.public.yml"])
    
    cmd.extend(["up", "-d"])
    run_command(cmd)

def generate_searxng_secret_key():
    """Generate a secret key for SearXNG."""
    # Using the same logic as the original script
    print("Checking SearXNG settings...")
    
    settings_path = os.path.join("searxng", "settings.yml")
    settings_base_path = os.path.join("searxng", "settings-base.yml")
    
    if not os.path.exists(settings_base_path):
        print(f"Warning: SearXNG base settings file not found at {settings_base_path}")
        return
    
    if not os.path.exists(settings_path):
        print(f"SearXNG settings.yml not found. Creating from {settings_base_path}...")
        try:
            shutil.copyfile(settings_base_path, settings_path)
            print(f"Created {settings_path} from {settings_base_path}")
        except Exception as e:
            print(f"Error creating settings.yml: {e}")
            return
    
    print("Generating SearXNG secret key...")
    system = platform.system()
    
    try:
        if system == "Windows":
            # Windows PowerShell implementation
            ps_command = [
                "powershell", "-Command",
                "$randomBytes = New-Object byte[] 32; " +
                "(New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes($randomBytes); " +
                "$secretKey = -join ($randomBytes | ForEach-Object { \"{0:x2}\" -f $_ }); " +
                "(Get-Content searxng/settings.yml) -replace 'ultrasecretkey', $secretKey | Set-Content searxng/settings.yml"
            ]
            subprocess.run(ps_command, check=True)
        else:
            # Linux/macOS implementation
            openssl_cmd = ["openssl", "rand", "-hex", "32"]
            random_key = subprocess.check_output(openssl_cmd).decode('utf-8').strip()
            
            if system == "Darwin":  # macOS
                sed_cmd = ["sed", "-i", "", f"s|ultrasecretkey|{random_key}|g", settings_path]
            else:  # Linux
                sed_cmd = ["sed", "-i", f"s|ultrasecretkey|{random_key}|g", settings_path]
            
            subprocess.run(sed_cmd, check=True)
        
        print("SearXNG secret key generated successfully.")
    except Exception as e:
        print(f"Error generating SearXNG secret key: {e}")

def main():
    parser = argparse.ArgumentParser(description='Enhanced Local AI Package service manager.')
    parser.add_argument('--profile', choices=['cpu', 'gpu-nvidia', 'gpu-amd', 'none'], default='cpu',
                      help='Profile to use for Docker Compose (default: cpu)')
    parser.add_argument('--environment', choices=['private', 'public'], default='private',
                      help='Environment to use for Docker Compose (default: private)')
    parser.add_argument('--config', default='services.json',
                      help='Service configuration file (default: services.json)')
    parser.add_argument('--no-supabase', action='store_true',
                      help='Skip Supabase setup and startup')
    parser.add_argument('--dry-run', action='store_true',
                      help='Show what would be started without actually starting services')
    parser.add_argument('--list-services', action='store_true',
                      help='List all available services and exit')
    
    args = parser.parse_args()
    
    # Initialize service manager
    try:
        service_manager = ServiceManager(args.config)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure services.json exists or specify a different config file with --config")
        sys.exit(1)
    
    # List services if requested
    if args.list_services:
        print("Available services:")
        for service_name, service_config in service_manager.config['services'].items():
            enabled = "✓" if service_config.get('enabled') else "✗"
            description = service_config.get('description', 'No description')
            print(f"  {enabled} {service_name} - {description}")
        return
    
    # Validate configuration
    if not service_manager.validate_config():
        sys.exit(1)
    
    # Get enabled services for the profile
    enabled_services = service_manager.get_enabled_services(args.profile)
    
    if not enabled_services:
        print(f"No services enabled for profile '{args.profile}'")
        sys.exit(1)
    
    # Show summary
    service_manager.print_service_summary(enabled_services, args.profile)
    
    if args.dry_run:
        print("Dry run - not starting any services")
        return
    
    # Generate dynamic configuration files
    override_file = service_manager.generate_override_file(enabled_services, args.environment)
    service_manager.generate_caddyfile(enabled_services)
    
    # Setup Supabase if needed
    if not args.no_supabase and any(service_manager.config['services'].get(s, {}).get('supabase') for s in enabled_services):
        clone_supabase_repo()
        prepare_supabase_env()
    
    # Generate SearXNG secret if SearXNG is enabled
    if 'searxng' in enabled_services:
        generate_searxng_secret_key()
    
    # Stop existing containers
    stop_existing_containers(service_manager.project_name, args.profile)
    
    # Start Supabase first if needed
    if not args.no_supabase and any(service_manager.config['services'].get(s, {}).get('supabase') for s in enabled_services):
        start_supabase(service_manager.project_name, args.environment)
        print("Waiting for Supabase to initialize...")
        time.sleep(10)
    
    # Start local AI services
    start_local_ai(service_manager.project_name, args.profile, args.environment, override_file)
    
    print("\n🎉 Local AI Package startup complete!")
    print("Check the logs with: docker compose -p localai logs -f")

if __name__ == "__main__":
    main()