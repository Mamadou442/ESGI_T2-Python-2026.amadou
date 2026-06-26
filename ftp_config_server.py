"""
FTP Configuration Server for American Hospital - T2 Project
Handles FTP server setup, user management, and directory initialization
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple


# ────────────────────────────────────────────────
# FTP Server Configuration
# ────────────────────────────────────────────────

class FTPConfig:
    """Centralized FTP server configuration management"""
    
    # Server settings
    HOST = "127.0.0.1"
    PORT = 21
    TIMEOUT = 30
    MAX_CONNECTIONS = 10
    PASSIVE_PORTS = (30000, 40000)
    
    # Root directory
    FTP_ROOT = "FTP_ROOT"
    CONFIG_FILE = "ftp_config.json"
    LOG_FILE = "ftp_access.log"
    
    # Sites definition
    SITES = {
        "paris": {
            "name": "Paris Hospital",
            "user": "paris_admin",
            "region": "Île-de-France",
            "quota_gb": 100,
        },
        "grenoble": {
            "name": "Grenoble Hospital",
            "user": "grenoble_admin",
            "region": "Auvergne-Rhône-Alpes",
            "quota_gb": 100,
        },
        "marseille": {
            "name": "Marseille Hospital",
            "user": "marseille_admin",
            "region": "Provence-Alpes-Côte d'Azur",
            "quota_gb": 100,
        },
        "rennes": {
            "name": "Rennes Hospital",
            "user": "rennes_admin",
            "region": "Bretagne",
            "quota_gb": 100,
        },
    }
    
    # Directory structure
    DIR_STRUCTURE = {
        "data": {
            "description": "Active data files",
            "permissions": "rwx------",
        },
        "backups/daily": {
            "description": "Daily backup snapshots",
            "permissions": "rwx------",
        },
        "backups/weekly": {
            "description": "Weekly backup archives",
            "permissions": "rwx------",
        },
        "archives": {
            "description": "Version archives",
            "permissions": "rwx------",
        },
        "logs": {
            "description": "Access and transfer logs",
            "permissions": "rw-------",
        },
    }


# ────────────────────────────────────────────────
# User Management
# ────────────────────────────────────────────────

class FTPUserManager:
    """Manages FTP users and credentials"""
    
    def __init__(self, config_file: str = FTPConfig.CONFIG_FILE):
        self.config_file = config_file
        self.users = self._load_users()
    
    def _load_users(self) -> Dict:
        """Load users from config file or create defaults"""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                return json.load(f).get("users", {})
        return self._create_default_users()
    
    def _create_default_users(self) -> Dict:
        """Create default user configuration"""
        users = {}
        for site_key, site_config in FTPConfig.SITES.items():
            users[site_config["user"]] = {
                "site": site_key,
                "password_hash": self._hash_password("root"),  # Default: "root"
                "home_dir": f"{FTPConfig.FTP_ROOT}/{site_key}",
                "permissions": ["read", "write", "delete"],
                "created": datetime.now().isoformat(),
                "status": "active",
            }
        return users
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, username: str, password: str) -> bool:
        """Verify user credentials"""
        if username not in self.users:
            return False
        user = self.users[username]
        return user["password_hash"] == self._hash_password(password)
    
    def create_user(self, username: str, site: str, password: str, permissions: List[str] = None) -> bool:
        """Create a new FTP user"""
        if username in self.users:
            print(f"❌ User '{username}' already exists.")
            return False
        
        if site not in FTPConfig.SITES:
            print(f"❌ Site '{site}' not found.")
            return False
        
        permissions = permissions or ["read", "write"]
        
        self.users[username] = {
            "site": site,
            "password_hash": self._hash_password(password),
            "home_dir": f"{FTPConfig.FTP_ROOT}/{site}",
            "permissions": permissions,
            "created": datetime.now().isoformat(),
            "status": "active",
        }
        
        self.save_users()
        print(f"✓ User '{username}' created successfully.")
        return True
    
    def change_password(self, username: str, new_password: str) -> bool:
        """Change user password"""
        if username not in self.users:
            print(f"❌ User '{username}' not found.")
            return False
        
        self.users[username]["password_hash"] = self._hash_password(new_password)
        self.save_users()
        print(f"✓ Password for '{username}' changed successfully.")
        return True
    
    def delete_user(self, username: str) -> bool:
        """Delete a user"""
        if username not in self.users:
            print(f"❌ User '{username}' not found.")
            return False
        
        del self.users[username]
        self.save_users()
        print(f"✓ User '{username}' deleted successfully.")
        return True
    
    def list_users(self) -> None:
        """List all users"""
        print(f"\n{'Username':<20} {'Site':<15} {'Status':<10} {'Permissions'}")
        print("─" * 70)
        for username, info in self.users.items():
            perms = ", ".join(info["permissions"])
            print(f"{username:<20} {info['site']:<15} {info['status']:<10} {perms}")
    
    def save_users(self) -> None:
        """Save users to config file"""
        config = {"users": self.users}
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)


# ────────────────────────────────────────────────
# Directory Management
# ────────────────────────────────────────────────

class FTPDirectoryManager:
    """Manages FTP directory structure and initialization"""
    
    def __init__(self, root_path: str = FTPConfig.FTP_ROOT):
        self.root_path = root_path
    
    def initialize_directory_structure(self) -> bool:
        """Initialize the complete FTP directory structure"""
        print(f"\n📁 Initializing FTP directory structure at '{self.root_path}'...\n")
        
        try:
            for site_key, site_config in FTPConfig.SITES.items():
                for dir_name, dir_info in FTPConfig.DIR_STRUCTURE.items():
                    dir_path = os.path.join(self.root_path, site_key, dir_name)
                    os.makedirs(dir_path, exist_ok=True)
                    print(f"  ✓ {dir_path:<50} ({dir_info['description']})")
            
            print("\n✓ Directory structure initialized successfully.\n")
            return True
        except Exception as e:
            print(f"❌ Error initializing directories: {e}\n")
            return False
    
    def get_directory_tree(self) -> str:
        """Generate directory tree representation"""
        tree = []
        for site_key in FTPConfig.SITES.keys():
            tree.append(f"\n{site_key}/")
            site_path = os.path.join(self.root_path, site_key)
            if os.path.exists(site_path):
                for root, dirs, files in os.walk(site_path):
                    level = root.replace(site_path, "").count(os.sep)
                    indent = "  " * (level + 1)
                    tree.append(f"{indent}{os.path.basename(root)}/")
                    subindent = "  " * (level + 2)
                    for file in files:
                        tree.append(f"{subindent}{file}")
        return "\n".join(tree)
    
    def get_directory_sizes(self) -> Dict[str, float]:
        """Calculate size of each site directory in MB"""
        sizes = {}
        for site_key in FTPConfig.SITES.keys():
            site_path = os.path.join(self.root_path, site_key)
            if os.path.exists(site_path):
                total_size = 0
                for root, dirs, files in os.walk(site_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                sizes[site_key] = total_size / (1024 * 1024)  # Convert to MB
        return sizes
    
    def cleanup_old_files(self, days: int = 30) -> int:
        """Remove files older than specified days"""
        from time import time
        current_time = time()
        threshold = current_time - (days * 86400)
        removed_count = 0
        
        for site_key in FTPConfig.SITES.keys():
            site_path = os.path.join(self.root_path, site_key)
            if os.path.exists(site_path):
                for root, dirs, files in os.walk(site_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if os.path.getmtime(file_path) < threshold:
                            os.remove(file_path)
                            removed_count += 1
        
        return removed_count


# ────────────────────────────────────────────────
# Logging and Monitoring
# ────────────────────────────────────────────────

class FTPLogger:
    """Handles FTP access logging"""
    
    def __init__(self, log_file: str = FTPConfig.LOG_FILE):
        self.log_file = log_file
    
    def log_access(self, username: str, action: str, file_path: str, status: str = "success") -> None:
        """Log FTP access"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {username:<15} {action:<10} {file_path:<40} {status}"
        
        with open(self.log_file, "a") as f:
            f.write(log_entry + "\n")
    
    def get_recent_logs(self, limit: int = 10) -> List[str]:
        """Get recent log entries"""
        if not os.path.exists(self.log_file):
            return []
        
        with open(self.log_file, "r") as f:
            lines = f.readlines()
        
        return lines[-limit:]


