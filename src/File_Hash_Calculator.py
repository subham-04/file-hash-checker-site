import os
import hashlib
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import json
from datetime import datetime, timedelta
from pathlib import Path
import requests
import csv

# Globals
pause_flag = threading.Event()
stop_flag = threading.Event()
is_scanning = False
is_paused = False
dark_mode = True

# VirusTotal API globals
vt_results = {}  # Store hash -> VT results mapping
vt_api_key = ""  # VirusTotal API key
selected_hashes = []  # Store selected hashes for VT checking

# File selection globals
file_selection_state = {}  # Store checkbox states for files
select_all_state = False  # Track select all state

# === VIRUSTOTAL QUOTA TRACKING ===
DAILY_QUOTA_LIMIT = 500
MONTHLY_QUOTA_LIMIT = 15000
QUOTA_FILE = "vt_quota_tracking.json"
API_KEY_FILE = "vt_api_key.dat"  # Separate file for API key

# Registry settings for secure quota tracking (Windows)
import winreg
REGISTRY_KEY = r"SOFTWARE\FileHashCalculator"
QUOTA_REG_PATH = "VTQuotaData"

def get_secure_quota_data():
    """Get quota data from Windows registry (more secure than JSON)"""
    default_data = {
        "daily": {},
        "monthly": {},
        "current_month": datetime.now().strftime("%Y-%m"),
        "current_day": datetime.now().strftime("%Y-%m-%d")
    }
    
    try:
        # Try to access registry
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY, 0, winreg.KEY_READ) as key:
            quota_json, _ = winreg.QueryValueEx(key, QUOTA_REG_PATH)
            return json.loads(quota_json)
    except (FileNotFoundError, winreg.error, json.JSONDecodeError):
        # Registry key doesn't exist or is corrupted, return default
        return default_data

def save_secure_quota_data(data):
    """Save quota data to Windows registry (more secure than JSON)"""
    try:
        # Create registry key if it doesn't exist
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY) as key:
            quota_json = json.dumps(data)
            winreg.SetValueEx(key, QUOTA_REG_PATH, 0, winreg.REG_SZ, quota_json)
    except Exception as e:
        print(f"Error saving quota data to registry: {e}")
        # Fallback to JSON file if registry fails
        save_quota_data_fallback(data)

