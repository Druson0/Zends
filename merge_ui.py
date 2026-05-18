import os

# paths
base_dir = r"c:\Users\Vigne\OneDrive\Desktop\Zends"
customer_ui_path = os.path.join(base_dir, "customer_ui.py")
rag_mgmt_path = os.path.join(base_dir, "rag_management.py")
output_path = os.path.join(base_dir, "customer_ui_new.py")

with open(customer_ui_path, "r", encoding="utf-8") as f:
    c_lines = f.readlines()

with open(rag_mgmt_path, "r", encoding="utf-8") as f:
    r_lines = f.readlines()

# find where Hero ends in customer_ui
hero_end_idx = -1
for i, line in enumerate(c_lines):
    if line.strip() == "# ── FAQ Section":
        hero_end_idx = i
        break

if hero_end_idx == -1:
    print("Could not find '# ── FAQ Section'")
    exit(1)

# we need to inject import requests at the top
c_lines.insert(2, "import requests\n")
hero_end_idx += 1  # shift because of insert

# Create tabs
tabs_code = [
    "\n    # Create Tabs to separate Customer view from Admin RAG view\n",
    "    tab_customer, tab_rag = st.tabs([\"💬 Customer Portal\", \"⚙️ RAG Document Management\"])\n\n",
    "    with tab_customer:\n"
]

c_top = c_lines[:hero_end_idx]
c_bottom = c_lines[hero_end_idx:]

# indent c_bottom
c_bottom_indented = []
for line in c_bottom:
    if line == "\n":
        c_bottom_indented.append(line)
    else:
        c_bottom_indented.append("        " + line)

# Extract RAG logic
rag_start_idx = -1
for i, line in enumerate(r_lines):
    if line.strip() == "# ─── UI Layout ───────────────────────────────────────────────────────────────":
        rag_start_idx = i
        break

if rag_start_idx == -1:
    print("Could not find RAG UI Layout")
    exit(1)

rag_logic = r_lines[rag_start_idx+1:]
rag_logic_indented = ["    with tab_rag:\n"]
for line in rag_logic:
    if line == "\n":
        rag_logic_indented.append(line)
    else:
        rag_logic_indented.append("        " + line)

with open(output_path, "w", encoding="utf-8") as f:
    f.writelines(c_top)
    f.writelines(tabs_code)
    f.writelines(c_bottom_indented)
    f.writelines(["\n"])
    f.writelines(rag_logic_indented)

print("Merged successfully!")
