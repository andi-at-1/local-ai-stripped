#!/usr/bin/env python3
"""
configure_services.py

Interactive shell for configuring Local AI Package services.
Features:
- Check/uncheck services to enable/disable
- Edit ports and IP addresses
- Save configuration to services.json
- User-friendly interface with colored output
"""

import os
import json
import sys
from typing import Dict, List, Any, Optional

class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ServiceConfigurator:
    def __init__(self, config_file: str = "services.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load service configuration from JSON file."""
        if not os.path.exists(self.config_file):
            print(f"{Colors.FAIL}Error: Configuration file {self.config_file} not found{Colors.ENDC}")
            sys.exit(1)
        
        with open(self.config_file, 'r') as file:
            return json.load(file)
    
    def save_config(self) -> None:
        """Save current configuration to JSON file."""
        with open(self.config_file, 'w') as file:
            json.dump(self.config, file, indent=2)
        print(f"{Colors.OKGREEN}✓ Configuration saved to {self.config_file}{Colors.ENDC}")
    
    def print_header(self, title: str) -> None:
        """Print a formatted header."""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{title.center(60)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
    
    def print_service_list(self) -> None:
        """Display all services with their current status."""
        services = self.config['services']
        categories = {}
        
        # Group services by category
        for service_name, service_config in services.items():
            category = service_config.get('category', 'other')
            if category not in categories:
                categories[category] = []
            categories[category].append((service_name, service_config))
        
        print(f"{Colors.OKCYAN}Current Service Configuration:{Colors.ENDC}\n")
        
        service_index = 1
        self.service_index_map = {}
        
        for category, service_list in sorted(categories.items()):
            print(f"{Colors.OKBLUE}📁 {category.title()}:{Colors.ENDC}")
            for service_name, service_config in service_list:
                enabled = service_config.get('enabled', False)
                status_icon = f"{Colors.OKGREEN}✓{Colors.ENDC}" if enabled else f"{Colors.FAIL}✗{Colors.ENDC}"
                description = service_config.get('description', 'No description')[:50] + "..."
                
                # Store mapping for easy selection
                self.service_index_map[service_index] = service_name
                
                ports = service_config.get('ports', [])
                port_info = ""
                if ports:
                    port_info = f" ({ports[0]['host_ip']}:{ports[0]['host_port']})"
                
                print(f"  {service_index:2d}. {status_icon} {service_name}{port_info}")
                print(f"      {Colors.WARNING}{description}{Colors.ENDC}")
                service_index += 1
            print()
    
    def toggle_service(self, service_name: str) -> None:
        """Toggle a service's enabled status."""
        if service_name in self.config['services']:
            current_status = self.config['services'][service_name].get('enabled', False)
            self.config['services'][service_name]['enabled'] = not current_status
            new_status = "enabled" if not current_status else "disabled"
            status_color = Colors.OKGREEN if not current_status else Colors.WARNING
            print(f"{status_color}✓ Service '{service_name}' {new_status}{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}✗ Service '{service_name}' not found{Colors.ENDC}")
    
    def edit_service_ports(self, service_name: str) -> None:
        """Edit ports and IPs for a service."""
        if service_name not in self.config['services']:
            print(f"{Colors.FAIL}✗ Service '{service_name}' not found{Colors.ENDC}")
            return
        
        service_config = self.config['services'][service_name]
        ports = service_config.get('ports', [])
        
        if not ports:
            print(f"{Colors.WARNING}Service '{service_name}' has no configurable ports{Colors.ENDC}")
            return
        
        print(f"\n{Colors.OKCYAN}Editing ports for: {service_name}{Colors.ENDC}")
        print(f"Description: {service_config.get('description', 'No description')}")
        print(f"\nCurrent port configuration:")
        
        for i, port_config in enumerate(ports):
            host_ip = port_config.get('host_ip', '127.0.0.1')
            host_port = port_config.get('host_port', 0)
            container_port = port_config.get('container_port', 0)
            protocol = port_config.get('protocol', 'tcp')
            
            print(f"  Port {i+1}: {host_ip}:{host_port} -> {container_port}/{protocol}")
        
        print(f"\n{Colors.OKBLUE}What would you like to edit?{Colors.ENDC}")
        for i, port_config in enumerate(ports):
            print(f"  {i+1}. Edit port {i+1} mapping")
        print(f"  0. Back to main menu")
        
        try:
            choice = input(f"\n{Colors.BOLD}Enter choice (0-{len(ports)}): {Colors.ENDC}").strip()
            choice_num = int(choice)
            
            if choice_num == 0:
                return
            elif 1 <= choice_num <= len(ports):
                self.edit_single_port(service_name, choice_num - 1)
            else:
                print(f"{Colors.FAIL}Invalid choice. Please enter a number between 0 and {len(ports)}.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}Invalid input. Please enter a number.{Colors.ENDC}")
    
    def edit_single_port(self, service_name: str, port_index: int) -> None:
        """Edit a single port configuration."""
        port_config = self.config['services'][service_name]['ports'][port_index]
        
        print(f"\n{Colors.OKCYAN}Editing port {port_index + 1} for {service_name}:{Colors.ENDC}")
        print(f"Current: {port_config['host_ip']}:{port_config['host_port']} -> {port_config['container_port']}/{port_config.get('protocol', 'tcp')}")
        
        # Edit host IP
        current_ip = port_config.get('host_ip', '127.0.0.1')
        new_ip = input(f"\nHost IP [{current_ip}]: ").strip()
        if new_ip and new_ip != current_ip:
            port_config['host_ip'] = new_ip
            print(f"{Colors.OKGREEN}✓ Host IP updated to: {new_ip}{Colors.ENDC}")
        
        # Edit host port
        current_port = port_config.get('host_port', 0)
        new_port_str = input(f"Host Port [{current_port}]: ").strip()
        if new_port_str:
            try:
                new_port = int(new_port_str)
                if 1 <= new_port <= 65535:
                    if new_port != current_port:
                        # Check for port conflicts
                        if self.check_port_conflict(service_name, port_config['host_ip'], new_port):
                            print(f"{Colors.FAIL}✗ Port conflict detected! Port {new_port} is already in use.{Colors.ENDC}")
                            return
                        port_config['host_port'] = new_port
                        print(f"{Colors.OKGREEN}✓ Host port updated to: {new_port}{Colors.ENDC}")
                else:
                    print(f"{Colors.FAIL}✗ Invalid port number. Must be between 1-65535.{Colors.ENDC}")
            except ValueError:
                print(f"{Colors.FAIL}✗ Invalid port number.{Colors.ENDC}")
        
        print(f"{Colors.OKGREEN}Port configuration updated successfully!{Colors.ENDC}")
    
    def check_port_conflict(self, current_service: str, host_ip: str, host_port: int) -> bool:
        """Check if a port is already in use by another service."""
        for service_name, service_config in self.config['services'].items():
            if service_name == current_service or not service_config.get('enabled', False):
                continue
            
            for port_config in service_config.get('ports', []):
                if (port_config.get('host_ip') == host_ip and 
                    port_config.get('host_port') == host_port):
                    return True
        return False
    
    def show_profiles(self) -> None:
        """Show available profiles and their included services."""
        profiles = self.config.get('profiles', {})
        
        print(f"{Colors.OKCYAN}Available Profiles:{Colors.ENDC}\n")
        
        for profile_name, profile_config in profiles.items():
            description = profile_config.get('description', 'No description')
            included_services = profile_config.get('included_services', [])
            
            print(f"{Colors.OKBLUE}{profile_name.upper()}:{Colors.ENDC}")
            print(f"  Description: {description}")
            print(f"  Included services ({len(included_services)}): {', '.join(included_services[:5])}")
            if len(included_services) > 5:
                print(f"    ... and {len(included_services) - 5} more")
            print()
    
    def show_enabled_summary(self) -> None:
        """Show summary of currently enabled services."""
        enabled_services = []
        for service_name, service_config in self.config['services'].items():
            if service_config.get('enabled', False):
                enabled_services.append(service_name)
        
        print(f"{Colors.OKGREEN}Currently Enabled Services ({len(enabled_services)}):{Colors.ENDC}")
        if enabled_services:
            for service_name in enabled_services:
                service_config = self.config['services'][service_name]
                ports = service_config.get('ports', [])
                port_info = ""
                if ports:
                    port_info = f" → {ports[0]['host_ip']}:{ports[0]['host_port']}"
                print(f"  ✓ {service_name}{port_info}")
        else:
            print("  No services currently enabled")
        print()
    
    def main_menu(self) -> None:
        """Display and handle the main menu."""
        while True:
            self.print_header("Local AI Package Service Configurator")
            
            print(f"{Colors.OKBLUE}Options:{Colors.ENDC}")
            print("  1. 📋 View all services")
            print("  2. ⚙️  Toggle service (enable/disable)")
            print("  3. 🔧 Edit service ports/IPs")
            print("  4. 📊 Show enabled services summary")
            print("  5. 📁 Show available profiles")
            print("  6. 💾 Save configuration")
            print("  7. 🚀 Start services (using current config)")
            print("  0. ❌ Exit")
            
            try:
                choice = input(f"\n{Colors.BOLD}Enter your choice (0-7): {Colors.ENDC}").strip()
                
                if choice == '0':
                    print(f"\n{Colors.OKCYAN}Goodbye! 👋{Colors.ENDC}")
                    break
                elif choice == '1':
                    self.print_service_list()
                    input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
                elif choice == '2':
                    self.handle_toggle_service()
                elif choice == '3':
                    self.handle_edit_ports()
                elif choice == '4':
                    self.show_enabled_summary()
                    input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
                elif choice == '5':
                    self.show_profiles()
                    input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
                elif choice == '6':
                    self.save_config()
                    input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
                elif choice == '7':
                    self.start_services()
                else:
                    print(f"{Colors.FAIL}Invalid choice. Please enter a number between 0-7.{Colors.ENDC}")
                    input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
                    
            except KeyboardInterrupt:
                print(f"\n\n{Colors.OKCYAN}Goodbye! 👋{Colors.ENDC}")
                break
            except Exception as e:
                print(f"{Colors.FAIL}An error occurred: {e}{Colors.ENDC}")
                input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
    
    def handle_toggle_service(self) -> None:
        """Handle toggling a service's enabled status."""
        self.print_service_list()
        
        try:
            choice = input(f"\n{Colors.BOLD}Enter service number to toggle (0 to cancel): {Colors.ENDC}").strip()
            choice_num = int(choice)
            
            if choice_num == 0:
                return
            elif choice_num in self.service_index_map:
                service_name = self.service_index_map[choice_num]
                self.toggle_service(service_name)
                input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}Invalid service number.{Colors.ENDC}")
                input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}Invalid input. Please enter a number.{Colors.ENDC}")
            input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
    
    def handle_edit_ports(self) -> None:
        """Handle editing service ports."""
        self.print_service_list()
        
        try:
            choice = input(f"\n{Colors.BOLD}Enter service number to edit ports (0 to cancel): {Colors.ENDC}").strip()
            choice_num = int(choice)
            
            if choice_num == 0:
                return
            elif choice_num in self.service_index_map:
                service_name = self.service_index_map[choice_num]
                self.edit_service_ports(service_name)
                input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}Invalid service number.{Colors.ENDC}")
                input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}Invalid input. Please enter a number.{Colors.ENDC}")
            input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
    
    def start_services(self) -> None:
        """Start services using the enhanced script."""
        print(f"\n{Colors.OKCYAN}Starting services with current configuration...{Colors.ENDC}")
        self.save_config()
        
        print(f"\n{Colors.OKBLUE}Available profiles:{Colors.ENDC}")
        profiles = list(self.config.get('profiles', {}).keys())
        for i, profile in enumerate(profiles, 1):
            print(f"  {i}. {profile}")
        
        try:
            profile_choice = input(f"\n{Colors.BOLD}Select profile (1-{len(profiles)}) or Enter for CPU: {Colors.ENDC}").strip()
            
            if profile_choice == "":
                profile = "cpu"
            else:
                profile_num = int(profile_choice)
                if 1 <= profile_num <= len(profiles):
                    profile = profiles[profile_num - 1]
                else:
                    print(f"{Colors.FAIL}Invalid profile choice. Using CPU profile.{Colors.ENDC}")
                    profile = "cpu"
            
            print(f"\n{Colors.OKGREEN}Starting services with profile: {profile}{Colors.ENDC}")
            
            import subprocess
            cmd = ["python3", "start_services_enhanced.py", "--profile", profile]
            
            dry_run = input(f"\n{Colors.BOLD}Dry run? (y/N): {Colors.ENDC}").strip().lower()
            if dry_run in ['y', 'yes']:
                cmd.append("--dry-run")
            
            print(f"\n{Colors.OKCYAN}Executing: {' '.join(cmd)}{Colors.ENDC}")
            subprocess.run(cmd)
            
        except ValueError:
            print(f"{Colors.FAIL}Invalid input.{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}Error starting services: {e}{Colors.ENDC}")
        
        input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")

def main():
    """Main entry point."""
    try:
        configurator = ServiceConfigurator()
        configurator.main_menu()
    except KeyboardInterrupt:
        print(f"\n{Colors.OKCYAN}Goodbye! 👋{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}Fatal error: {e}{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()