def save_quota_data_fallback(data):
    """Fallback method to save quota data to file"""
    try:
        quota_file = get_quota_file_path()
        with open(quota_file, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving quota data to file: {e}")

def get_api_key_file_path():
    """Get the path for API key storage file"""
    return Path.cwd() / API_KEY_FILE

def save_api_key(api_key):
    """Save API key to encrypted file"""
    try:
        # Simple base64 encoding (not truly secure, but better than plain text)
        import base64
        encoded_key = base64.b64encode(api_key.encode()).decode()
        
        api_file = get_api_key_file_path()
        with open(api_file, 'w') as f:
            f.write(encoded_key)
    except Exception as e:
        print(f"Error saving API key: {e}")

def load_api_key():
    """Load API key from encrypted file"""
    try:
        api_file = get_api_key_file_path()
        if api_file.exists():
            import base64
            with open(api_file, 'r') as f:
                encoded_key = f.read().strip()
                api_key = base64.b64decode(encoded_key).decode()
                return api_key
        return ""
    except Exception as e:
        print(f"Error loading API key: {e}")
        return ""

def get_quota_file_path():
    """Get the path for quota tracking file"""
    return Path.cwd() / QUOTA_FILE

def load_quota_data():
    """Load quota usage data from secure storage (registry preferred, file fallback)"""
    try:
        # Try secure registry storage first
        return get_secure_quota_data()
    except Exception as e:
        print(f"Registry access failed, using file fallback: {e}")
        # Fallback to JSON file
        quota_file = get_quota_file_path()
        default_data = {
            "daily": {},
            "monthly": {},
            "current_month": datetime.now().strftime("%Y-%m"),
            "current_day": datetime.now().strftime("%Y-%m-%d")
        }
        
        try:
            if quota_file.exists():
                with open(quota_file, 'r') as f:
                    data = json.load(f)
                    # Ensure all required keys exist
                    for key in default_data:
                        if key not in data:
                            data[key] = default_data[key]
                    return data
            else:
                return default_data
        except Exception as e:
            print(f"Error loading quota data from file: {e}")
            return default_data

def save_quota_data(data):
    """Save quota usage data to secure storage"""
    try:
        # Try secure registry storage first
        save_secure_quota_data(data)
    except Exception as e:
        print(f"Registry save failed, using file fallback: {e}")
        # Fallback to JSON file
        save_quota_data_fallback(data)

def update_quota_usage(requests_count=1):
    """Update quota usage and return current status"""
    quota_data = load_quota_data()
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_month = datetime.now().strftime("%Y-%m")
    
    # Initialize current day/month if not exists
    if current_date not in quota_data["daily"]:
        quota_data["daily"][current_date] = 0
    if current_month not in quota_data["monthly"]:
        quota_data["monthly"][current_month] = 0
    
    # Clean old daily data (keep only last 30 days)
    cutoff_date = datetime.now() - timedelta(days=30)
    quota_data["daily"] = {
        date: count for date, count in quota_data["daily"].items()
        if datetime.strptime(date, "%Y-%m-%d") > cutoff_date
    }
    
    # Clean old monthly data (keep only last 12 months)
    cutoff_month = datetime.now() - timedelta(days=365)
    quota_data["monthly"] = {
        month: count for month, count in quota_data["monthly"].items()
        if datetime.strptime(month, "%Y-%m") > cutoff_month
    }
    
    # Update usage
    quota_data["daily"][current_date] += requests_count
    quota_data["monthly"][current_month] += requests_count
    quota_data["current_day"] = current_date
    quota_data["current_month"] = current_month
    
    # Save updated data
    save_quota_data(quota_data)
    
    return quota_data

def get_quota_status():
    """Get current quota status with integrity validation"""
    quota_data = load_quota_data()
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_month = datetime.now().strftime("%Y-%m")
    
    # Validate quota data integrity
    if validate_quota_integrity(quota_data):
        daily_used = quota_data["daily"].get(current_date, 0)
        monthly_used = quota_data["monthly"].get(current_month, 0)
    else:
        # If validation fails, reset quota data for security
        print("Quota data validation failed - resetting to prevent manipulation")
        quota_data = {
            "daily": {current_date: 0},
            "monthly": {current_month: 0},
            "current_month": current_month,
            "current_day": current_date
        }
        save_quota_data(quota_data)
        daily_used = 0
        monthly_used = 0
    
    daily_remaining = max(0, DAILY_QUOTA_LIMIT - daily_used)
    monthly_remaining = max(0, MONTHLY_QUOTA_LIMIT - monthly_used)
    
    return {
        "daily_used": daily_used,
        "daily_remaining": daily_remaining,
        "monthly_used": monthly_used,
        "monthly_remaining": monthly_remaining,
        "can_make_request": daily_remaining > 0 and monthly_remaining > 0
    }

def validate_quota_integrity(quota_data):
    """Validate quota data for signs of manipulation"""
    try:
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_month = datetime.now().strftime("%Y-%m")
        
        # Check if data structure is valid
        required_keys = ["daily", "monthly", "current_month", "current_day"]
        if not all(key in quota_data for key in required_keys):
            return False
        
        # Check for negative values (impossible)
        for date, count in quota_data["daily"].items():
            if count < 0 or count > DAILY_QUOTA_LIMIT * 2:  # Allow some buffer for edge cases
                return False
        
        for month, count in quota_data["monthly"].items():
            if count < 0 or count > MONTHLY_QUOTA_LIMIT * 2:  # Allow some buffer for edge cases
                return False
        
        # Check if current month total matches sum of days
        if current_month in quota_data["monthly"]:
            days_in_month = [date for date in quota_data["daily"].keys() if date.startswith(current_month)]
            month_sum = sum(quota_data["daily"].get(date, 0) for date in days_in_month)
            if abs(quota_data["monthly"][current_month] - month_sum) > 10:  # Allow small discrepancy
                return False
        
        return True
    except Exception as e:
        print(f"Quota validation error: {e}")
        return False

def check_quota_before_request(requests_needed=1):
    """Check if quota allows for the requested number of API calls"""
    status = get_quota_status()
    
    if requests_needed > status["daily_remaining"]:
        return False, f"Daily quota exceeded! Used: {status['daily_used']}/{DAILY_QUOTA_LIMIT}. Try again tomorrow."
    
    if requests_needed > status["monthly_remaining"]:
        return False, f"Monthly quota exceeded! Used: {status['monthly_used']}/{MONTHLY_QUOTA_LIMIT}. Resets next month."
    
    return True, "OK"

def update_quota_display():
    """Update the quota display labels"""
    try:
        status = get_quota_status()
        
        # Update daily quota display
        daily_color = ACCENT_GREEN if status["daily_remaining"] > 50 else (ACCENT_RED if status["daily_remaining"] == 0 else "#FFA500")  # Orange for low
        daily_text = f"Daily: {status['daily_used']}/{DAILY_QUOTA_LIMIT} ({status['daily_remaining']} left)"
        vt_daily_quota_label.config(text=daily_text, fg=daily_color)
        
        # Update monthly quota display  
        monthly_color = ACCENT_GREEN if status["monthly_remaining"] > 1000 else (ACCENT_RED if status["monthly_remaining"] == 0 else "#FFA500")  # Orange for low
        monthly_text = f"Monthly: {status['monthly_used']}/{MONTHLY_QUOTA_LIMIT} ({status['monthly_remaining']} left)"
        vt_monthly_quota_label.config(text=monthly_text, fg=monthly_color)
        
    except Exception as e:
        vt_daily_quota_label.config(text="Daily: Error loading", fg=ACCENT_RED)
        vt_monthly_quota_label.config(text="Monthly: Error loading", fg=ACCENT_RED)
        print(f"Error updating quota display: {e}")

def export_results_to_csv():
    """Export Results tab data to CSV file"""
    try:
        # Get all items from the results tree
        items = tree.get_children()
        if not items:
            messagebox.showwarning("No Data", "No results to export. Please scan files first.")
            return
        
        # Ask user for save location
        suggested_name = f"hash_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file_path = filedialog.asksaveasfilename(
            title="Export Results to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        # If user didn't specify extension, add .csv
        if file_path and not file_path.endswith('.csv'):
            file_path += '.csv'
        
        if not file_path:
            return
        
        # Write CSV file
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            headers = ["Selected", "Type", "Filename", "Path", "Size", "Extension", "MD5", "SHA1", "SHA256"]
            writer.writerow(headers)
            
            # Write data rows
            exported_count = 0
            for item in items:
                values = tree.item(item)['values']
                if values:  # Ensure there are values to write
                    writer.writerow(values)
                    exported_count += 1
        
        messagebox.showinfo("Export Complete", 
                          f"Successfully exported {exported_count} results to:\n{file_path}")
        
    except Exception as e:
        messagebox.showerror("Export Error", f"Failed to export results:\n{str(e)}")

def export_vt_results_to_csv():
    """Export VirusTotal tab data to CSV file"""
    try:
        # Get all items from the VT tree
        items = vt_tree.get_children()
        if not items:
            messagebox.showwarning("No Data", "No VirusTotal results to export. Please check files with VirusTotal first.")
            return
        
        # Ask user for save location
        suggested_name = f"virustotal_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file_path = filedialog.asksaveasfilename(
            title="Export VirusTotal Results to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        # If user didn't specify extension, add .csv
        if file_path and not file_path.endswith('.csv'):
            file_path += '.csv'
        
        if not file_path:
            return
        
        # Write CSV file
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            headers = ["Status", "Hash Type", "Hash", "Malicious", "Suspicious", "Clean", "Last Scan", "Filename"]
            writer.writerow(headers)
            
            # Write data rows
            exported_count = 0
            for item in items:
                values = vt_tree.item(item)['values']
                if values:  # Ensure there are values to write
                    writer.writerow(values)
                    exported_count += 1
        
        messagebox.showinfo("Export Complete", 
                          f"Successfully exported {exported_count} VirusTotal results to:\n{file_path}")
        
    except Exception as e:
        messagebox.showerror("Export Error", f"Failed to export VirusTotal results:\n{str(e)}")

# === HASHING ===
def calculate_hashes(file_path):
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                md5.update(chunk)
                sha1.update(chunk)
                sha256.update(chunk)
        return md5.hexdigest(), sha1.hexdigest(), sha256.hexdigest()
    except Exception as e:
        return f"Error: {e}", "", ""

def scan_folder(folder_path, update_callback, done_callback, tree_widget, progress_variable):
    all_files = []
    folder_structure = {}
    
    # Build folder structure and collect all files using os.walk (depth-first traversal)
    for root, dirs, files in os.walk(folder_path):
        # Store folder structure for tree view
        rel_root = os.path.relpath(root, folder_path) if root != folder_path else ""
        
        # Add files to the list for processing
        for file in files:
            file_path = os.path.join(root, file)
            all_files.append(file_path)
        
        # Build proper nested structure for tree view
        folder_structure[rel_root] = {
            'dirs': dirs.copy(),  # Direct subdirectories at this level
            'files': files.copy(),  # Files at this level
            'full_path': root
        }

    total_files = len(all_files)
    if total_files == 0:
        update_callback("⚠️ No files found in the selected folder.")
        messagebox.showinfo("Empty Folder", "The selected folder contains no files to scan.")
        done_callback()
        return

    # Update folder tree structure after scanning
    def update_folder_tree():
        build_folder_tree(folder_path, folder_structure)

    for idx, file_path in enumerate(all_files, 1):
        if stop_flag.is_set():
            update_callback("⛔ Scan stopped.")
            break
        while pause_flag.is_set():
            update_callback("⏸ Paused...")
            threading.Event().wait(0.2)

        rel_path = os.path.relpath(file_path, folder_path)
        file_ext = os.path.splitext(file_path)[1].lower() or "No Extension"
        file_size = get_file_size(file_path)
        update_callback(f"Processing: {rel_path} ({idx}/{total_files})")
        md5, sha1, sha256 = calculate_hashes(file_path)

        # Update UI in main thread with smoother progress
        def update_ui():
            # Initialize file selection state
            file_selection_state[file_path] = False
            tree_widget.insert('', tk.END, values=("☐", "Folder", rel_path, file_path, file_size, file_ext, md5, sha1, sha256))
            progress_percentage = (idx / total_files) * 100
            progress_variable.set(progress_percentage)
            
        tree_widget.after(0, update_ui)

    # Update folder tree after all files are processed
    tree_widget.after(0, update_folder_tree)
    done_callback()

def get_file_size(file_path):
    try:
        size = os.path.getsize(file_path)
        # Convert to human readable format
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    except:
        return "Unknown"

def build_folder_tree(root_folder, folder_structure):
    # This function is no longer needed since we removed the folder structure tab
    # Keeping it as a placeholder to avoid errors during folder scanning
    pass

# === BUTTON HANDLERS ===
def browse_folder():
    folder = filedialog.askdirectory(title="Select Folder to Scan")
    if folder:
        selected_folder.set(folder)
        folder_name = os.path.basename(folder)
        status_var.set(f"[FOLDER] Selected: {folder_name} - Ready to process")
        selection_status_label.config(text=f"FOLDER: {folder_name}", fg=ACCENT_GREEN)
        # Enable Start Processing button
        start_processing_btn.config(state="normal")
        # Clear any file selection and disable other input methods
        if hasattr(start_processing, 'pending_files') and start_processing.pending_files:
            start_processing.pending_files = []
            drop_label.config(text="Drag & Drop Files Here", fg=TEXT_MUTED)
        # Disable other input methods
        browse_files_btn.config(state="disabled")
        drop_label.config(text="Folder selected - Other input methods disabled", fg=TEXT_MUTED)

def start_processing(mode=None):
    """Start processing selected folder or files with proper error handling"""
    global is_scanning, is_paused
    
    # Get current selections
    folder_path = selected_folder.get()
    files_to_process = getattr(start_processing, 'pending_files', [])
    
    # Enhanced error handling and validation
    if mode == "folder":
        if not folder_path:
            messagebox.showwarning("No Folder Selected", "Please select a folder first using the 'Choose Folder' button.")
            return
        if files_to_process:
            # Clear conflicting file selection
            start_processing.pending_files = []
            selection_status_label.config(text="")
            drop_label.config(text="Drag & Drop Files Here\nOr use Browse Files button above", fg=TEXT_MUTED)
            start_processing_btn.config(state="disabled")
            messagebox.showinfo("Selection Cleared", "File selection cleared. Processing folder instead.")
        
        # Process folder
        processing_type = "folder"
        processing_count = "all files in folder"
        
    elif mode == "files":
        if not files_to_process:
            messagebox.showwarning("No Files Selected", "Please select files first using the 'Browse Files' button or drag & drop.")
            return
        if folder_path:
            # Clear conflicting folder selection
            selected_folder.set("")
            start_processing_btn.config(state="disabled")
            messagebox.showinfo("Selection Cleared", "Folder selection cleared. Processing files instead.")
        
        # Process files
        processing_type = "files"
        processing_count = f"{len(files_to_process)} files"
        
    else:
        # Auto-detect mode (legacy support)
        if folder_path and not files_to_process:
            processing_type = "folder"
            processing_count = "all files in folder"
        elif files_to_process and not folder_path:
            processing_type = "files"
            processing_count = f"{len(files_to_process)} files"
        elif folder_path and files_to_process:
            # Conflict - ask user to choose
            choice = messagebox.askyesnocancel(
                title="Multiple Selections Detected",
                message="Both folder and files are selected.\n\nYes = Process Folder\nNo = Process Files\nCancel = Cancel operation"
            )
            if choice is True:
                # Process folder, clear files
                start_processing.pending_files = []
                selection_status_label.config(text="")
                drop_label.config(text="Drag & Drop Files Here\nOr use Browse Files button above", fg=TEXT_MUTED)
                start_processing_btn.config(state="disabled")
                processing_type = "folder"
                processing_count = "all files in folder"
            elif choice is False:
                # Process files, clear folder
                selected_folder.set("")
                start_processing_btn.config(state="disabled")
                processing_type = "files"
                processing_count = f"{len(files_to_process)} files"
            else:
                # Cancel
                return
        else:
            messagebox.showwarning("Nothing to Process", "Please select a folder or files first.")
            return
    
    # Confirm processing
    confirm = messagebox.askyesno(
        title="Confirm Processing",
        message=f"Ready to process {processing_count}.\n\nThis will:\n• Switch to Results tab\n• Start hash calculation\n• Clear any existing results\n\nContinue?"
    )
    
    if not confirm:
        return
    
    # Disable Start Processing button during processing
    start_processing_btn.config(state="disabled")
    
    # Switch to Results tab automatically
    tabs.select(results_tab)
    
    # Reset table and start processing
    reset_table()
    is_scanning = True
    is_paused = False
    update_control_buttons()
    
    try:
        if processing_type == "folder":
            status_var.set(f"🔍 Starting folder scan: {os.path.basename(folder_path)}")
            start_scan(folder_path)
        elif processing_type == "files":
            status_var.set(f"🔍 Starting file processing: {len(files_to_process)} files")
            process_dropped_files(files_to_process)
            # Clear pending files after processing starts
            start_processing.pending_files = []
            selection_status_label.config(text="")
            
    except Exception as e:
        # Error handling
        messagebox.showerror("Processing Error", f"Failed to start processing:\n{str(e)}")
        is_scanning = False
        is_paused = False
        update_control_buttons()
        # Re-enable button
        if folder_path or (hasattr(start_processing, 'pending_files') and start_processing.pending_files):
            start_processing_btn.config(state="normal")

def start_scanning():
    """Legacy function - now calls start_processing"""
    start_processing()

def start_scan(folder_path):
    global is_scanning
    pause_flag.clear()
    stop_flag.clear()
    status_var.set("🔍 Starting scan...")
    progress_var.set(0)
    is_scanning = True

    threading.Thread(
        target=scan_folder,
        args=(folder_path, status_var.set, scan_done, tree, progress_var),
        daemon=True
    ).start()

def toggle_pause_resume():
    global is_paused
    if is_paused:
        # Resume
        pause_flag.clear()
        is_paused = False
        status_var.set("▶️ Resumed")
    else:
        # Pause
        pause_flag.set()
        is_paused = True
        status_var.set("⏸ Paused")
    update_control_buttons()

def stop_scan():
    global is_scanning, is_paused
    stop_flag.set()
    pause_flag.clear()
    is_scanning = False
    is_paused = False
    status_var.set("⛔ Scan stopped")
    update_control_buttons()

def start_over():
    """Reset the application state and clear all results"""
    global is_scanning, is_paused
    try:
        # Stop any running operations
        stop_flag.set()
        pause_flag.clear()
        
        # Reset scanning state
        is_scanning = False
        is_paused = False
        
        # Clear all results with error handling
        reset_table()
        
        # Reset UI elements
        status_var.set("Ready for new selection")
        selected_folder.set("")
        progress_var.set(0)
        
        # Reset Start Processing button and re-enable all input methods
        start_processing_btn.config(state="disabled")
        browse_button.config(state="normal")
        browse_files_btn.config(state="normal")
        
        # Clear pending files and selection status
        if hasattr(start_processing, 'pending_files'):
            start_processing.pending_files = []
        selection_status_label.config(text="")
        drop_label.config(text="Drag & Drop Files Here", fg=TEXT_MUTED)
        
        # Update control buttons
        update_control_buttons()
        
        # Clear drop area text
        if 'drop_label' in globals():
            drop_label.config(text="Drag & Drop Files Here\nOr use Browse Files button above", fg=TEXT_MUTED)
        
        # Log successful reset
        print("Application state reset successfully")
        
    except Exception as e:
        print(f"Error during start over: {str(e)}")
        # Even if there's an error, try to reset basic state
        is_scanning = False
        is_paused = False
        status_var.set("Reset with errors - Ready for new selection")
        messagebox.showwarning("Reset Warning", f"Reset completed with some errors:\n{str(e)}")

def reset_table():
    """Clear all results from the table with error handling"""
    try:
        if 'tree' in globals() and tree.winfo_exists():
            # Clear all items from the tree
            for row in tree.get_children():
                tree.delete(row)
            print(f"Cleared {len(tree.get_children())} items from results table")
        else:
            print("Results table not found or not initialized")
    except Exception as e:
        print(f"Error clearing results table: {str(e)}")
        # Try alternative clearing method
        try:
            tree.delete(*tree.get_children())
        except:
            print("Alternative table clearing method also failed")

def scan_done():
    global is_scanning, is_paused
    is_scanning = False
    is_paused = False
    status_var.set("✅ Done.")
    update_control_buttons()

def update_control_buttons():
    if is_scanning:
        if is_paused:
            pause_resume_btn.config(text="▶️ Resume", state="normal")
        else:
            pause_resume_btn.config(text="⏸ Pause", state="normal")
        stop_btn.config(state="normal")
        start_over_btn.config(state="normal")
        # Show pause/resume and stop buttons
        pause_resume_btn.pack(side="left", padx=(0, 10))
        stop_btn.pack(side="left", padx=(0, 10))
    else:
        # Hide pause/resume and stop buttons when not scanning
        pause_resume_btn.pack_forget()
        stop_btn.pack_forget()
        start_over_btn.config(state="normal")

def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    apply_theme()
    theme_btn.config(text="🌙 Dark Mode" if not dark_mode else "☀️ Light Mode")

def apply_theme():
    if dark_mode:
        # Chakra UI Dark Theme
        bg_main = "#09090b"  # Updated to user requested color
        bg_surface = "#2D3748"
        bg_lighter = "#4A5568"
        text_primary = "#F7FAFC"
        text_secondary = "#E2E8F0"
        text_muted = "#A0AEC0"
        accent_green = "#68D391"
    else:
        # Light Theme
        bg_main = "#FFFFFF"
        bg_surface = "#F7FAFC"
        bg_lighter = "#E2E8F0"
        text_primary = "#1A202C"
        text_secondary = "#2D3748"
        text_muted = "#4A5568"
        accent_green = "#38A169"
    
    # Update root and frames
    root.configure(bg=bg_main)
    for widget in [top_frame, progress_frame, btn_frame, main_frame, process_tab, process_content, 
                   input_methods_frame, methods_container, input_column, guide_column,
                   results_tab, results_content, table_container, tree_frame,
                   vt_tab, vt_content, vt_header_frame, vt_action_frame,
                   vt_api_frame, vt_status_frame, vt_progress_frame, vt_table_container, 
                   vt_tree_frame, vt_bottom_frame, vt_info_frame]:
        try:
            if widget.winfo_exists():
                widget.configure(bg=bg_main)
        except:
            pass  # Skip if widget doesn't exist
    
    # Update drop frame color
    if drop_frame.winfo_exists():
        drop_frame.configure(bg=bg_surface)
    
    # Update labels
    for label in [title_label, progress_label, status_label, input_label, selection_status_label,
                  guide_text, results_header, vt_header, vt_api_status_label, vt_status_label, vt_info_label,
                  vt_daily_quota_label, vt_monthly_quota_label]:
        try:
            if label.winfo_exists():
                if label == status_label:
                    label.configure(bg=bg_main, fg=accent_green)
                elif label in [selection_status_label, guide_text, vt_api_status_label, vt_status_label, vt_info_label,
                              vt_daily_quota_label, vt_monthly_quota_label]:
                    label.configure(bg=bg_main, fg=text_muted)
                elif label == drop_label:
                    label.configure(bg=bg_surface, fg=text_muted)
                else:
                    label.configure(bg=bg_main, fg=text_primary)
        except:
            pass  # Skip if label doesn't exist
    
    # Update ttk styles
    style.configure(".", background=bg_main, foreground=text_primary, fieldbackground=bg_surface)
    style.configure("TLabel", background=bg_main, foreground=text_primary)
    style.configure("TButton", background=bg_surface, foreground=text_primary)
    style.configure("TNotebook", background=bg_main)
    style.configure("TNotebook.Tab", background=bg_surface, foreground=text_secondary)
    style.configure("Treeview", background=bg_surface, fieldbackground=bg_surface, foreground=text_primary)
    style.configure("Treeview.Heading", background=bg_lighter, foreground=text_primary)
    style.configure("TProgressbar", background=accent_green, troughcolor=bg_surface)

def copy_selected_row():
    selection = tree.selection()
    if selection:
        item = tree.item(selection[0])
        values = item['values']
        if values:
            # Format: Source | Filename | Path | Size | Extension | MD5 | SHA1 | SHA256
            copy_text = f"{values[0]}\t{values[1]}\t{values[2]}\t{values[3]}\t{values[4]}\t{values[5]}\t{values[6]}\t{values[7]}"
            root.clipboard_clear()
            root.clipboard_append(copy_text)
            messagebox.showinfo("Copied", "Selected row copied to clipboard!")
    else:
        messagebox.showwarning("No Selection", "Please select a row to copy.")

def copy_all_results():
    if tree.get_children():
        all_data = []
        # Add header
        all_data.append("Source\tFilename\tPath\tSize\tExtension\tMD5\tSHA1\tSHA256")
        # Add all rows
        for child in tree.get_children():
            item = tree.item(child)
            values = item['values']
            all_data.append(f"{values[0]}\t{values[1]}\t{values[2]}\t{values[3]}\t{values[4]}\t{values[5]}\t{values[6]}\t{values[7]}")
        
        copy_text = "\n".join(all_data)
        root.clipboard_clear()
        root.clipboard_append(copy_text)
        messagebox.showinfo("Copied", f"All {len(all_data)-1} results copied to clipboard!")
    else:
        messagebox.showwarning("No Data", "No results to copy.")

def clear_all_results():
    """Clear all results from the table"""
    global file_selection_state, select_all_state
    for item in tree.get_children():
        tree.delete(item)
    file_selection_state.clear()
    select_all_state = False
    update_select_all_button()
    status_var.set("🗑️ All results cleared")

def toggle_select_all():
    """Toggle select all files"""
    global select_all_state, file_selection_state
    select_all_state = not select_all_state
    
    # Update all file selections
    for item in tree.get_children():
        file_path = tree.item(item)['values'][3]  # Path is at index 3
        file_selection_state[file_path] = select_all_state
        # Update checkbox display
        values = list(tree.item(item)['values'])
        values[0] = "☑️" if select_all_state else "☐"
        tree.item(item, values=values)
    
    update_select_all_button()

def update_select_all_button():
    """Update the select all button text and header"""
    global select_all_state
    if select_all_state:
        select_all_btn.config(text="☐ Deselect All")
        tree.heading("Select", text="☑️")
    else:
        select_all_btn.config(text="☑️ Select All")
        tree.heading("Select", text="☐")

def toggle_file_selection(file_path):
    """Toggle selection for a specific file"""
    global file_selection_state
    current_state = file_selection_state.get(file_path, False)
    file_selection_state[file_path] = not current_state
    
    # Update the specific row
    for item in tree.get_children():
        if tree.item(item)['values'][3] == file_path:  # Path is at index 3
            values = list(tree.item(item)['values'])
            values[0] = "☑️" if file_selection_state[file_path] else "☐"
            tree.item(item, values=values)
            break
    
    # Update select all state based on current selections
    total_files = len(tree.get_children())
    selected_files = sum(1 for selected in file_selection_state.values() if selected)
    
    global select_all_state
    if selected_files == total_files and total_files > 0:
        select_all_state = True
    else:
        select_all_state = False
    
    update_select_all_button()

def move_selected_to_vt():
    """Move selected files to VirusTotal tab"""
    global file_selection_state
    
    # Get selected files
    selected_files = []
    for item in tree.get_children():
        item_values = tree.item(item)['values']
        file_path = item_values[3]  # Path is at index 3
        if file_selection_state.get(file_path, False):
            selected_files.append({
                'filename': item_values[2],  # Filename at index 2
                'path': file_path,
                'md5': item_values[6],  # MD5 at index 6
                'sha1': item_values[7],  # SHA1 at index 7
                'sha256': item_values[8]  # SHA256 at index 8
            })
    
    if not selected_files:
        messagebox.showwarning("No Selection", "Please select files to move to VirusTotal scanner.")
        return
    
    # Clear current VT queue and populate with selected files
    for item in vt_tree.get_children():
        vt_tree.delete(item)
    
    # Add selected files to VT queue using MD5 hash
    for file_info in selected_files:
        md5_hash = file_info['md5']
        if md5_hash and md5_hash != "Error":
            vt_tree.insert('', 'end', 
                          values=("QUEUED", "MD5", md5_hash, "?", "?", "?", "Pending", file_info['filename']),
                          open=False)
    
    # Update status and switch to VT tab
    vt_status_label.config(text=f"📊 {len(selected_files)} files ready for VirusTotal analysis")
    tabs.select(vt_tab)  # Switch to VT tab
    messagebox.showinfo("Files Moved", f"{len(selected_files)} files moved to VirusTotal scanner.\nUsing MD5 hashes for analysis.")

def on_tree_click(event):
    """Handle clicks on the results tree"""
    region = tree.identify_region(event.x, event.y)
    if region == "cell":
        column = tree.identify_column(event.x)  # Only takes x coordinate
        if column == "#1":  # First column (Select)
            item = tree.identify_row(event.y)
            if item:
                item_values = tree.item(item)['values']
                if len(item_values) >= 4:  # Ensure we have enough values
                    file_path = item_values[3]  # Path is at index 3
                    toggle_file_selection(file_path)

def quick_vt_check():
    """Quick VirusTotal check for selected row"""
    if not vt_api_key:
        messagebox.showwarning("API Key Required", "Please set your VirusTotal API key first.")
        set_vt_api_key()
        return
    
    selection = tree.selection()
    if not selection:
        messagebox.showwarning("No Selection", "Please select a row to check with VirusTotal.")
        return
    
    item = selection[0]
    item_data = tree.item(item)
    values = item_data['values']
    
    if len(values) >= 8:
        filename = values[1]
        md5_hash = values[5]
        sha1_hash = values[6] 
        sha256_hash = values[7]
        
        # Prefer SHA256, then SHA1, then MD5
        hash_to_use = sha256_hash if sha256_hash and sha256_hash != "Error" else \
                     sha1_hash if sha1_hash and sha1_hash != "Error" else \
                     md5_hash if md5_hash and md5_hash != "Error" else None
        
        if hash_to_use:
            # Show immediate feedback
            messagebox.showinfo("Checking VirusTotal", f"Checking {filename} with VirusTotal...\nThis may take a few seconds.")
            
            def vt_check_thread():
                try:
                    response = check_hash_with_vt(hash_to_use)
                    
                    def show_result():
                        if response and 'data' in response:
                            data = response['data']
                            attributes = data.get('attributes', {})
                            stats = attributes.get('last_analysis_stats', {})
                            
                            malicious = stats.get('malicious', 0)
                            suspicious = stats.get('suspicious', 0)
                            harmless = stats.get('harmless', 0)
                            undetected = stats.get('undetected', 0)
                            
                            # Determine status
                            if malicious > 0:
                                status = f"🚨 MALICIOUS"
                                details = f"❌ {malicious} engines detected this file as malicious!"
                                msg_type = "error"
                            elif suspicious > 0:
                                status = f"⚠️ SUSPICIOUS"
                                details = f"⚠️ {suspicious} engines flagged this file as suspicious."
                                msg_type = "warning"
                            else:
                                status = f"✅ CLEAN"
                                details = f"✅ File appears clean ({harmless + undetected} engines checked)."
                                msg_type = "info"
                            
                            scan_date = attributes.get('last_analysis_date', 0)
                            scan_date_str = datetime.fromtimestamp(scan_date).strftime("%Y-%m-%d %H:%M") if scan_date else "Unknown"
                            
                            result_text = f"""
VirusTotal Result for: {filename}
{'-' * 50}

Status: {status}
{details}

Detection Statistics:
• Malicious: {malicious}
• Suspicious: {suspicious}
• Harmless: {harmless}
• Undetected: {undetected}

Last Scan: {scan_date_str}
Hash: {hash_to_use}
"""
                            
                            if msg_type == "error":
                                messagebox.showerror("VirusTotal Result", result_text)
                            elif msg_type == "warning":
                                messagebox.showwarning("VirusTotal Result", result_text)
                            else:
                                messagebox.showinfo("VirusTotal Result", result_text)
                        
                        elif response and 'error' in response:
                            if "not found" in response['error'].lower():
                                messagebox.showinfo("VirusTotal Result", 
                                                   f"File not found in VirusTotal database.\n\nThis could mean:\n• The file is new/rare\n• The file hasn't been submitted to VT\n• The hash might be incorrect\n\nFilename: {filename}\nHash: {hash_to_use}")
                            else:
                                messagebox.showerror("VirusTotal Error", f"Error checking file:\n{response['error']}")
                        else:
                            messagebox.showerror("VirusTotal Error", "Unknown error occurred while checking the file.")
                    
                    root.after(0, show_result)
                    
                except Exception as e:
                    def show_error():
                        messagebox.showerror("VirusTotal Error", f"Error checking file:\n{str(e)}")
                    root.after(0, show_error)
            
            # Start the check in background
            threading.Thread(target=vt_check_thread, daemon=True).start()
        else:
            messagebox.showwarning("No Valid Hash", "No valid hash found for this file.")
    else:
        messagebox.showwarning("Invalid Data", "Selected row doesn't contain valid file data.")

def process_dropped_files(file_paths):
    """Process dropped or selected files with progress tracking"""
    if not file_paths:
        return
    
    # Start processing immediately with visual feedback
    global is_scanning, is_paused
    is_scanning = True
    is_paused = False
    update_control_buttons()
    
    # Update drop area and status
    drop_label.config(text=f"⚡ Processing {len(file_paths)} file(s)...", fg=ACCENT_GREEN)
    status_var.set(f"🔍 Processing {len(file_paths)} selected files...")
    progress_var.set(0)
    
    def process_files_thread():
        global is_scanning, is_paused
        
        for idx, file_path in enumerate(file_paths, 1):
            # Check for stop/pause flags
            if stop_flag.is_set():
                break
            while pause_flag.is_set():
                threading.Event().wait(0.2)
                
            if os.path.isfile(file_path):
                filename = os.path.basename(file_path)
                file_size = get_file_size(file_path)
                file_ext = os.path.splitext(file_path)[1].lower() or "No Extension"
                
                # Update progress and status
                progress_percentage = (idx / len(file_paths)) * 100
                
                def update_progress():
                    status_var.set(f"🔍 Processing: {filename} ({idx}/{len(file_paths)})")
                    progress_var.set(progress_percentage)
                
                root.after(0, update_progress)
                
                # Calculate hashes
                md5, sha1, sha256 = calculate_hashes(file_path)
                
                # Update UI in main thread
                def update_files_ui():
                    # Initialize file selection state
                    file_selection_state[file_path] = False
                    tree.insert('', tk.END, values=("☐", "Files", filename, file_path, file_size, file_ext, md5, sha1, sha256))
                
                root.after(0, update_files_ui)
        
        # Finalize processing
        def reset_ui():
            global is_scanning, is_paused
            is_scanning = False
            is_paused = False
            update_control_buttons()
            
            drop_label.config(text="📎 Click to select files or drop them here\n✨ Click 'Start Processing' to begin", 
                            fg=TEXT_MUTED)
            status_var.set(f"✅ Successfully processed {len(file_paths)} files")
            progress_var.set(100)
        
        root.after(0, reset_ui)
    
    # Process files in background thread
    threading.Thread(target=process_files_thread, daemon=True).start()

def browse_files_for_hash():
    """Browse and select files for hash calculation"""
    files = filedialog.askopenfilenames(
        title="Select Files for Hash Calculation",
        filetypes=[
            ("All Files", "*.*"),
            ("Text Files", "*.txt"),
            ("Images", "*.jpg *.jpeg *.png *.gif *.bmp"),
            ("Documents", "*.pdf *.doc *.docx *.xls *.xlsx"),
            ("Archives", "*.zip *.rar *.7z *.tar *.gz")
        ]
    )
    
    if files:
        # Store files for later processing instead of immediately processing
        start_processing.pending_files = list(files)
        status_var.set(f"[FILES] Selected {len(files)} files - Ready to process")
        selection_status_label.config(text=f"FILES: {len(files)} files selected", fg=ACCENT_GREEN)
        drop_label.config(text=f"{len(files)} files selected - Other input methods disabled", fg=ACCENT_GREEN)
        # Enable Start Processing button
        start_processing_btn.config(state="normal")
        # Clear any folder selection and disable other input methods
        if selected_folder.get():
            selected_folder.set("")
        # Disable other input methods
        browse_button.config(state="disabled")

# === VIRUSTOTAL FUNCTIONS ===
import requests
import json
from datetime import datetime

def set_vt_api_key():
    """Set VirusTotal API key"""
    global vt_api_key
    
    # Create API key input dialog
    api_dialog = tk.Toplevel(root)
    api_dialog.title("VirusTotal API Key")
    api_dialog.geometry("500x200")
    api_dialog.configure(bg=BG_MAIN)
    api_dialog.resizable(False, False)
    
    # Center the dialog
    api_dialog.transient(root)
    api_dialog.grab_set()
    api_dialog.focus_set()
    
    # API key input frame
    input_frame = tk.Frame(api_dialog, bg=BG_MAIN)
    input_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    tk.Label(input_frame, text="Enter your VirusTotal API Key:", 
             bg=BG_MAIN, fg=TEXT_PRIMARY, font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))
    
    tk.Label(input_frame, text="Get your free API key from: https://www.virustotal.com/gui/my-apikey", 
             bg=BG_MAIN, fg=TEXT_MUTED, font=("Arial", 10)).pack(anchor="w", pady=(0, 15))
    
    api_key_var = tk.StringVar(value=vt_api_key)
    api_entry = tk.Entry(input_frame, textvariable=api_key_var, font=("Arial", 10), 
                        show="*", width=60, bg=BG_SURFACE, fg=TEXT_PRIMARY, 
                        insertbackground=TEXT_PRIMARY)
    api_entry.pack(fill="x", pady=(0, 15))
    api_entry.focus()
    
    # Buttons
    btn_frame = tk.Frame(input_frame, bg=BG_MAIN)
    btn_frame.pack(fill="x")
    
    def save_key_action():
        global vt_api_key
        new_key = api_key_var.get().strip()
        if new_key:
            vt_api_key = new_key
            # Save to persistent storage using the global function
            save_api_key(new_key)
            vt_api_status_label.config(text=f"API Key: {'*' * (len(new_key) - 8) + new_key[-8:] if len(new_key) > 8 else '*' * len(new_key)}")
            messagebox.showinfo("Success", "VirusTotal API key saved successfully!")
            api_dialog.destroy()
        else:
            messagebox.showwarning("Invalid Key", "Please enter a valid API key.")
    
    def cancel():
        api_dialog.destroy()
    
    ttk.Button(btn_frame, text="💾 Save", command=save_key_action).pack(side="left", padx=(0, 10))
    ttk.Button(btn_frame, text="❌ Cancel", command=cancel).pack(side="left")
    
    # Bind Enter key
    api_entry.bind("<Return>", lambda e: save_key_action())

