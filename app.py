import csv
import tkinter as tk
from functools import lru_cache
from os.path import normpath
from pprint import pprint
from tkinter.filedialog import asksaveasfilename

import customtkinter as ctk
import pynetbox
from tksheet import Sheet

# Basic parameters and initializations
# Supported modes : Light, Dark, System
ctk.set_appearance_mode("System")

# Supported themes : green, dark-blue, blue
ctk.set_default_color_theme("blue")

appWidth, appHeight = 1400, 420

# Scrollable frame class
class TableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)


# App Class
class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("CI Downloader")
        self.geometry(f"{appWidth}x{appHeight}")

        # init variables
        self.tenant_group_id = 0
        self.tenant_id = 0
        self.region_id = 0
        self.site_id = 0
        self.status = "all"
        header = [
            "Name",
            "Status",
            "Model/Type",
            "Mgmt IP",
            "Tenant",
            "Site",
            "Region",
            "Serial",
            "Primary Device",
        ]
        self.status_values = {
            "All": "all",
            "Active": "active",
            "Offline": "offline"
        }

        # create sidebar frame with widgets
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=5)
        self.sidebar_frame.grid(
            row=0, column=0, rowspan=10, padx=(10, 0), pady=(10, 0), sticky="nsew"
        )
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # create table frame
        self.table_frame = ctk.CTkFrame(self, width=800, corner_radius=5)
        self.table_frame.grid(
            row=3, column=1, columnspan=10, rowspan=20, padx=20, pady=20, sticky="nsew"
        )
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame_switches = []

        # URL Label
        self.url_label = ctk.CTkLabel(self, text="URL")
        self.url_label.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        # URL Entry Field
        self.url_entry = ctk.CTkEntry(
            self,
            placeholder_text="https://demo.netbox.dev/",
        )
        self.url_entry.grid(row=0, column=2, columnspan=4, padx=5, pady=5, sticky="ew")

        # Token Label
        self.token_label = ctk.CTkLabel(self, text="Token")
        self.token_label.grid(row=1, column=1, padx=5, pady=5, sticky="e")

        # Token Entry Field
        self.token_entry = ctk.CTkEntry(
            self, placeholder_text="b353f1efdc128974423ec7dbf4e75460923de9f8"
        )
        self.token_entry.grid(
            row=1, column=2, columnspan=4, padx=5, pady=5, sticky="ew"
        )

        # Connect Button
        self.connect_to_server_button = ctk.CTkButton(
            self.sidebar_frame, text="Connect to Server", command=self.connect_to_server
        )
        self.connect_to_server_button.grid(
            row=0, column=0, columnspan=1, padx=5, pady=5, sticky="ew"
        )

        # Load data Button
        self.load_data_button = ctk.CTkButton(
            self.sidebar_frame, text="Load Data", command=self.load_data
        )
        self.load_data_button.grid(
            row=11, column=0, columnspan=1, padx=5, pady=5, sticky="ew"
        )
        self.load_data_button.configure(state="disabled")

        # Save data Button
        self.save_data_button = ctk.CTkButton(
            self.sidebar_frame, text="Save Data", command=self.save_sheet
        )
        self.save_data_button.grid(
            row=12, column=0, columnspan=1, padx=5, pady=5, sticky="ew"
        )
        self.save_data_button.configure(state="disabled")

        # Device Checkbox
        self.checkbox_device_var = tk.StringVar()
        self.checkbox_device_var.set("on")
        self.checkbox_device = ctk.CTkCheckBox(master=self.sidebar_frame, text="Devices", variable=self.checkbox_device_var, onvalue="on", offvalue="off")
        self.checkbox_device.grid(row=8, column=0, pady=(5, 0), padx=5, sticky="wn")

        # Context Checkbox
        self.checkbox_context_var = tk.StringVar()
        self.checkbox_context_var.set("on")
        self.checkbox_context = ctk.CTkCheckBox(master=self.sidebar_frame, text="Context", variable=self.checkbox_context_var, onvalue="on", offvalue="off")
        self.checkbox_context.grid(row=9, column=0, pady=(5, 0), padx=5, sticky="wn")

        # Virtual-Machine Checkbox
        self.checkbox_vm_var = tk.StringVar()
        self.checkbox_vm_var.set("on")
        self.checkbox_vm = ctk.CTkCheckBox(master=self.sidebar_frame, text="Virtual-Machine", variable=self.checkbox_vm_var, onvalue="on", offvalue="off")
        self.checkbox_vm.grid(row=10, column=0, pady=(5, 0), padx=5, sticky="wn")

        # Tenant Group Drowndown
        self.tenant_group_option_menu_var = ctk.StringVar(value="Tenant Group")
        self.tenant_group_option_menu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=[],
            command=self.tenant_groups_dropdown_callback,
            variable=self.tenant_group_option_menu_var,
            anchor=ctk.CENTER
        )
        self.tenant_group_option_menu.grid(
            row=3, column=0, columnspan=1, padx=5, pady=5, sticky="new"
        )
        self.tenant_group_option_menu.configure(state="disabled")

        # Tenant Dropdown
        self.tenant_option_menu_var = ctk.StringVar(value="Tenant")
        self.tenant_option_menu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=[],
            command=self.tenants_dropdown_callback,
            variable=self.tenant_option_menu_var,
            anchor=ctk.CENTER
        )
        self.tenant_option_menu.grid(
            row=4, column=0, columnspan=1, padx=5, pady=5, sticky="ew"
        )
        self.tenant_option_menu.configure(state="disabled")

        # Region Dropdown
        self.region_option_menu_var = ctk.StringVar(value="Region")
        self.region_option_menu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=[],
            command=self.region_dropdown_callback,
            variable=self.region_option_menu_var,
            anchor=ctk.CENTER
        )
        self.region_option_menu.grid(
            row=5, column=0, columnspan=1, padx=5, pady=5, sticky="ew"
        )
        self.region_option_menu.configure(state="disabled")

        # Site Dropdown
        self.site_option_menu_var = ctk.StringVar(value="Site")
        self.site_option_menu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=[],
            command=self.site_dropdown_callback,
            variable=self.site_option_menu_var,
            anchor=ctk.CENTER
        )
        self.site_option_menu.grid(
            row=6, column=0, columnspan=1, padx=5, pady=5, sticky="ew"
        )
        self.site_option_menu.configure(state="disabled")

        # Status Dropdown
        self.status_option_menu_var = ctk.StringVar(value="Status")
        self.status_option_menu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=list(self.status_values.keys()),
            command=self.status_dropdown_callback,
            variable=self.status_option_menu_var,
            anchor=ctk.CENTER
        )
        self.status_option_menu.grid(
            row=7, column=0, columnspan=1, padx=5, pady=5, sticky="ew"
        )
        self.status_option_menu.configure(state="disabled")

        # Data Sheet
        self.sheet = Sheet(
            self.table_frame, default_column_width=150, show_row_index=True, data=[[]]
        )
        self.sheet.grid(row=3, column=2, sticky="nswe")
        self.sheet.set_header_data(value=header)
        self.sheet.headers(show_headers_if_not_sheet=True)
        self.sheet.height_and_width(height=300, width=1200)

        # create a span which encompasses the table, header and index
        # all data values, no displayed values
        self.sheet_span = self.sheet.span(
            header=True,
            index=True,
            hdisp=False,
            idisp=False,
        )


    def connect_to_server(self):
        if (url := self.url_entry.get()) and (token := self.token_entry.get()):
            try:
                self.nb = pynetbox.api(url, token=token)
                self.nb.http_session.verify = False
                tenant_group_rs = self.nb.tenancy.tenant_groups.all()
                self.tenant_groups = {
                    tenant_group.name: tenant_group.id
                    for tenant_group in tenant_group_rs
                }
                tenant_groups = list(self.tenant_groups.keys())
                region_rs = self.nb.dcim.regions.all()
                self.regions = {region.name: region.id for region in region_rs}
                self.regions["all"] = 0
                regions = list(self.regions.keys())
                self.tenant_group_option_menu.configure(
                    values=tenant_groups, state="normal"
                )
                self.region_option_menu.configure(values=regions, state="normal")
                self.status_option_menu.configure(state="normal")

            except Exception as e:
                tk.messagebox.showerror("Python Error", message=e)
        else:
            tk.messagebox.showerror(
                "Python Error",
                "Error: You need to enter the URL and Token to conect to the server!",
            )

    def tenant_groups_dropdown_callback(self, choice):
        self.tenant_group_id = self.tenant_groups[choice]
        tenant_rs = self.nb.tenancy.tenants.filter(tenant_group_id=self.tenant_group_id)
        self.tenants = {tenant.name: tenant.id for tenant in tenant_rs}
        self.tenants["all"] = 0
        tenants = list(self.tenants.keys())
        self.tenant_option_menu.configure(values=tenants, state="normal")
        self.load_data_button.configure(state="normal")

    def region_dropdown_callback(self, choice):
        query_params = {}
        self.region_id = self.regions[choice]
        if self.region_id != 0:
            query_params["region_id"] = self.region_id
        sites_rs = self.nb.dcim.sites.filter(**query_params)
        self.sites = {site.name: site.id for site in sites_rs}
        self.sites["all"] = 0
        sites = list(self.sites.keys())
        self.site_option_menu.configure(values=sites, state="normal")

    def tenants_dropdown_callback(self, choice):
        self.tenant_id = self.tenants[choice]

    def site_dropdown_callback(self, choice):
        self.site_id = self.sites[choice]

    def status_dropdown_callback(self, choice):
        self.status = self.status_values[choice]

    def load_data(self):
        query_params = {}
        if self.tenant_group_id != 0:
            query_params["tenant_group_id"] = self.tenant_group_id
        if self.tenant_id != 0:
            query_params["tenant_id"] = self.tenant_id
        if self.region_id != 0:
            query_params["region_id"] = self.region_id
        if self.site_id != 0:
            query_params["site_id"] = self.site_id
        if self.status != "all":
            query_params["status"] = self.status
        pprint(query_params)
        value_list = []
        try:
            # Pull and process devices
            if self.checkbox_device_var.get() == "on":
                devices = list(self.nb.dcim.devices.filter(**query_params))
                for device in devices:
                    region = self.get_region_by_site_id(device.site.id)
                    values = [
                        device.name,
                        device.status,
                        device.device_type,
                        device.primary_ip,
                        device.tenant,
                        device.site,
                        region,
                        device.serial,
                        "N/A",
                    ]
                    value_list.append(values)
            # Pull and process virtual device context
            if self.checkbox_context_var.get() == "on":
                contexts = self.nb.dcim.virtual_device_contexts.filter(**query_params)
                for context in contexts:
                    location_data = self.get_device_details_by_device_id(context.device.id)
                    values = [
                        context.name,
                        context.status,
                        "device-context",
                        context.primary_ip,
                        context.tenant,
                        location_data["site"],
                        location_data["region"],
                        "N/A",
                        context.device.name,
                    ]
                    value_list.append(values)
            # Pull and process virtual-machines
            if self.checkbox_vm_var.get() == "on":
                vms = self.nb.virtualization.virtual_machines.filter(**query_params)
                for vm in vms:
                    if site := vm.site:
                        region = self.get_region_by_site_id(vm.site.id)
                        site = site.name
                    else:
                        region = "N/A"
                        site = "N/A"
                    values = [
                        vm.name,
                        vm.status,
                        "virtual-machine",
                        vm.primary_ip,
                        vm.tenant,
                        site,
                        region,
                        "N/A",
                        "N/A",
                    ]
                    value_list.append(values)
            # Set list values and enable Save button
            self.sheet.set_sheet_data(value_list)
            self.save_data_button.configure(state="normal")

        except Exception as e:
            tk.messagebox.showerror("Python Error", message=e)

    def dummy_function(self):
        pass

    @lru_cache(maxsize=128)
    def get_region_by_site_id(self, site_id: int) -> str:
        print("No Cache Site")
        try:
            site = self.nb.dcim.sites.get(id=site_id)
            if region := site.region:
                region_name = region.name
            else:
                region_name = "N/A"
        except Exception as e:
            tk.messagebox.showerror("Python Error", message=e)
            region_name = "N/A"
        return region_name

    @lru_cache(maxsize=128)
    def get_device_details_by_device_id(self, device_id: int) -> dict:
        print("No Cache Device")
        try:
            device = self.nb.dcim.devices.get(id=device_id)
            site = device.site
            site_name = site.name
            if region := site.region:
                region_name = region.name
            else:
                region_name = "N/A"
        except Exception as e:
            tk.messagebox.showerror("Python Error", message=e)
            region_name = "N/A"
            site_name = "N/A"
        return {"site": site_name, "region": region_name}

    def save_sheet(self):
        filepath = asksaveasfilename(
            parent=self,
            title="Save sheet as",
            filetypes=[("CSV File", ".csv"), ("TSV File", ".tsv")],
            defaultextension=".csv",
            confirmoverwrite=True,
        )
        if not filepath or not filepath.lower().endswith((".csv", ".tsv")):
            return
        try:
            with open(normpath(filepath), "w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(
                    fh,
                    dialect=csv.excel
                    if filepath.lower().endswith(".csv")
                    else csv.excel_tab,
                    lineterminator="\n",
                )
                writer.writerows(self.sheet_span.data)
        except Exception:
            tk.messagebox.showerror("Python Error", message=e)
            return

if __name__ == "__main__":
    app = App()
    app.mainloop()

