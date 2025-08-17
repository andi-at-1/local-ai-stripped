# Service Configuration System

The Enhanced Local AI Package now includes a powerful service configuration system that allows you to easily enable/disable services, configure ports, and customize your AI stack according to your needs.

## Quick Start

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure your services:**
   ```bash
   # Edit services.yml to enable/disable services and configure ports
   nano services.yml
   ```

3. **Start your customized stack:**
   ```bash
   python start_services_enhanced.py --profile cpu
   ```

## Key Features

### 🎛️ **Service Control**
- **Enable/Disable**: Turn any service on or off with a simple `enabled: true/false`
- **Descriptions**: Each service includes a clear description of its purpose
- **Categories**: Services are organized by function (workflow, database, etc.)
- **Dependencies**: Automatic dependency management

### 🔧 **Flexible Configuration**
- **Custom Ports**: Change host ports for any service
- **IP Binding**: Configure which IP addresses services bind to
- **Environment Modes**: Private (localhost) vs Public (external access)
- **Profile Support**: CPU, GPU-NVIDIA, GPU-AMD, and minimal profiles

### 📊 **Enhanced Management**
- **Portainer Integration**: Optional Docker container management UI
- **Dynamic Generation**: Automatic Docker Compose and Caddyfile generation
- **Validation**: Built-in port conflict detection and configuration validation
- **Service Discovery**: Automatic reverse proxy configuration for web services

## Configuration File Structure

### Global Settings
```yaml
global:
  project_name: "localai"          # Docker Compose project name
  default_host_ip: "127.0.0.1"    # Default IP for service binding
```

### Service Configuration
```yaml
services:
  service-name:
    enabled: true                   # Enable/disable this service
    description: "Service purpose"  # What this service does
    category: "workflow"           # Service category
    reverse_proxy: true            # Include in reverse proxy
    ports:                         # Port configuration
      - host_ip: "127.0.0.1"
        host_port: 5678
        container_port: 5678
        protocol: "tcp"
    depends_on:                    # Service dependencies
      - "postgres"
    profiles: ["all"]              # Which profiles include this service
```

### Profile Definitions
```yaml
profiles:
  cpu:
    description: "CPU-only setup for development"
    included_services:
      - "n8n"
      - "open-webui"
      # ... more services
```

## Available Services

### 🤖 **Core AI Services**
- **n8n** (`:5678`) - Workflow automation with AI nodes
- **open-webui** (`:8080`) - ChatGPT-like interface
- **flowise** (`:3001`) - Visual AI agent builder

### 🧠 **LLM Services**
- **ollama-cpu** (`:11434`) - CPU-optimized LLM serving
- **ollama-gpu** (`:11434`) - NVIDIA GPU LLM serving
- **ollama-gpu-amd** (`:11434`) - AMD GPU LLM serving

### 🗄️ **Database & Storage**
- **postgres** (`:5433`) - PostgreSQL via Supabase
- **qdrant** (`:6333`, `:6334`) - Vector database
- **neo4j** (`:7474`, `:7687`) - Knowledge graph database
- **clickhouse** (`:8123`, `:9000`, `:9009`) - Analytics database
- **minio** (`:9010`, `:9011`) - S3-compatible object storage
- **redis** (`:6379`) - Cache and session store

### 🔍 **Search & Discovery**
- **searxng** (`:8081`) - Privacy-focused metasearch engine

### 📊 **Observability**
- **langfuse-web** (`:3000`) - LLM observability platform
- **langfuse-worker** (`:3030`) - Background processing

### 🌐 **Infrastructure**
- **caddy** (`:80`, `:443`) - Reverse proxy with automatic HTTPS
- **portainer** (`:9000`) - Docker container management (optional)

## Usage Examples

### Basic Usage
```bash
# Start with default CPU profile
python start_services_enhanced.py

# Start with GPU support
python start_services_enhanced.py --profile gpu-nvidia

# Start in public mode (external access)
python start_services_enhanced.py --environment public

# See what would be started without actually starting
python start_services_enhanced.py --dry-run

# List all available services
python start_services_enhanced.py --list-services
```

### Advanced Configuration
```bash
# Use custom configuration file
python start_services_enhanced.py --config my-services.yml

# Skip Supabase setup
python start_services_enhanced.py --no-supabase

# Combine options
python start_services_enhanced.py --profile gpu-nvidia --environment public --dry-run
```

## Customization Examples

### Disable Unnecessary Services
```yaml
# In services.yml, disable services you don't need
langfuse-web:
  enabled: false    # Disable LLM observability
  
neo4j:
  enabled: false    # Disable graph database

searxng:
  enabled: false    # Disable search engine
```

### Change Port Mappings
```yaml
# Avoid port conflicts by changing host ports
n8n:
  enabled: true
  ports:
    - host_ip: "127.0.0.1"
      host_port: 8678    # Changed from 5678
      container_port: 5678
      protocol: "tcp"
```

### Enable Container Management
```yaml
# Enable Portainer for Docker management
portainer:
  enabled: true       # Enable the service
  ports:
    - host_ip: "127.0.0.1"
      host_port: 9000
      container_port: 9000
      protocol: "tcp"
```

### Custom Network Configuration
```yaml
# Bind to all interfaces for external access
global:
  default_host_ip: "0.0.0.0"    # Accept connections from any IP

# Or configure per-service
open-webui:
  enabled: true
  ports:
    - host_ip: "0.0.0.0"        # External access
      host_port: 8080
      container_port: 8080
```

## Environment Modes

### Private Mode (Default)
- Services bind to `127.0.0.1` (localhost only)
- All configured ports are exposed
- Suitable for development and local use

### Public Mode
- Only reverse proxy ports (80, 443) are exposed externally
- Individual service ports are closed for security
- Suitable for production deployment

## Migration from Original Setup

The new system is backward compatible. Your existing `.env` configuration will continue to work. To migrate:

1. **Keep your `.env` file** - All environment variables are still used
2. **Customize `services.yml`** - Enable/disable services as needed
3. **Use new script** - Replace `start_services.py` with `start_services_enhanced.py`

## Troubleshooting

### Port Conflicts
```bash
# The system automatically detects port conflicts
Error: Port conflict! 127.0.0.1:9000 is used by both minio and portainer
```
Solution: Change one of the conflicting ports in `services.yml`

### Service Dependencies
Services with dependencies will be validated. If you disable a required service, you'll get a warning.

### Configuration Validation
```bash
# Check configuration without starting services
python start_services_enhanced.py --dry-run
```

## Generated Files

The system creates several generated files:

- **`docker-compose.override.{environment}.generated.yml`** - Dynamic port mappings
- **`Caddyfile.generated`** - Dynamic reverse proxy configuration

These files are automatically created and shouldn't be edited manually.

## Integration with Existing Workflows

The enhanced system maintains compatibility with:
- Existing Docker Compose commands
- Current environment variable system
- Original service configurations
- Established network topology

You can gradually migrate to the new system while keeping your existing setup functional.