def get_selected_hashes():
    """Get selected hashes from the results table"""
    global selected_hashes
    
    selection = tree.selection()
    if not selection:
        messagebox.showwarning("No Selection", "Please select files from the Results tab to check with VirusTotal.")
        return
    
    selected_hashes.clear()
    
    for item in selection:
        item_data = tree.item(item)
        values = item_data['values']
        if len(values) >= 8:
            # Get all hash types
            md5_hash = values[5]
            sha1_hash = values[6] 
            sha256_hash = values[7]
            filename = values[1]
            
            # Prefer SHA256, then SHA1, then MD5
            hash_to_use = sha256_hash if sha256_hash and sha256_hash != "Error" else \
                         sha1_hash if sha1_hash and sha1_hash != "Error" else \
                         md5_hash if md5_hash and md5_hash != "Error" else None
            
            if hash_to_use:
                selected_hashes.append({
                    'filename': filename,
                    'hash': hash_to_use,
                    'hash_type': 'SHA256' if hash_to_use == sha256_hash else 'SHA1' if hash_to_use == sha1_hash else 'MD5'
                })
    
    if selected_hashes:
        vt_status_label.config(text=f"📊 Selected {len(selected_hashes)} files for VirusTotal analysis")
        populate_vt_queue()
    else:
        messagebox.showwarning("No Valid Hashes", "No valid hashes found in selected files.")

