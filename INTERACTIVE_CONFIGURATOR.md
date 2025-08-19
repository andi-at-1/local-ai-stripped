# Interactive Service Configurator

The Local AI Package now includes a user-friendly interactive shell for configuring services, ports, and IPs with a simple menu-driven interface.

## 🚀 Quick Start

Launch the interactive configurator:

```bash
python3 configure_services.py
```

## 🎯 Features

### ✅ **Service Management**
- **Check/Uncheck Services**: Easily enable or disable any of the 16 available services
- **Visual Status**: Clear ✓/✗ indicators show which services are enabled
- **Service Categories**: Services are organized by function (workflow, database, LLM, etc.)
- **Service Descriptions**: Each service includes a helpful description

### 🔧 **Port & IP Configuration**
- **Edit Host IPs**: Change which interface services bind to (127.0.0.1, 0.0.0.0, etc.)
- **Edit Host Ports**: Modify port mappings to avoid conflicts
- **Port Conflict Detection**: Automatic validation prevents port conflicts
- **Multiple Ports**: Services with multiple ports are fully configurable

### 💾 **Configuration Management**
- **Auto-Save**: All changes are saved to `services.json`
- **Persistent Settings**: Configuration persists between runs
- **Profile Support**: View and understand different deployment profiles
- **Real-time Updates**: See changes immediately in the interface

## 📋 **Menu Options**

```
Local AI Package Service Configurator
════════════════════════════════════════

Options:
  1. 📋 View all services
  2. ⚙️  Toggle service (enable/disable)
  3. 🔧 Edit service ports/IPs
  4. 📊 Show enabled services summary
  5. 📁 Show available profiles
  6. 💾 Save configuration
  7. 🚀 Start services (using current config)
  0. ❌ Exit
```

## 🎮 **How to Use**

### **1. View All Services**
- Shows all 16 services organized by category
- Displays current status (enabled/disabled)
- Shows current port mappings
- Each service has a number for easy selection

### **2. Toggle Services**
- Enter a service number to enable/disable it
- Immediate feedback on status change
- Perfect for quickly customizing your stack

### **3. Edit Ports & IPs**
- Select a service to modify its network configuration
- Change host IP (127.0.0.1 for localhost, 0.0.0.0 for external access)
- Change host ports to avoid conflicts
- Automatic conflict detection and validation

### **4. View Enabled Summary**
- Quick overview of currently enabled services
- Shows port mappings for enabled services
- Helps verify your configuration before starting

### **5. Show Profiles**
- View available deployment profiles (CPU, GPU-NVIDIA, GPU-AMD, none)
- See which services are included in each profile
- Understand the different deployment scenarios

### **6. Save Configuration**
- Manually save changes to `services.json`
- Configuration is also auto-saved when starting services
- Ensures your settings persist between sessions

### **7. Start Services**
- Launch the enhanced startup script with current configuration
- Choose deployment profile
- Option for dry-run to preview what would be started

## 🎨 **User Interface**

The configurator features a colorful, intuitive interface:
- **Green (✓)**: Enabled services and successful operations
- **Red (✗)**: Disabled services and errors
- **Blue**: Headers and menu options
- **Cyan**: Information and descriptions
- **Yellow**: Warnings and secondary information

## 📊 **Service Categories**

### **🔧 Workflow**
- **n8n**: Workflow automation platform

### **💬 Interface**
- **open-webui**: ChatGPT-like interface for local models

### **🤖 AI-Builder**
- **flowise**: Visual AI agent builder

### **🧠 LLM**
- **ollama-cpu/gpu/gpu-amd**: Local LLM serving platforms

### **🗄️ Database**
- **postgres**: PostgreSQL via Supabase
- **qdrant**: Vector database
- **neo4j**: Knowledge graph database
- **clickhouse**: Analytics database

### **🔍 Search**
- **searxng**: Privacy-focused search engine

### **📊 Observability**
- **langfuse-web/worker**: LLM monitoring and analytics

### **💾 Storage**
- **minio**: S3-compatible object storage

### **⚡ Cache**
- **redis**: In-memory cache

### **🌐 Proxy**
- **caddy**: Automatic HTTPS reverse proxy

### **🛠️ Management**
- **portainer**: Docker container management UI (optional)

## 💡 **Usage Examples**

### **Enable Portainer for Docker Management**
1. Run `python3 configure_services.py`
2. Choose option `2` (Toggle service)
3. Find Portainer (usually service #16)
4. Enter `16` to enable it
5. Choose option `6` to save configuration

### **Change n8n Port to Avoid Conflict**
1. Run `python3 configure_services.py`
2. Choose option `3` (Edit service ports/IPs)
3. Find n8n (usually service #1)
4. Enter `1` to select n8n
5. Choose port `1` to edit
6. Change host port from `5678` to `8678`
7. Configuration is automatically saved

### **Setup External Access**
1. Run `python3 configure_services.py`
2. Choose option `3` (Edit service ports/IPs)
3. Select the service you want external access for
4. Change host IP from `127.0.0.1` to `0.0.0.0`
5. Save and start with public environment

### **Quick Service Customization**
1. View all services with option `1`
2. Toggle unwanted services off with option `2`
3. Check summary with option `4`
4. Start services with option `7`

## 🔄 **Integration with Enhanced Startup**

The configurator seamlessly integrates with the enhanced startup script:
- Changes are automatically saved to `services.json`
- The startup script reads the current configuration
- Profile selection is available in both interfaces
- Dry-run option helps verify configuration

## 🛟 **Tips & Tricks**

- **Start Small**: Begin with just the core services you need
- **Check Conflicts**: The system prevents port conflicts automatically
- **Use Profiles**: Leverage built-in profiles as starting points
- **External Access**: Change host IP to `0.0.0.0` for external access
- **Save Often**: Use option `6` to save configuration frequently
- **Dry Run**: Always test with dry-run before actual deployment

## 🔧 **No Dependencies Required**

The interactive configurator uses only Python standard library:
- No external packages needed
- Works on any system with Python 3.6+
- Colorful interface using ANSI codes
- JSON configuration for maximum compatibility

This interactive approach makes managing your Local AI Package services intuitive and efficient, whether you're a beginner or power user!