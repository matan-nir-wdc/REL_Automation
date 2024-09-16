import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
import auto_fa as AUTO_FA
import project as PRJ


def print_to_text(text_widget, message):
    text_widget.insert(tk.END, message + '\n')
    text_widget.see(tk.END)  # Ensure the text widget scrolls to the end


class ConsoleRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert('end', message)  # Insert at the end
        self.text_widget.see('end')  # Ensure it is visible at the end

    def flush(self):
        pass  # This method is needed for file-like objects


def only_one_not_none(*args):
    # Count how many values are not None
    count_not_none = sum(arg is not None for arg in args)
    # Check if exactly one value is not None
    return count_not_none == 1


def select_folder(entry_widget):
    folder_path = filedialog.askdirectory()
    if folder_path:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, folder_path)


def submit():
    folder1_path = folder1_entry.get()
    folder2_path = folder2_entry.get()
    folder3_path = folder3_entry.get()
    amount = amount_entry.get()
    project = dropdown_var.get()
    check_not_none = [folder1_path, folder2_path, folder3_path]
    if not folder1_path and not folder2_path and not folder3_path:
        messagebox.showwarning("Input Error", "Please fill in one path")
        return
    if not only_one_not_none(check_not_none):
        messagebox.showwarning("Input Error", "Only ONE option can be choosen")
        return

    try:
        amount = int(amount)
        if amount < 1:
            raise ValueError()
    except ValueError:
        messagebox.showwarning("Input Error", "Amount must be a number bigger than 0")
        return


    print(f"Folder 1: {folder1_path}")
    print(f"Folder 2: {folder2_path}")
    print(f"Folder 3: {folder3_path}")
    print(f"Amount: {amount}")
    print(f"Dropdown option: {project}")
    print("-" * 40)
    if folder1_path:
        sys.stdout = ConsoleRedirector(console_output_text)
        current_project = PRJ.choose(project)
        # test_flow(path=path, project=project)
        vtf_data = AUTO_FA.vtf_info(folder1_path)
        AUTO_FA.ctf_log_error(folder1_path, True, vtf_data)
        sres = AUTO_FA.smartReport(folder1_path, project_json=current_project.smartReport)
        AUTO_FA.pdl_report(folder1_path)
        AUTO_FA.protocol_log_info(folder1_path, vtf_data)
        AUTO_FA.emonitor_actions(folder1_path, amount, sres)
        #FH.remove_quotes_from_file(folder1_path)

        AUTO_FA.run_auto_fa(rwr_amount=amount, path=folder1_path, project=prj)


# Create the main window
root = tk.Tk()
root.title("REL Auto FA")

# Create and place widgets for folder paths
tk.Label(root, text="Single folder run:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
folder1_entry = tk.Entry(root, width=50)
folder1_entry.grid(row=0, column=1, padx=5, pady=5)
folder1_button = tk.Button(root, text="Browse", command=lambda: select_folder(folder1_entry))
folder1_button.grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="FW Folder run:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
folder2_entry = tk.Entry(root, width=50)
folder2_entry.grid(row=1, column=1, padx=5, pady=5)
folder2_button = tk.Button(root, text="Browse", command=lambda: select_folder(folder2_entry))
folder2_button.grid(row=1, column=2, padx=5, pady=5)

tk.Label(root, text="Zip folder run:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
folder3_entry = tk.Entry(root, width=50)
folder3_entry.grid(row=2, column=1, padx=5, pady=5)
folder3_button = tk.Button(root, text="Browse", command=lambda: select_folder(folder3_entry))
folder3_button.grid(row=2, column=2, padx=5, pady=5)

# Create and place widget for amount input
tk.Label(root, text="Amount:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
amount_entry = tk.Entry(root, width=20)
amount_entry.insert(0, "2")
amount_entry.grid(row=3, column=1, padx=5, pady=5)

# Create and place widget for dropdown option
tk.Label(root, text="Options:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
dropdown_var = tk.StringVar(root)
options = ["OBERON", "SPA"]
dropdown_menu = ttk.OptionMenu(root, dropdown_var, options[0], *options)
dropdown_menu.grid(row=4, column=1, padx=5, pady=5)

# Create and place submit button
submit_button = tk.Button(root, text="Submit", command=submit)
submit_button.grid(row=5, column=1, pady=10)

# Create Text widget to display console output
console_output_text = tk.Text(root, wrap='word', height=20, width=80)
console_output_text.grid(row=6, columnspan=3, padx=5, pady=5)

# Start the main event loop
root.mainloop()