def populate_vt_queue():
    """Populate the VirusTotal queue with selected hashes"""
    # Clear previous queue
    for item in vt_tree.get_children():
        vt_tree.delete(item)
    
    # Add selected hashes to queue
    for hash_info in selected_hashes:
        vt_tree.insert('', 'end', 
                      text=f"📄 {hash_info['filename']}",
                      values=("Queued", hash_info['hash_type'], hash_info['hash'][:32] + "...", "Waiting..."),
                      open=False)

def check_virustotal():
    """Check files in VT queue with VirusTotal API using MD5 hashes"""
    if not vt_api_key:
        messagebox.showwarning("API Key Required", "Please set your VirusTotal API key first.")
        set_vt_api_key()
        return
    
    # Get files from VT queue
    queue_files = []
    for item in vt_tree.get_children():
        item_values = vt_tree.item(item)['values']
        if len(item_values) >= 8:
            filename = item_values[7]  # Filename at index 7
            hash_value = item_values[2].replace("...", "")  # Remove the "..." from display
            
            # Find the full hash from the original item text or reconstruct
            queue_files.append({
                'item': item,
                'filename': filename,
                'hash': hash_value,
                'hash_type': item_values[1]  # Should be MD5
            })
    
    if not queue_files:
        messagebox.showwarning("No Files", "No files in VirusTotal queue. Please move files from Results tab first.")
        return
    
    # Check quota before proceeding
    requests_needed = len(queue_files)
    can_proceed, quota_message = check_quota_before_request(requests_needed)
    
    if not can_proceed:
        messagebox.showerror("Quota Exceeded", f"{quota_message}\n\nFiles to check: {requests_needed}\n\nPlease try again when quota resets or reduce the number of files.")
        update_quota_display()  # Refresh display
        return
    
    # Show quota warning if high usage
    status = get_quota_status()
    if requests_needed > 50:  # Warn for large batches
        confirm = messagebox.askyesno(
            "Large Batch Check", 
            f"You're about to check {requests_needed} files.\n\n"
            f"Current quota usage:\n"
            f"• Daily: {status['daily_used']}/{status['daily_limit']} (will use {requests_needed} more)\n"
            f"• Monthly: {status['monthly_used']}/{status['monthly_limit']} (will use {requests_needed} more)\n\n"
            f"Continue with batch check?"
        )
        if not confirm:
            return
    
    # Start checking in background thread
    def vt_check_thread():
        total_files = len(queue_files)
        
        for idx, file_info in enumerate(queue_files, 1):
            # Update status
            def update_status():
                vt_status_label.config(text=f"🔍 Checking {file_info['filename']} ({idx}/{total_files})")
                vt_progress_var.set((idx / total_files) * 100)
            
            root.after(0, update_status)
            
            # Update status to checking
            def update_tree_checking():
                vt_tree.item(file_info['item'], values=("Checking...", file_info['hash_type'], 
                                                      file_info['hash'][:16] + "...", "?", "?", "?", "Scanning...", file_info['filename']))
            
            root.after(0, update_tree_checking)
            
            # Make API request using MD5 hash
            try:
                response = check_hash_with_vt(file_info['hash'])
                
                if response and 'data' in response:
                    data = response['data']
                    attributes = data.get('attributes', {})
                    stats = attributes.get('last_analysis_stats', {})
                    
                    malicious = stats.get('malicious', 0)
                    suspicious = stats.get('suspicious', 0)
                    harmless = stats.get('harmless', 0)
                    undetected = stats.get('undetected', 0)
                    
                    # Determine status
                    if malicious > 0:
                        status = "THREAT"
                        status_color = "red"
                    elif suspicious > 0:
                        status = "SUSPICIOUS"
                        status_color = "orange"
                    else:
                        status = "CLEAN"
                        status_color = "green"
                    
                    scan_date = attributes.get('last_analysis_date', 0)
                    scan_date_str = datetime.fromtimestamp(scan_date).strftime("%m/%d/%Y") if scan_date else "Unknown"
                    
                    # Update tree with detailed results and color coding
                    def update_tree_result():
                        # Determine tag based on threat level
                        tag = "clean" if (malicious + suspicious) == 0 else "threat"
                        
                        vt_tree.item(file_info['item'], values=(status, file_info['hash_type'], 
                                                              file_info['hash'][:16] + "...", 
                                                              str(malicious), str(suspicious), 
                                                              str(harmless + undetected), scan_date_str, file_info['filename']),
                                   tags=(tag,))
                    
                    root.after(0, update_tree_result)
                    
                    # Store detailed results
                    vt_results[file_info['hash']] = {
                        'filename': file_info['filename'],
                        'response': response,
                        'status': status,
                        'stats': stats,
                        'scan_date': scan_date_str
                    }
                    
                elif response and 'error' in response:
                    # Handle errors
                    error_msg = response['error']
                    def update_tree_error():
                        if "not found" in error_msg.lower():
                            vt_tree.item(file_info['item'], values=("NOT FOUND", file_info['hash_type'], 
                                                                  file_info['hash'][:16] + "...", "0", "0", "0", "Not scanned", file_info['filename']),
                                       tags=("clean",))  # Not found = clean
                        else:
                            vt_tree.item(file_info['item'], values=("ERROR", file_info['hash_type'], 
                                                                  file_info['hash'][:16] + "...", "?", "?", "?", error_msg[:20], file_info['filename']),
                                       tags=())  # No color for errors
                    
                    root.after(0, update_tree_error)
                
                else:
                    def update_tree_unknown():
                        vt_tree.item(file_info['item'], values=("ERROR", file_info['hash_type'], 
                                                              file_info['hash'][:16] + "...", "?", "?", "?", "Unknown error", file_info['filename']),
                                   tags=())  # No color for errors
                    
                    root.after(0, update_tree_unknown)
            
            except Exception as e:
                def update_tree_exception():
                    vt_tree.item(file_info['item'], values=("ERROR", file_info['hash_type'], 
                                                          file_info['hash'][:16] + "...", "?", "?", "?", f"Error: {str(e)[:20]}", file_info['filename']),
                                   tags=())  # No color for errors
                
                root.after(0, update_tree_exception)
            
            # Rate limiting - VirusTotal free API allows 4 requests per minute
            import time
            if idx < total_files:  # Don't sleep after last request
                time.sleep(16)  # 16 seconds between requests for safety
        
        # Final status update
        def final_update():
            completed = len([r for r in vt_results.values()])
            threats = sum(1 for r in vt_results.values() if 'THREAT' in r.get('status', ''))
            suspicious = sum(1 for r in vt_results.values() if 'SUSPICIOUS' in r.get('status', ''))
            clean = sum(1 for r in vt_results.values() if 'CLEAN' in r.get('status', ''))
            
            vt_status_label.config(text=f"✅ Scan Complete: {threats} threats, {suspicious} suspicious, {clean} clean files")
            vt_progress_var.set(100)
        
        root.after(0, final_update)
    
    # Start the thread
    threading.Thread(target=vt_check_thread, daemon=True).start()
    
    # Start the thread
    threading.Thread(target=vt_check_thread, daemon=True).start()