# ────────────────────────────────────────────────
# Server Status and Info
# ────────────────────────────────────────────────

class FTPServerInfo:
    """Provides server status and information"""
    
    @staticmethod
    def display_config() -> None:
        """Display server configuration"""
        print("\n" + "─" * 60)
        print("  FTP SERVER CONFIGURATION")
        print("─" * 60)
        print(f"  Host:              {FTPConfig.HOST}")
        print(f"  Port:              {FTPConfig.PORT}")
        print(f"  Root Directory:    {FTPConfig.FTP_ROOT}")
        print(f"  Max Connections:   {FTPConfig.MAX_CONNECTIONS}")
        print(f"  Timeout:           {FTPConfig.TIMEOUT}s")
        print(f"  Passive Ports:     {FTPConfig.PASSIVE_PORTS[0]}-{FTPConfig.PASSIVE_PORTS[1]}")
        print("─" * 60 + "\n")
    
    @staticmethod
    def display_sites() -> None:
        """Display configured sites"""
        print("\n" + "─" * 80)
        print("  CONFIGURED SITES")
        print("─" * 80)
        print(f"{'Site':<15} {'Name':<30} {'Region':<30} {'Quota'}")
        print("─" * 80)
        for site_key, site_config in FTPConfig.SITES.items():
            print(f"{site_key:<15} {site_config['name']:<30} {site_config['region']:<30} {site_config['quota_gb']}GB")
        print("─" * 80 + "\n")
    
    @staticmethod
    def display_stats(user_manager: FTPUserManager, dir_manager: FTPDirectoryManager) -> None:
        """Display server statistics"""
        sizes = dir_manager.get_directory_sizes()
        total_size = sum(sizes.values())
        
        print("\n" + "─" * 60)
        print("  SERVER STATISTICS")
        print("─" * 60)
        print(f"  Total Users:       {len(user_manager.users)}")
        print(f"  Total Sites:       {len(FTPConfig.SITES)}")
        print(f"  Total Data Size:   {total_size:.2f} MB")
        print("─" * 60)
        print(f"{'Site':<20} {'Size (MB)'}")
        print("─" * 60)
        for site, size in sizes.items():
            print(f"  {site:<18} {size:.2f}")
        print("─" * 60 + "\n")


# ────────────────────────────────────────────────
# Initialization Script
# ────────────────────────────────────────────────

def initialize_ftp_server() -> None:
    """Complete FTP server initialization"""
    print("\n")
    print("  ╔═══════════════════════════════════════════════════════╗")
    print("  ║  FTP Configuration Server - American Hospital (T2)   ║")
    print("  ║  Initial Setup                                      ║")
    print("  ╚═══════════════════════════════════════════════════════╝")
    
    # Display configuration
    FTPServerInfo.display_config()
    FTPServerInfo.display_sites()
    
    # Initialize directories
    dir_manager = FTPDirectoryManager()
    dir_manager.initialize_directory_structure()
    
    # Create default users
    user_manager = FTPUserManager()
    print("\n📋 Default users created:")
    user_manager.list_users()
    
    # Display stats
    FTPServerInfo.display_stats(user_manager, dir_manager)
    
    print("✓ FTP Server initialization completed successfully!\n")


if __name__ == "__main__":
    initialize_ftp_server()
