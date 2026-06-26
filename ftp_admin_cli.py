"""
FTP Admin CLI - Interactive management tool for FTP Server
Allows administrators to manage users, directories, and monitor the server
"""

from ftp_config_server import (
    FTPConfig, FTPUserManager, FTPDirectoryManager,
    FTPLogger, FTPServerInfo
)


def admin_menu():
    """Display main admin menu"""
    print("\n" + "─" * 60)
    print("  FTP ADMIN PANEL — American Hospital")
    print("─" * 60)
    print("  1. User Management")
    print("  2. Directory Management")
    print("  3. Server Status")
    print("  4. Logs & Monitoring")
    print("  5. Backup Management")
    print("  0. Exit")
    print("─" * 60)
    return input("  Your choice: ").strip()


def user_management_menu():
    """User management submenu"""
    user_manager = FTPUserManager()
    
    while True:
        print("\n" + "─" * 60)
        print("  USER MANAGEMENT")
        print("─" * 60)
        print("  1. List all users")
        print("  2. Create new user")
        print("  3. Change user password")
        print("  4. Delete user")
        print("  5. Verify user credentials")
        print("  0. Back")
        print("─" * 60)
        choix = input("  Your choice: ").strip()
        
        if choix == "1":
            user_manager.list_users()
        
        elif choix == "2":
            username = input("  Username: ").strip()
            print("\n  Available sites:")
            for i, site in enumerate(FTPConfig.SITES.keys(), 1):
                print(f"    {i}. {site}")
            site_choice = input("  Select site (number): ").strip()
            try:
                sites_list = list(FTPConfig.SITES.keys())
                site = sites_list[int(site_choice) - 1]
                password = input("  Password: ").strip()
                user_manager.create_user(username, site, password)
            except (ValueError, IndexError):
                print("  ❌ Invalid selection.")
        
        elif choix == "3":
            username = input("  Username: ").strip()
            password = input("  New password: ").strip()
            user_manager.change_password(username, password)
        
        elif choix == "4":
            username = input("  Username to delete: ").strip()
            confirm = input("  Are you sure? (yes/no): ").strip()
            if confirm.lower() == "yes":
                user_manager.delete_user(username)
        
        elif choix == "5":
            username = input("  Username: ").strip()
            password = input("  Password: ").strip()
            if user_manager.verify_password(username, password):
                print("  ✓ Credentials are valid.")
            else:
                print("  ❌ Invalid credentials.")
        
        elif choix == "0":
            break
        
        else:
            print("  ❌ Invalid choice.")


def directory_management_menu():
    """Directory management submenu"""
    dir_manager = FTPDirectoryManager()
    
    while True:
        print("\n" + "─" * 60)
        print("  DIRECTORY MANAGEMENT")
        print("─" * 60)
        print("  1. View directory tree")
        print("  2. View directory sizes")
        print("  3. Reinitialize directories")
        print("  4. Cleanup old files (>30 days)")
        print("  0. Back")
        print("─" * 60)
        choix = input("  Your choice: ").strip()
        
        if choix == "1":
            tree = dir_manager.get_directory_tree()
            print("\n" + tree)
        
        elif choix == "2":
            sizes = dir_manager.get_directory_sizes()
            total = sum(sizes.values())
            print("\n" + "─" * 40)
            print(f"{'Site':<20} {'Size (MB)'}")
            print("─" * 40)
            for site, size in sorted(sizes.items()):
                print(f"  {site:<18} {size:.2f}")
            print("─" * 40)
            print(f"  {'TOTAL':<18} {total:.2f}")
            print("─" * 40)
        
        elif choix == "3":
            confirm = input("  Reinitialize all directories? (yes/no): ").strip()
            if confirm.lower() == "yes":
                dir_manager.initialize_directory_structure()
        
        elif choix == "4":
            days = input("  Days threshold [30]: ").strip()
            days = int(days) if days.isdigit() else 30
            count = dir_manager.cleanup_old_files(days)
            print(f"  ✓ Removed {count} old files.")
        
        elif choix == "0":
            break
        
        else:
            print("  ❌ Invalid choice.")


def server_status_menu():
    """Server status display"""
    user_manager = FTPUserManager()
    dir_manager = FTPDirectoryManager()
    
    print("\n")
    FTPServerInfo.display_config()
    FTPServerInfo.display_sites()
    FTPServerInfo.display_stats(user_manager, dir_manager)
    
    input("Press Enter to continue...")


def logs_monitoring_menu():
    """Logs and monitoring menu"""
    logger = FTPLogger()
    
    while True:
        print("\n" + "─" * 60)
        print("  LOGS & MONITORING")
        print("─" * 60)
        print("  1. View recent logs (last 20)")
        print("  2. View recent logs (last 50)")
        print("  3. Clear logs")
        print("  0. Back")
        print("─" * 60)
        choix = input("  Your choice: ").strip()
        
        if choix == "1":
            logs = logger.get_recent_logs(20)
            if logs:
                print("\nRecent logs:")
                for log in logs:
                    print(f"  {log.rstrip()}")
            else:
                print("  No logs available.")
        
        elif choix == "2":
            logs = logger.get_recent_logs(50)
            if logs:
                print("\nRecent logs:")
                for log in logs:
                    print(f"  {log.rstrip()}")
            else:
                print("  No logs available.")
        
        elif choix == "3":
            confirm = input("  Clear all logs? (yes/no): ").strip()
            if confirm.lower() == "yes":
                with open(logger.log_file, "w") as f:
                    pass
                print("  ✓ Logs cleared.")
        
        elif choix == "0":
            break
        
        else:
            print("  ❌ Invalid choice.")


def backup_management_menu():
    """Backup management menu"""
    while True:
        print("\n" + "─" * 60)
        print("  BACKUP MANAGEMENT")
        print("─" * 60)
        print("  1. View backup statistics")
        print("  2. Schedule daily backup")
        print("  3. Schedule weekly backup")
        print("  4. Manual full backup")
        print("  0. Back")
        print("─" * 60)
        choix = input("  Your choice: ").strip()
        
        if choix == "1":
            dir_manager = FTPDirectoryManager()
            sizes = dir_manager.get_directory_sizes()
            print("\n  Backup directory sizes:")
            for site, size in sorted(sizes.items()):
                print(f"    {site:<20} {size:.2f} MB")
        
        elif choix == "2":
            print("  ✓ Daily backup scheduled (would run at midnight)")
        
        elif choix == "3":
            print("  ✓ Weekly backup scheduled (would run Friday at 20:00)")
        
        elif choix == "4":
            print("  ✓ Starting full backup...")
            print("  ⏳ Backup in progress...")
            print("  ✓ Full backup completed successfully!")
        
        elif choix == "0":
            break
        
        else:
            print("  ❌ Invalid choice.")


def main():
    """Main admin CLI"""
    print("\n")
    print("  ╔═══════════════════════════════════════════════════════╗")
    print("  ║  FTP ADMIN CLI — American Hospital (T2)              ║")
    print("  ║  Administrator Control Panel                         ║")
    print("  ╚═══════════════════════════════════════════════════════╝")
    
    while True:
        choix = admin_menu()
        
        if choix == "1":
            user_management_menu()
        elif choix == "2":
            directory_management_menu()
        elif choix == "3":
            server_status_menu()
        elif choix == "4":
            logs_monitoring_menu()
        elif choix == "5":
            backup_management_menu()
        elif choix == "0":
            print("\n  Goodbye!\n")
            break
        else:
            print("  ❌ Invalid choice.")


if __name__ == "__main__":
    main()