def check_hash_with_vt(hash_value):
    """Make API request to VirusTotal with quota tracking"""
    # Clean the hash value to remove any spaces or invalid characters
    clean_hash = hash_value.strip().replace(" ", "")
    
    # Check quota before making request
    can_proceed, quota_message = check_quota_before_request(1)
    if not can_proceed:
        return {"error": f"Quota exceeded: {quota_message}"}
    
    url = f"https://www.virustotal.com/api/v3/files/{clean_hash}"
    headers = {
        "accept": "application/json",
        "x-apikey": vt_api_key
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        # Update quota usage after successful API call (even if 404/error, we used a request)
        update_quota_usage(1)
        # Update UI display in main thread
        root.after(0, update_quota_display)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {"error": "File not found in VirusTotal database"}
        elif response.status_code == 429:
            return {"error": "Rate limit exceeded - please wait before making more requests"}
        elif response.status_code == 401:
            return {"error": "Invalid API key - please check your VirusTotal API key"}
        else:
            return {"error": f"API error: {response.status_code} - {response.text[:100]}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}

def view_vt_details():
    """View detailed VirusTotal results for selected item"""
    selection = vt_tree.selection()
    if not selection:
        messagebox.showwarning("No Selection", "Please select an item to view details.")
        return
    
    item = selection[0]
    item_data = vt_tree.item(item)
    filename = item_data['text'].replace("📄 ", "")
    
    # Find the hash for this filename
    hash_value = None
    for hash_info in selected_hashes:
        if hash_info['filename'] == filename:
            hash_value = hash_info['hash']
            break
    
    if not hash_value or hash_value not in vt_results:
        messagebox.showinfo("No Details", "No detailed results available for this file.")
        return
    
    # Create details window
    details_window = tk.Toplevel(root)
    details_window.title(f"VirusTotal Details - {filename}")
    details_window.geometry("800x600")
    details_window.configure(bg=BG_MAIN)
    
    # Details content
    details_frame = tk.Frame(details_window, bg=BG_MAIN)
    details_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Scrollable text area
    text_frame = tk.Frame(details_frame, bg=BG_MAIN)
    text_frame.pack(fill="both", expand=True)
    
    details_text = tk.Text(text_frame, bg=BG_SURFACE, fg=TEXT_PRIMARY, 
                          font=("Consolas", 10), wrap="word")
    details_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=details_text.yview)
    details_text.configure(yscrollcommand=details_scrollbar.set)
    
    details_text.pack(side="left", fill="both", expand=True)
    details_scrollbar.pack(side="right", fill="y")
    
    # Populate details
    result = vt_results[hash_value]
    details_content = f"""
VirusTotal Analysis Report
=========================

File: {result['filename']}
Hash: {hash_value}
Status: {result['status']}
Last Scan: {result['scan_date']}

Detection Statistics:
- Malicious: {result['stats'].get('malicious', 0)}
- Suspicious: {result['stats'].get('suspicious', 0)}
- Harmless: {result['stats'].get('harmless', 0)}
- Undetected: {result['stats'].get('undetected', 0)}

Raw API Response:
{json.dumps(result['response'], indent=2)}
"""
    
    details_text.insert("1.0", details_content)
    details_text.config(state="disabled")

def export_vt_report():
    """Export VirusTotal results to a file"""
    if not vt_results:
        messagebox.showwarning("No Data", "No VirusTotal results to export.")
        return
    
    filename = filedialog.asksaveasfilename(
        title="Save VirusTotal Report",
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("JSON Files", "*.json"), ("All Files", "*.*")]
    )
    
    if filename:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=== VIRUSTOTAL ANALYSIS REPORT ===\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Files Analyzed: {len(vt_results)}\n\n")
                
                for hash_value, result in vt_results.items():
                    f.write(f"\n--- {result['filename']} ---\n")
                    f.write(f"Hash: {hash_value}\n")
                    f.write(f"Status: {result['status']}\n")
                    f.write(f"Last Scan: {result['scan_date']}\n")
                    f.write(f"Detection Stats: {result['stats']}\n")
                    f.write("-" * 50 + "\n")
            
            messagebox.showinfo("Export Complete", f"VirusTotal report saved to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save report:\n{str(e)}")

def clear_vt_results():
    """Clear VirusTotal results"""
    global vt_results, selected_hashes
    
    vt_results.clear()
    selected_hashes.clear()
    
    for item in vt_tree.get_children():
        vt_tree.delete(item)
    
    vt_status_label.config(text="📊 No files selected for VirusTotal analysis")
    vt_progress_var.set(0)

# === GUI ===
root = tk.Tk()
root.title("Hash Calculator - Instant File & Folder Analysis")
root.geometry("1280x700")

# Create StringVar after root window
selected_folder = tk.StringVar()

# === Chakra UI Dark Theme Styling ===
# Colors based on Chakra UI dark theme
BG_MAIN = "#09090b"      # Very dark background - user requested
BG_SURFACE = "#2D3748"   # gray.700 - surface/card background  
BG_LIGHTER = "#4A5568"   # gray.600 - lighter surfaces
TEXT_PRIMARY = "#F7FAFC" # gray.100 - primary text
TEXT_SECONDARY = "#E2E8F0" # gray.200 - secondary text
TEXT_MUTED = "#A0AEC0"   # gray.400 - muted text
ACCENT_BLUE = "#63B3ED"  # blue.300 - primary accent
ACCENT_GREEN = "#68D391" # green.300 - success/positive
ACCENT_RED = "#FC8181"   # red.300 - error/warning
FOCUS_RING = "#4299E1"   # blue.500 - focus indicators

root.configure(bg=BG_MAIN)

style = ttk.Style(root)
root.option_add("*Font", "Arial 10")

style.theme_use("clam")

style.configure(".", background=BG_MAIN, foreground=TEXT_PRIMARY, fieldbackground=BG_SURFACE)
style.configure("TLabel", background=BG_MAIN, foreground=TEXT_PRIMARY)
style.configure("TButton", background=BG_SURFACE, foreground=TEXT_PRIMARY, padding=8, relief="flat")
style.map("TButton", 
          background=[("active", BG_LIGHTER), ("pressed", BG_LIGHTER)],
          foreground=[("active", TEXT_PRIMARY)])
style.configure("TNotebook", background=BG_MAIN, tabposition='n')  # Changed to top
style.configure("TNotebook.Tab", background=BG_SURFACE, foreground=TEXT_SECONDARY, padding=[15, 8], relief="flat")
style.map("TNotebook.Tab", 
          background=[("selected", BG_LIGHTER)], 
          foreground=[("selected", TEXT_PRIMARY)])
style.configure("Treeview", background=BG_SURFACE, fieldbackground=BG_SURFACE, foreground=TEXT_PRIMARY, rowheight=28)
style.configure("Treeview.Heading", background=BG_LIGHTER, foreground=TEXT_PRIMARY, relief="flat")
style.map("Treeview.Heading", background=[("active", BG_LIGHTER)])
style.configure("TProgressbar", background=ACCENT_GREEN, troughcolor=BG_SURFACE)

# === Top Control Panel ===
top_frame = tk.Frame(root, bg=BG_MAIN)
top_frame.pack(fill="x", pady=10, padx=15)

# Title and theme toggle
title_frame = tk.Frame(top_frame, bg=BG_MAIN)
title_frame.pack(fill="x")

title_label = tk.Label(title_frame, text="Hash Calculator", bg=BG_MAIN, fg=TEXT_PRIMARY, font=("Arial", 16, "bold"))
title_label.pack(side="left")

theme_btn = ttk.Button(title_frame, text="☀️ Light Mode", command=toggle_theme)
theme_btn.pack(side="right")

# Progress section
progress_frame = tk.Frame(top_frame, bg=BG_MAIN)
progress_frame.pack(fill="x", pady=(10, 5))

progress_label = tk.Label(progress_frame, text="Progress:", bg=BG_MAIN, fg=TEXT_SECONDARY, font=("Arial", 10))
progress_label.pack(anchor="w")

progress_var = tk.DoubleVar()
progress = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate", variable=progress_var, style="TProgressbar", length=400)
progress.pack(fill="x", pady=(5, 0))

# Control buttons (initially hidden)
btn_frame = tk.Frame(top_frame, bg=BG_MAIN)
btn_frame.pack(anchor="w", pady=(10, 0))

pause_resume_btn = ttk.Button(btn_frame, text="⏸ Pause", command=toggle_pause_resume, state="disabled")
stop_btn = ttk.Button(btn_frame, text="⏹ Stop", command=stop_scan, state="disabled")
start_over_btn = ttk.Button(btn_frame, text="🔄 Start Over", command=start_over)
start_over_btn.pack(side="left")

# === Main Content Area ===
main_frame = tk.Frame(root, bg=BG_MAIN)
main_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

# === Notebook (Tabs) - Top positioned ===
tabs = ttk.Notebook(main_frame, style="TNotebook")
tabs.pack(fill="both", expand=True, anchor="nw")  # Anchor to northwest (top-left)

# === Hash Calculator Tab (merged Process + Drag & Drop) ===
process_tab = tk.Frame(tabs, bg=BG_MAIN)
tabs.add(process_tab, text="Hash Calculator")

# Hash Calculator tab content
process_content = tk.Frame(process_tab, bg=BG_MAIN)
process_content.pack(fill="both", expand=True, padx=20, pady=20)

status_var = tk.StringVar(value="🚀 Ready! Select a folder or files to start hash calculation")
status_label = tk.Label(process_content, textvariable=status_var, anchor="w", fg=ACCENT_GREEN, bg=BG_MAIN, font=("Arial", 12))
status_label.pack(fill="x", pady=(0, 20))

# === Input Methods Section ===
input_methods_frame = tk.Frame(process_content, bg=BG_MAIN)
input_methods_frame.pack(fill="x", pady=(0, 20))

input_label = tk.Label(input_methods_frame, text="Choose Your Input Method", bg=BG_MAIN, fg=TEXT_PRIMARY, font=("Arial", 14, "bold"))
input_label.pack(anchor="w", pady=(0, 15))

# Create two columns - Left for unified input, Right for guide
methods_container = tk.Frame(input_methods_frame, bg=BG_MAIN)
methods_container.pack(fill="x")

# Left column - UNIFIED input methods
input_column = tk.Frame(methods_container, bg=BG_MAIN)
input_column.pack(side="left", fill="both", expand=True, padx=(0, 30))

# === UNIFIED INPUT SECTION ===
unified_section = tk.Frame(input_column, bg=BG_MAIN)
unified_section.pack(fill="x", pady=(0, 20))

# Input method buttons row
input_buttons_frame = tk.Frame(unified_section, bg=BG_MAIN)
input_buttons_frame.pack(fill="x", pady=(0, 15))

browse_button = ttk.Button(input_buttons_frame, text="Choose Folder", command=browse_folder)
browse_button.pack(side="left", padx=(0, 15))

browse_files_btn = ttk.Button(input_buttons_frame, text="Browse Files", command=browse_files_for_hash)
browse_files_btn.pack(side="left")

# Drag & Drop area
drop_frame = tk.Frame(unified_section, bg=BG_SURFACE, relief="solid", bd=2)
drop_frame.pack(fill="x", pady=(0, 15))

drop_label = tk.Label(drop_frame, 
                     text="Drag & Drop Files Here",
                     bg=BG_SURFACE, fg=TEXT_MUTED, font=("Arial", 11), 
                     justify="center", pady=20)
drop_label.pack(fill="x")

# Selection status display
selection_status_frame = tk.Frame(unified_section, bg=BG_MAIN)
selection_status_frame.pack(fill="x", pady=(0, 15))

selection_status_label = tk.Label(selection_status_frame, text="No selection made", 
                                 bg=BG_MAIN, fg=TEXT_MUTED, font=("Arial", 10))
selection_status_label.pack(anchor="w")

# Single Start Processing button
start_processing_btn = ttk.Button(unified_section, text="Start Processing", 
                                 command=start_processing, state="disabled",
                                 style="Accent.TButton")
start_processing_btn.pack(anchor="w")

# Right column - Quick guide (same as before)
guide_column = tk.Frame(methods_container, bg=BG_MAIN)
guide_column.pack(side="right", fill="both", expand=True, padx=(30, 0))

guide_header = tk.Label(guide_column, text="Quick Start Guide", bg=BG_MAIN, fg=TEXT_PRIMARY, font=("Arial", 12, "bold"))
guide_header.pack(anchor="w", pady=(0, 10))

guide_text = tk.Label(guide_column, 
                     text="STEP 1: Choose Input Method\n" +
                          "• FOLDER: Scans all files in a directory\n" +
                          "• FILES: Process specific files only\n" +
                          "• DRAG & DROP: Drop files directly\n\n" +
                          "STEP 2: Start Processing\n" +
                          "• Click the Start Processing button\n" +
                          "• Automatically switches to Results tab\n\n" +
                          "STEP 3: View Results\n" +
                          "• Right-click any cell to copy\n" +
                          "• Use checkboxes to select files\n" +
                          "• Move selected files to VT Scanner\n\n" +
                          "CONTROLS:\n" +
                          "• Pause/Resume during processing\n" +
                          "• Stop to cancel current operation\n" +
                          "• Start Over to reset everything",
                     bg=BG_MAIN, fg=TEXT_MUTED, font=("Arial", 9), 
                     justify="left", anchor="nw")
guide_text.pack(fill="x")

# === Results Tab ===
results_tab = tk.Frame(tabs, bg=BG_MAIN)
tabs.add(results_tab, text="Results")

# Results tab content
results_content = tk.Frame(results_tab, bg=BG_MAIN)
results_content.pack(fill="both", expand=True, padx=20, pady=20)

# Results header with copy buttons
results_header_frame = tk.Frame(results_content, bg=BG_MAIN)
results_header_frame.pack(fill="x", pady=(0, 10))

results_header = tk.Label(results_header_frame, text="Hash Calculation Results", bg=BG_MAIN, fg=TEXT_PRIMARY, font=("Arial", 14, "bold"))
results_header.pack(side="left")

# Copy and clear buttons
action_frame = tk.Frame(results_header_frame, bg=BG_MAIN)
action_frame.pack(side="right")

select_all_btn = ttk.Button(action_frame, text="☑️ Select All", command=lambda: toggle_select_all())
select_all_btn.pack(side="left", padx=(0, 10))

move_to_vt_btn = ttk.Button(action_frame, text="➡️ Move to VT", command=move_selected_to_vt)
move_to_vt_btn.pack(side="left", padx=(0, 10))

copy_selected_btn = ttk.Button(action_frame, text="📋 Copy Selected", command=copy_selected_row)
copy_selected_btn.pack(side="left", padx=(0, 10))

quick_vt_btn = ttk.Button(action_frame, text="🔍 Quick VT Check", command=quick_vt_check)
quick_vt_btn.pack(side="left", padx=(0, 10))

export_results_btn = ttk.Button(action_frame, text="📊 Export CSV", command=export_results_to_csv)
export_results_btn.pack(side="left", padx=(0, 10))

copy_all_btn = ttk.Button(action_frame, text="📋 Copy All", command=copy_all_results)
copy_all_btn.pack(side="left", padx=(0, 10))

copy_hashes_btn = ttk.Button(action_frame, text="🔑 Copy Hashes", command=lambda: copy_hash_values("all"))
copy_hashes_btn.pack(side="left", padx=(0, 10))

clear_results_btn = ttk.Button(action_frame, text="🗑️ Clear All", command=clear_all_results)
clear_results_btn.pack(side="left")

# Add accessibility instructions
accessibility_frame = tk.Frame(results_content, bg=BG_MAIN)
accessibility_frame.pack(fill="x", pady=(5, 10))

accessibility_label = tk.Label(accessibility_frame, 
                              text="💡 Table Tips: Double-click any cell to select/copy text | Right-click for quick copy options | Ctrl+C to copy row | Spacebar to toggle selection | Click checkbox to select files",
                              bg=BG_MAIN, fg=TEXT_MUTED, font=("Arial", 9))
accessibility_label.pack(anchor="w")

# Table frame with horizontal scrollbar
table_container = tk.Frame(results_content, bg=BG_MAIN)
table_container.pack(fill="both", expand=True)

# Create frame for treeview and scrollbars
tree_frame = tk.Frame(table_container, bg=BG_MAIN)
tree_frame.pack(fill="both", expand=True)

# Update columns to include source type and path with checkbox
columns = ("Select", "Source", "Filename", "Path", "Size", "File Extension", "MD5", "SHA1", "SHA256")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings", style="Treeview")

# Configure columns with proper widths
tree.heading("Select", text="☐", command=lambda: toggle_select_all())
tree.column("Select", anchor="center", width=60, minwidth=50)

tree.heading("Source", text="Source")
tree.column("Source", anchor="center", width=80, minwidth=60)

tree.heading("Filename", text="Filename")
tree.column("Filename", anchor="w", width=200, minwidth=150)

tree.heading("Path", text="Path")
tree.column("Path", anchor="w", width=250, minwidth=200)

tree.heading("Size", text="Size")
tree.column("Size", anchor="center", width=80, minwidth=60)

tree.heading("File Extension", text="Extension")
tree.column("File Extension", anchor="center", width=100, minwidth=80)

tree.heading("MD5", text="MD5")
tree.column("MD5", anchor="w", width=250, minwidth=200)

tree.heading("SHA1", text="SHA1")
tree.column("SHA1", anchor="w", width=280, minwidth=250)

tree.heading("SHA256", text="SHA256")
tree.column("SHA256", anchor="w", width=350, minwidth=300)

# Pack treeview
tree.pack(side="left", fill="both", expand=True)

# Vertical scrollbar
v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=v_scrollbar.set)
v_scrollbar.pack(side="right", fill="y")

# Horizontal scrollbar
h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=tree.xview)
tree.configure(xscrollcommand=h_scrollbar.set)
h_scrollbar.pack(side="bottom", fill="x")

# Add right-click context menu for copying AND VirusTotal checking
def show_context_menu(event):
    # Get the item that was right-clicked
    item = tree.identify_row(event.y)
    if item:
        tree.selection_set(item)  # Select the item
    
    # Get the column that was clicked
    column = tree.identify_column(event.x)
    
    context_menu = tk.Menu(root, tearoff=0, bg=BG_SURFACE, fg=TEXT_PRIMARY, 
                          activebackground=BG_LIGHTER, activeforeground=TEXT_PRIMARY)
    
    # Add cell-specific copy options
    if item and column:
        column_index = int(column.replace('#', '')) - 1
        column_names = ["Select", "Source", "Filename", "Path", "Size", "Extension", "MD5", "SHA1", "SHA256"]
        if 0 <= column_index < len(column_names):
            column_name = column_names[column_index]
            context_menu.add_command(label=f"📋 Copy {column_name}", command=lambda: copy_specific_cell(item, column_index))
            context_menu.add_separator()
    
    # Hash-specific copy options
    if item:
        hash_menu = tk.Menu(context_menu, tearoff=0, bg=BG_SURFACE, fg=TEXT_PRIMARY)
        hash_menu.add_command(label="📋 Copy MD5", command=lambda: copy_hash_values("md5"))
        hash_menu.add_command(label="📋 Copy SHA1", command=lambda: copy_hash_values("sha1"))
        hash_menu.add_command(label="📋 Copy SHA256", command=lambda: copy_hash_values("sha256"))
        hash_menu.add_command(label="📋 Copy All Hashes", command=lambda: copy_hash_values("all"))
        context_menu.add_cascade(label="🔑 Copy Hashes", menu=hash_menu)
        context_menu.add_separator()
    
    context_menu.add_command(label="📋 Copy Selected Row", command=copy_selected_row)
    context_menu.add_separator()
    context_menu.add_command(label="🔍 Check with VirusTotal", command=lambda: quick_vt_check())
    context_menu.add_separator()
    context_menu.add_command(label="📋 Copy All Results", command=copy_all_results)
    try:
        context_menu.tk_popup(event.x_root, event.y_root)
    finally:
        context_menu.grab_release()

def copy_specific_cell(item, column_index):
    """Copy a specific cell value"""
    try:
        item_data = tree.item(item)
        values = item_data['values']
        if 0 <= column_index < len(values):
            cell_value = str(values[column_index])
            root.clipboard_clear()
            root.clipboard_append(cell_value)
            
            column_names = ["Select", "Source", "Filename", "Path", "Size", "Extension", "MD5", "SHA1", "SHA256"]
            column_name = column_names[column_index] if column_index < len(column_names) else f"Column {column_index + 1}"
            messagebox.showinfo("Copied", f"{column_name} copied to clipboard!\n\nValue: {cell_value[:100]}{'...' if len(cell_value) > 100 else ''}")
        else:
            messagebox.showwarning("Error", "Invalid column selected.")
    except Exception as e:
        messagebox.showerror("Copy Error", f"Failed to copy cell: {str(e)}")

def copy_hash_values(hash_type="all"):
    """Copy hash values from selected row"""
    selection = tree.selection()
    if not selection:
        messagebox.showwarning("No Selection", "Please select a row first.")
        return
    
    item = tree.item(selection[0])
    values = item['values']
    
    if len(values) >= 9:
        md5_hash = values[6]    # MD5 at index 6
        sha1_hash = values[7]   # SHA1 at index 7
        sha256_hash = values[8] # SHA256 at index 8
        
        if hash_type == "md5":
            root.clipboard_clear()
            root.clipboard_append(md5_hash)
            messagebox.showinfo("Copied", f"MD5 Hash copied:\n{md5_hash}")
        elif hash_type == "sha1":
            root.clipboard_clear()
            root.clipboard_append(sha1_hash)
            messagebox.showinfo("Copied", f"SHA1 Hash copied:\n{sha1_hash}")
        elif hash_type == "sha256":
            root.clipboard_clear()
            root.clipboard_append(sha256_hash)
            messagebox.showinfo("Copied", f"SHA256 Hash copied:\n{sha256_hash}")
        elif hash_type == "all":
            all_hashes = f"MD5: {md5_hash}\nSHA1: {sha1_hash}\nSHA256: {sha256_hash}"
            root.clipboard_clear()
            root.clipboard_append(all_hashes)
            messagebox.showinfo("Copied", "All hashes copied to clipboard!")
    else:
        messagebox.showwarning("Invalid Data", "Selected row doesn't contain hash data.")

def quick_vt_check():
    """Quick VirusTotal check for selected row"""
    if not vt_api_key:
        messagebox.showwarning("API Key Required", "Please set your VirusTotal API key first.")
        set_vt_api_key()
        return
    
    selection = tree.selection()
    if not selection:
        messagebox.showwarning("No Selection", "Please select a row to check with VirusTotal.")
        return
    
    item = selection[0]
    item_data = tree.item(item)
    values = item_data['values']
    
    if len(values) >= 8:
        filename = values[1]
        md5_hash = values[5]
        sha1_hash = values[6] 
        sha256_hash = values[7]
        
        # Prefer SHA256, then SHA1, then MD5
        hash_to_use = sha256_hash if sha256_hash and sha256_hash != "Error" else \
                     sha1_hash if sha1_hash and sha1_hash != "Error" else \
                     md5_hash if md5_hash and md5_hash != "Error" else None
        
        if hash_to_use:
            # Show immediate feedback
            messagebox.showinfo("Checking VirusTotal", f"Checking {filename} with VirusTotal...\nThis may take a few seconds.")
            
            def vt_check_thread():
                try:
                    response = check_hash_with_vt(hash_to_use)
                    
                    def show_result():
                        if response and 'data' in response:
                            data = response['data']
                            attributes = data.get('attributes', {})
                            stats = attributes.get('last_analysis_stats', {})
                            
                            malicious = stats.get('malicious', 0)
                            suspicious = stats.get('suspicious', 0)
                            harmless = stats.get('harmless', 0)
                            undetected = stats.get('undetected', 0)
                            
                            # Determine status
                            if malicious > 0:
                                status = f"🚨 MALICIOUS"
                                details = f"❌ {malicious} engines detected this file as malicious!"
                                msg_type = "error"
                            elif suspicious > 0:
                                status = f"⚠️ SUSPICIOUS"
                                details = f"⚠️ {suspicious} engines flagged this file as suspicious."
                                msg_type = "warning"
                            else:
                                status = f"✅ CLEAN"
                                details = f"✅ File appears clean ({harmless + undetected} engines checked)."
                                msg_type = "info"
                            
                            scan_date = attributes.get('last_analysis_date', 0)
                            scan_date_str = datetime.fromtimestamp(scan_date).strftime("%Y-%m-%d %H:%M") if scan_date else "Unknown"
                            
                            result_text = f"""
VirusTotal Result for: {filename}
{'-' * 50}

Status: {status}
{details}

Detection Statistics:
• Malicious: {malicious}
• Suspicious: {suspicious}
• Harmless: {harmless}
• Undetected: {undetected}

Last Scan: {scan_date_str}
Hash: {hash_to_use}
"""
                            
                            if msg_type == "error":
                                messagebox.showerror("VirusTotal Result", result_text)
                            elif msg_type == "warning":
                                messagebox.showwarning("VirusTotal Result", result_text)
                            else:
                                messagebox.showinfo("VirusTotal Result", result_text)
                        
                        elif response and 'error' in response:
                            if "not found" in response['error'].lower():
                                messagebox.showinfo("VirusTotal Result", 
                                                   f"File not found in VirusTotal database.\n\nThis could mean:\n• The file is new/rare\n• The file hasn't been submitted to VT\n• The hash might be incorrect\n\nFilename: {filename}\nHash: {hash_to_use}")
                            else:
                                messagebox.showerror("VirusTotal Error", f"Error checking file:\n{response['error']}")
                        else:
                            messagebox.showerror("VirusTotal Error", "Unknown error occurred while checking the file.")
                    
                    root.after(0, show_result)
                    
                except Exception as e:
                    def show_error():
                        messagebox.showerror("VirusTotal Error", f"Error checking file:\n{str(e)}")
                    root.after(0, show_error)
            
            # Start the check in background
            threading.Thread(target=vt_check_thread, daemon=True).start()
        else:
            messagebox.showwarning("No Valid Hash", "No valid hash found for this file.")
    else:
        messagebox.showwarning("Invalid Data", "Selected row doesn't contain valid file data.")

tree.bind("<Button-3>", show_context_menu)  # Right-click
tree.bind("<Button-1>", on_tree_click)  # Left-click for checkbox selection
# tree.bind("<Double-1>", on_tree_double_click)  # Double-click for text selection - temporarily disabled

# Add keyboard shortcuts for better accessibility
def on_key_press(event):
    """Handle keyboard shortcuts in the results table"""
    if event.keysym == "c" and (event.state & 0x4):  # Ctrl+C
        copy_selected_row()
    elif event.keysym == "a" and (event.state & 0x4):  # Ctrl+A
        toggle_select_all()
    elif event.keysym == "space":  # Spacebar to toggle selection
        selection = tree.selection()
        if selection:
            item = selection[0]
            item_values = tree.item(item)['values']
            if len(item_values) >= 4:
                file_path = item_values[3]
                toggle_file_selection(file_path)
    elif event.keysym == "Return":  # Enter key to open selection dialog
        on_tree_double_click(event)

def on_tree_double_click(event):
    """Handle double-click to open text selection dialog"""
    item = tree.identify_row(event.y)
    if item:
        column = tree.identify_column(event.x)
        if column:
            column_index = int(column.replace('#', '')) - 1
            open_text_selection_dialog(item, column_index)

def open_text_selection_dialog(item, column_index):
    """Open a dialog with selectable text for the clicked cell"""
    try:
        item_data = tree.item(item)
        values = item_data['values']
        if 0 <= column_index < len(values):
            cell_value = str(values[column_index])
            column_names = ["Select", "Source", "Filename", "Path", "Size", "Extension", "MD5", "SHA1", "SHA256"]
            column_name = column_names[column_index] if column_index < len(column_names) else f"Column {column_index + 1}"
            
            # Create selection dialog
            selection_dialog = tk.Toplevel(root)
            selection_dialog.title(f"Select Text - {column_name}")
            selection_dialog.geometry("600x400")
            selection_dialog.configure(bg=BG_MAIN)
            selection_dialog.transient(root)
            selection_dialog.grab_set()
            
            # Center the dialog
            selection_dialog.geometry("+%d+%d" % (root.winfo_rootx() + 50, root.winfo_rooty() + 50))
            
            # Header
            header_frame = tk.Frame(selection_dialog, bg=BG_MAIN)
            header_frame.pack(fill="x", padx=20, pady=(20, 10))
            
            tk.Label(header_frame, text=f"📋 {column_name}", 
                    bg=BG_MAIN, fg=TEXT_PRIMARY, font=("Arial", 14, "bold")).pack(anchor="w")
            
            tk.Label(header_frame, text="Select and copy the text below:", 
                    bg=BG_MAIN, fg=TEXT_MUTED, font=("Arial", 10)).pack(anchor="w", pady=(5, 0))
            
            # Text area with selectable content
            text_frame = tk.Frame(selection_dialog, bg=BG_MAIN)
            text_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            text_widget = tk.Text(text_frame, bg=BG_SURFACE, fg=TEXT_PRIMARY, 
                                font=("Consolas", 11), wrap="word", height=10,
                                selectbackground=ACCENT_BLUE, selectforeground="white")
            
            # Add scrollbar
            text_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=text_scrollbar.set)
            
            text_widget.pack(side="left", fill="both", expand=True)
            text_scrollbar.pack(side="right", fill="y")
            
            # Insert and select all text
            text_widget.insert("1.0", cell_value)
            text_widget.select_range("1.0", "end")
            text_widget.focus_set()
            
            # Buttons
            button_frame = tk.Frame(selection_dialog, bg=BG_MAIN)
            button_frame.pack(fill="x", padx=20, pady=(0, 20))
            
            def copy_and_close():
                try:
                    # Get selected text or all text if nothing selected
                    try:
                        selected_text = text_widget.get("sel.first", "sel.last")
                    except tk.TclError:
                        selected_text = text_widget.get("1.0", "end-1c")
                    
                    root.clipboard_clear()
                    root.clipboard_append(selected_text)
                    selection_dialog.destroy()
                    messagebox.showinfo("Copied", f"Text copied to clipboard!\n\nLength: {len(selected_text)} characters")
                except Exception as e:
                    messagebox.showerror("Copy Error", f"Failed to copy text: {str(e)}")
            
            def select_all():
                text_widget.select_range("1.0", "end")
                text_widget.focus_set()
            
            ttk.Button(button_frame, text="📋 Copy Selected", command=copy_and_close).pack(side="left", padx=(0, 10))
            ttk.Button(button_frame, text="☑️ Select All", command=select_all).pack(side="left", padx=(0, 10))
            ttk.Button(button_frame, text="❌ Close", command=selection_dialog.destroy).pack(side="left")
            
            # Keyboard shortcuts for the dialog
            def on_dialog_key(event):
                if event.keysym == "Escape":
                    selection_dialog.destroy()
                elif event.keysym == "c" and (event.state & 0x4):  # Ctrl+C
                    copy_and_close()
                elif event.keysym == "a" and (event.state & 0x4):  # Ctrl+A
                    select_all()
                    return "break"  # Prevent default behavior
            
            selection_dialog.bind("<KeyPress>", on_dialog_key)
            text_widget.bind("<KeyPress>", on_dialog_key)
        
    except Exception as e:
        messagebox.showerror("Selection Error", f"Failed to open selection dialog: {str(e)}")

tree.bind("<KeyPress>", on_key_press)
tree.focus_set()  # Make tree focusable for keyboard shortcuts

# === VIRUSTOTAL TAB ===
vt_tab = tk.Frame(tabs, bg=BG_MAIN)
tabs.add(vt_tab, text="VirusTotal Scanner")

# VirusTotal tab content
vt_content = tk.Frame(vt_tab, bg=BG_MAIN)
vt_content.pack(fill="both", expand=True, padx=20, pady=20)

# VirusTotal header with control buttons
vt_header_frame = tk.Frame(vt_content, bg=BG_MAIN)
vt_header_frame.pack(fill="x", pady=(0, 10))

vt_header = tk.Label(vt_header_frame, text="VirusTotal File Scanner", bg=BG_MAIN, fg=TEXT_PRIMARY, font=("Arial", 14, "bold"))
vt_header.pack(side="left")

# VirusTotal control buttons
vt_action_frame = tk.Frame(vt_header_frame, bg=BG_MAIN)
vt_action_frame.pack(side="right")

set_api_key_btn = ttk.Button(vt_action_frame, text="� Set API Key", command=set_vt_api_key)
set_api_key_btn.pack(side="left", padx=(0, 10))

select_hashes_btn = ttk.Button(vt_action_frame, text="� Select from Results", command=get_selected_hashes)
select_hashes_btn.pack(side="left", padx=(0, 10))

check_vt_btn = ttk.Button(vt_action_frame, text="� Check with VT", command=check_virustotal)
check_vt_btn.pack(side="left", padx=(0, 10))

clear_vt_btn = ttk.Button(vt_action_frame, text="�️ Clear", command=clear_vt_results)
clear_vt_btn.pack(side="left")

export_vt_btn = ttk.Button(vt_action_frame, text="📊 Export CSV", command=export_vt_results_to_csv)
export_vt_btn.pack(side="left", padx=(10, 0))

# API key status
vt_api_frame = tk.Frame(vt_content, bg=BG_MAIN)
vt_api_frame.pack(fill="x", pady=(0, 5))

vt_api_status_label = tk.Label(vt_api_frame, text="🔑 API Key: Not set", 
                              bg=BG_MAIN, fg=TEXT_MUTED, font=("Arial", 9))
vt_api_status_label.pack(side="left")

# Add quota tracking indicators
vt_quota_frame = tk.Frame(vt_content, bg=BG_MAIN)
vt_quota_frame.pack(fill="x", pady=(0, 5))

vt_daily_quota_label = tk.Label(vt_quota_frame, text="📅 Daily: Loading...", 
                               bg=BG_MAIN, fg=TEXT_MUTED, font=("Arial", 9))
vt_daily_quota_label.pack(side="left", padx=(0, 15))

vt_monthly_quota_label = tk.Label(vt_quota_frame, text="📊 Monthly: Loading...", 
                                 bg=BG_MAIN, fg=TEXT_MUTED, font=("Arial", 9))
vt_monthly_quota_label.pack(side="left")

# Status and progress
vt_status_frame = tk.Frame(vt_content, bg=BG_MAIN)
vt_status_frame.pack(fill="x", pady=(0, 10))

vt_status_label = tk.Label(vt_status_frame, text="📊 No files selected for VirusTotal analysis", 
                          bg=BG_MAIN, fg=TEXT_MUTED, font=("Arial", 10))
vt_status_label.pack(side="left")

# Progress bar for VT checking
vt_progress_frame = tk.Frame(vt_content, bg=BG_MAIN)
vt_progress_frame.pack(fill="x", pady=(0, 10))

vt_progress_var = tk.DoubleVar()
vt_progress = ttk.Progressbar(vt_progress_frame, orient="horizontal", mode="determinate", 
                             variable=vt_progress_var, style="TProgressbar", length=400)
vt_progress.pack(fill="x")

# VirusTotal results table
vt_table_container = tk.Frame(vt_content, bg=BG_MAIN)
vt_table_container.pack(fill="both", expand=True)

# Create frame for VT treeview
vt_tree_frame = tk.Frame(vt_table_container, bg=BG_MAIN)
vt_tree_frame.pack(fill="both", expand=True)

# Configure VT treeview columns for better results display
vt_columns = ("Status", "Hash Type", "Hash", "Malicious", "Suspicious", "Clean", "Last Scan", "Filename")
vt_tree = ttk.Treeview(vt_tree_frame, columns=vt_columns, show="headings", style="Treeview")

# Configure color tags for VT results
vt_tree.tag_configure("clean", background="#50a151")  # Green for clean files
vt_tree.tag_configure("threat", background="#f44336")  # Red for threats

# Configure VT tree headings and columns
vt_tree.heading("Status", text="Status")
vt_tree.column("Status", anchor="center", width=100, minwidth=80)

vt_tree.heading("Hash Type", text="Hash Type")
vt_tree.column("Hash Type", anchor="center", width=80, minwidth=60)

vt_tree.heading("Hash", text="Hash")
vt_tree.column("Hash", anchor="w", width=200, minwidth=150)

vt_tree.heading("Malicious", text="🚨 Malicious")
vt_tree.column("Malicious", anchor="center", width=80, minwidth=60)

vt_tree.heading("Suspicious", text="⚠️ Suspicious")
vt_tree.column("Suspicious", anchor="center", width=80, minwidth=60)

vt_tree.heading("Clean", text="✅ Clean")
vt_tree.column("Clean", anchor="center", width=80, minwidth=60)

vt_tree.heading("Last Scan", text="Last Scan")
vt_tree.column("Last Scan", anchor="center", width=120, minwidth=100)

vt_tree.heading("Filename", text="Filename")
vt_tree.column("Filename", anchor="w", width=200, minwidth=150)

# Pack VT treeview
vt_tree.pack(side="left", fill="both", expand=True)

# VT tree scrollbars
vt_v_scrollbar = ttk.Scrollbar(vt_tree_frame, orient="vertical", command=vt_tree.yview)
vt_tree.configure(yscrollcommand=vt_v_scrollbar.set)
vt_v_scrollbar.pack(side="right", fill="y")

vt_h_scrollbar = ttk.Scrollbar(vt_table_container, orient="horizontal", command=vt_tree.xview)
vt_tree.configure(xscrollcommand=vt_h_scrollbar.set)
vt_h_scrollbar.pack(side="bottom", fill="x")

# Add right-click context menu for VT results
def show_vt_context_menu(event):
    # Get the item that was right-clicked
    item = vt_tree.identify_row(event.y)
    if item:
        vt_tree.selection_set(item)  # Select the item
    
    # Get the column that was clicked
    column = vt_tree.identify_column(event.x)
    
    vt_context_menu = tk.Menu(root, tearoff=0, bg=BG_SURFACE, fg=TEXT_PRIMARY, 
                          activebackground=BG_LIGHTER, activeforeground=TEXT_PRIMARY)
    
    # Add cell-specific copy options for VT results
    if item and column:
        column_index = int(column.replace('#', '')) - 1
        vt_column_names = ["Status", "Hash Type", "Hash", "Malicious", "Suspicious", "Clean", "Last Scan", "Filename"]
        if 0 <= column_index < len(vt_column_names):
            column_name = vt_column_names[column_index]
            vt_context_menu.add_command(label=f"📋 Copy {column_name}", command=lambda: copy_vt_specific_cell(item, column_index))
            vt_context_menu.add_separator()
    
    vt_context_menu.add_command(label="📋 Copy Selected Row", command=copy_vt_selected_row)
    vt_context_menu.add_separator()
    vt_context_menu.add_command(label="📄 Copy Hash", command=copy_vt_hash)
    vt_context_menu.add_command(label="📋 Copy Filename", command=copy_vt_filename)
    vt_context_menu.add_separator()
    vt_context_menu.add_command(label="📋 Copy All VT Results", command=copy_all_vt_results)
    try:
        vt_context_menu.tk_popup(event.x_root, event.y_root)
    finally:
        vt_context_menu.grab_release()

def copy_vt_specific_cell(item, column_index):
    """Copy a specific cell value from VT results"""
    try:
        item_data = vt_tree.item(item)
        values = item_data['values']
        if 0 <= column_index < len(values):
            cell_value = str(values[column_index])
            root.clipboard_clear()
            root.clipboard_append(cell_value)
            
            vt_column_names = ["Status", "Hash Type", "Hash", "Malicious", "Suspicious", "Clean", "Last Scan", "Filename"]
            column_name = vt_column_names[column_index] if column_index < len(vt_column_names) else f"Column {column_index + 1}"
            messagebox.showinfo("Copied", f"{column_name} copied to clipboard!\n\nValue: {cell_value}")
        else:
            messagebox.showwarning("Error", "Invalid column selected.")
    except Exception as e:
        messagebox.showerror("Copy Error", f"Failed to copy cell: {str(e)}")

def copy_vt_selected_row():
    """Copy selected VT result row"""
    selection = vt_tree.selection()
    if selection:
        item = vt_tree.item(selection[0])
        values = item['values']
        if values:
            # Format: Status | Hash Type | Hash | Malicious | Suspicious | Clean | Last Scan | Filename
            copy_text = f"{values[0]}\t{values[1]}\t{values[2]}\t{values[3]}\t{values[4]}\t{values[5]}\t{values[6]}\t{values[7]}"
            root.clipboard_clear()
            root.clipboard_append(copy_text)
            messagebox.showinfo("Copied", "Selected VirusTotal result copied to clipboard!")
    else:
        messagebox.showwarning("No Selection", "Please select a row to copy.")

def copy_vt_hash():
    """Copy hash from selected VT result"""
    selection = vt_tree.selection()
    if selection:
        item = vt_tree.item(selection[0])
        values = item['values']
        if values and len(values) > 2:
            hash_value = values[2].replace("...", "")  # Remove "..." if present
            root.clipboard_clear()
            root.clipboard_append(hash_value)
            messagebox.showinfo("Copied", "Hash copied to clipboard!")
    else:
        messagebox.showwarning("No Selection", "Please select a row to copy hash.")

def copy_vt_filename():
    """Copy filename from selected VT result"""
    selection = vt_tree.selection()
    if selection:
        item = vt_tree.item(selection[0])
        values = item['values']
        if values and len(values) > 7:
            filename = values[7]
            root.clipboard_clear()
            root.clipboard_append(filename)
            messagebox.showinfo("Copied", "Filename copied to clipboard!")
    else:
        messagebox.showwarning("No Selection", "Please select a row to copy filename.")

def copy_all_vt_results():
    """Copy all VT results"""
    if vt_tree.get_children():
        all_data = []
        # Add header
        all_data.append("Status\tHash Type\tHash\tMalicious\tSuspicious\tClean\tLast Scan\tFilename")
        # Add all rows
        for child in vt_tree.get_children():
            item = vt_tree.item(child)
            values = item['values']
            all_data.append(f"{values[0]}\t{values[1]}\t{values[2]}\t{values[3]}\t{values[4]}\t{values[5]}\t{values[6]}\t{values[7]}")
        
        copy_text = "\n".join(all_data)
        root.clipboard_clear()
        root.clipboard_append(copy_text)
        messagebox.showinfo("Copied", f"All {len(all_data)-1} VirusTotal results copied to clipboard!")
    else:
        messagebox.showwarning("No Data", "No VirusTotal results to copy.")

vt_tree.bind("<Button-3>", show_vt_context_menu)  # Right-click
# vt_tree.bind("<Double-1>", on_vt_tree_double_click)  # Double-click for text selection - temporarily disabled

# Add keyboard shortcuts for VT table
def on_vt_key_press(event):
    """Handle keyboard shortcuts in the VT results table"""
    if event.keysym == "c" and (event.state & 0x4):  # Ctrl+C
        copy_vt_selected_row()
    elif event.keysym == "Return":  # Enter key to open selection dialog
        on_vt_tree_double_click(event)

def on_vt_tree_double_click(event):
    """Handle double-click to open text selection dialog for VT results"""
    item = vt_tree.identify_row(event.y)
    if item:
        column = vt_tree.identify_column(event.x)
        if column:
            column_index = int(column.replace('#', '')) - 1
            open_vt_text_selection_dialog(item, column_index)

def open_vt_text_selection_dialog(item, column_index):
    """Open a dialog with selectable text for the clicked VT cell"""
    try:
        item_data = vt_tree.item(item)
        values = item_data['values']
        if 0 <= column_index < len(values):
            cell_value = str(values[column_index])
            vt_column_names = ["Status", "Hash Type", "Hash", "Malicious", "Suspicious", "Clean", "Last Scan", "Filename"]
            column_name = vt_column_names[column_index] if column_index < len(vt_column_names) else f"Column {column_index + 1}"
            
            # Create selection dialog
            selection_dialog = tk.Toplevel(root)
            selection_dialog.title(f"Select Text - {column_name}")
            selection_dialog.geometry("600x400")
            selection_dialog.configure(bg=BG_MAIN)
            selection_dialog.transient(root)
            selection_dialog.grab_set()
            
            # Center the dialog
            selection_dialog.geometry("+%d+%d" % (root.winfo_rootx() + 50, root.winfo_rooty() + 50))
            
            # Header
            header_frame = tk.Frame(selection_dialog, bg=BG_MAIN)
            header_frame.pack(fill="x", padx=20, pady=(20, 10))
            
            tk.Label(header_frame, text=f"🔍 {column_name}", 
                    bg=BG_MAIN, fg=TEXT_PRIMARY, font=("Arial", 14, "bold")).pack(anchor="w")
            
            tk.Label(header_frame, text="Select and copy the text below:", 
                    bg=BG_MAIN, fg=TEXT_MUTED, font=("Arial", 10)).pack(anchor="w", pady=(5, 0))
            
            # Text area with selectable content
            text_frame = tk.Frame(selection_dialog, bg=BG_MAIN)
            text_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            text_widget = tk.Text(text_frame, bg=BG_SURFACE, fg=TEXT_PRIMARY, 
                                font=("Consolas", 11), wrap="word", height=10,
                                selectbackground=ACCENT_BLUE, selectforeground="white")
            
            # Add scrollbar
            text_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=text_scrollbar.set)
            
            text_widget.pack(side="left", fill="both", expand=True)
            text_scrollbar.pack(side="right", fill="y")
            
            # Insert and select all text
            text_widget.insert("1.0", cell_value)
            text_widget.select_range("1.0", "end")
            text_widget.focus_set()
            
            # Buttons
            button_frame = tk.Frame(selection_dialog, bg=BG_MAIN)
            button_frame.pack(fill="x", padx=20, pady=(0, 20))
            
            def copy_and_close():
                try:
                    # Get selected text or all text if nothing selected
                    try:
                        selected_text = text_widget.get("sel.first", "sel.last")
                    except tk.TclError:
                        selected_text = text_widget.get("1.0", "end-1c")
                    
                    root.clipboard_clear()
                    root.clipboard_append(selected_text)
                    selection_dialog.destroy()
                    messagebox.showinfo("Copied", f"Text copied to clipboard!\n\nLength: {len(selected_text)} characters")
                except Exception as e:
                    messagebox.showerror("Copy Error", f"Failed to copy text: {str(e)}")
            
            def select_all():
                text_widget.select_range("1.0", "end")
                text_widget.focus_set()
            
            ttk.Button(button_frame, text="📋 Copy Selected", command=copy_and_close).pack(side="left", padx=(0, 10))
            ttk.Button(button_frame, text="☑️ Select All", command=select_all).pack(side="left", padx=(0, 10))
            ttk.Button(button_frame, text="❌ Close", command=selection_dialog.destroy).pack(side="left")
            
            # Keyboard shortcuts for the dialog
            def on_dialog_key(event):
                if event.keysym == "Escape":
                    selection_dialog.destroy()
                elif event.keysym == "c" and (event.state & 0x4):  # Ctrl+C
                    copy_and_close()
                elif event.keysym == "a" and (event.state & 0x4):  # Ctrl+A
                    select_all()
                    return "break"  # Prevent default behavior
            
            selection_dialog.bind("<KeyPress>", on_dialog_key)
            text_widget.bind("<KeyPress>", on_dialog_key)
        
    except Exception as e:
        messagebox.showerror("Selection Error", f"Failed to open selection dialog: {str(e)}")

vt_tree.bind("<KeyPress>", on_vt_key_press)
vt_tree.focus_set()  # Make VT tree focusable for keyboard shortcuts

# VT action buttons at bottom
vt_bottom_frame = tk.Frame(vt_content, bg=BG_MAIN)
vt_bottom_frame.pack(fill="x", pady=(10, 0))

view_details_btn = ttk.Button(vt_bottom_frame, text="👁️ View Details", command=view_vt_details)
view_details_btn.pack(side="left", padx=(0, 10))

export_vt_report_btn = ttk.Button(vt_bottom_frame, text="📄 Export Report", command=export_vt_report)
export_vt_report_btn.pack(side="left")

# Info panel for VirusTotal
vt_info_frame = tk.Frame(vt_content, bg=BG_MAIN)
vt_info_frame.pack(fill="x", pady=(10, 0))

vt_info_label = tk.Label(vt_info_frame, 
                        text="💡 Instructions: 1) Select files in Results tab using checkboxes 2) Click 'Move to VT' 3) Set API key 4) Click 'Check with VT' 5) View detailed results below",
                        bg=BG_MAIN, fg=TEXT_MUTED, font=("Arial", 9))
vt_info_label.pack()

# Make drop area clickable
def on_drop_area_click(event):
    browse_files_for_hash()

def handle_drag_drop(file_paths):
    """Handle drag and drop files"""
    if file_paths:
        # Store files for later processing instead of immediately processing
        start_processing.pending_files = list(file_paths)
        status_var.set(f"[FILES] Dropped {len(file_paths)} files - Ready to process")
        selection_status_label.config(text=f"FILES: {len(file_paths)} files dropped", fg=ACCENT_GREEN)
        drop_label.config(text=f"{len(file_paths)} files dropped - Other input methods disabled", fg=ACCENT_GREEN)
        # Enable Start Processing button
        start_processing_btn.config(state="normal")
        # Clear any folder selection and disable other input methods
        if selected_folder.get():
            selected_folder.set("")
        # Disable other input methods
        browse_button.config(state="disabled")
        browse_files_btn.config(state="disabled")

drop_label.bind("<Button-1>", on_drop_area_click)
drop_frame.bind("<Button-1>", on_drop_area_click)

# Initialize quota display
update_quota_display()

# Initialize API key from storage
vt_api_key = load_api_key()
if vt_api_key:
    # Update the API status label to show key is loaded
    vt_api_status_label.config(text=f"API Key: {'*' * (len(vt_api_key) - 8) + vt_api_key[-8:] if len(vt_api_key) > 8 else '*' * len(vt_api_key)}")

# Start GUI
root.mainloop()
