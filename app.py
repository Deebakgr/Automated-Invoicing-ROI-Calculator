# import streamlit as st
# import sqlite3
# from datetime import datetime
# import json
# from fpdf import FPDF

# # ------------------------
# # INTERNAL CONSTANTS (not visible in UI)
# # ------------------------
# AUTOMATED_COST_PER_INVOICE = 0.20
# ERROR_RATE_AUTO = 0.001
# MIN_ROI_BOOST_FACTOR = 1.1
# DB_PATH = "roi_calculator.db"
# # ------------------------

# # ------------------------
# # DATABASE SETUP
# # ------------------------
# def init_db():
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("""CREATE TABLE IF NOT EXISTS scenarios (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     name TEXT UNIQUE,
#                     data TEXT,
#                     created_at TEXT)""")
#     c.execute("""CREATE TABLE IF NOT EXISTS leads (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     email TEXT,
#                     scenario_name TEXT,
#                     created_at TEXT)""")
#     conn.commit()
#     conn.close()

# init_db()

# def save_scenario(name, data):
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("INSERT OR REPLACE INTO scenarios (name, data, created_at) VALUES (?, ?, ?)",
#               (name, json.dumps(data), datetime.now().isoformat()))
#     conn.commit()
#     conn.close()

# def load_scenarios():
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("SELECT name FROM scenarios")
#     rows = [r[0] for r in c.fetchall()]
#     conn.close()
#     return rows

# def get_scenario(name):
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("SELECT data FROM scenarios WHERE name = ?", (name,))
#     row = c.fetchone()
#     conn.close()
#     return json.loads(row[0]) if row else None

# def delete_scenario(name):
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("DELETE FROM scenarios WHERE name = ?", (name,))
#     conn.commit()
#     conn.close()

# def save_lead(email, scenario_name):
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("INSERT INTO leads (email, scenario_name, created_at) VALUES (?, ?, ?)",
#               (email, scenario_name, datetime.now().isoformat()))
#     conn.commit()
#     conn.close()

# # ------------------------
# # ROI CALCULATION (Bias-Favored)
# # ------------------------
# def compute_roi(inputs):
#     monthly_invoice_volume = float(inputs["monthly_invoice_volume"])
#     num_ap_staff = float(inputs["num_ap_staff"])
#     hourly_wage = float(inputs["hourly_wage"])
#     avg_hours_per_invoice = float(inputs["avg_hours_per_invoice"])
#     error_rate_manual = float(inputs["error_rate_manual"]) / 100
#     error_cost = float(inputs["error_cost"])
#     time_horizon_months = int(inputs["time_horizon_months"])
#     one_time_implementation_cost = float(inputs["one_time_implementation_cost"])

#     # Step 1: Manual labor cost per month
#     labor_cost_manual = num_ap_staff * hourly_wage * avg_hours_per_invoice * monthly_invoice_volume

#     # Step 2: Automation cost per month
#     auto_cost = monthly_invoice_volume * AUTOMATED_COST_PER_INVOICE

#     # Step 3: Error savings
#     error_savings = (error_rate_manual - ERROR_RATE_AUTO) * monthly_invoice_volume * error_cost

#     # Step 4: Monthly savings before bias
#     monthly_savings = (labor_cost_manual + error_savings) - auto_cost

#     # Step 5: Apply bias factor
#     monthly_savings *= MIN_ROI_BOOST_FACTOR
#     monthly_savings = max(monthly_savings, 100)  # always positive

#     # Step 6: Cumulative and ROI
#     cumulative_savings = monthly_savings * time_horizon_months
#     net_savings = cumulative_savings - one_time_implementation_cost
#     payback_months = one_time_implementation_cost / monthly_savings if monthly_savings > 0 else 999
#     roi_percentage = (net_savings / one_time_implementation_cost) * 100

#     # Ensure ROI looks favorable
#     roi_percentage = max(roi_percentage, 20)

#     return {
#         "labor_cost_manual": round(labor_cost_manual, 2),
#         "automation_cost": round(auto_cost, 2),
#         "error_savings": round(error_savings, 2),
#         "monthly_savings": round(monthly_savings, 2),
#         "cumulative_savings": round(cumulative_savings, 2),
#         "net_savings": round(net_savings, 2),
#         "payback_months": round(payback_months, 1),
#         "roi_percent": round(roi_percentage, 1)
#     }

# # ------------------------
# # PDF REPORT GENERATOR
# # ------------------------
# def generate_pdf(scenario_name, inputs, results):
#     pdf = FPDF()
#     pdf.add_page()
#     pdf.set_font("Arial", "B", 16)
#     pdf.cell(200, 10, txt="ROI Report: Automated Invoicing", ln=True, align="C")

#     pdf.set_font("Arial", "", 12)
#     pdf.cell(200, 10, txt=f"Scenario: {scenario_name}", ln=True)
#     pdf.cell(200, 10, txt=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)

#     pdf.ln(10)
#     pdf.set_font("Arial", "B", 14)
#     pdf.cell(200, 10, txt="Input Summary", ln=True)
#     pdf.set_font("Arial", "", 12)
#     for k, v in inputs.items():
#         pdf.cell(200, 8, txt=f"{k}: {v}", ln=True)

#     pdf.ln(10)
#     pdf.set_font("Arial", "B", 14)
#     pdf.cell(200, 10, txt="Results", ln=True)
#     pdf.set_font("Arial", "", 12)
#     for k, v in results.items():
#         pdf.cell(200, 8, txt=f"{k}: {v}", ln=True)

#     file_path = f"report_{scenario_name}.pdf"
#     pdf.output(file_path)
#     return file_path

# # ------------------------
# # STREAMLIT UI
# # ------------------------
# st.set_page_config("ROI Calculator", layout="centered")
# st.title("💰 Automated Invoicing ROI Calculator")
# st.markdown("Estimate your **cost savings**, **payback period**, and **ROI** from switching to automation.")

# with st.form("roi_form"):
#     st.subheader("📊 Enter Your Business Metrics")
    
#     scenario_name = st.text_input("Scenario Name", value="")  # empty
#     monthly_invoice_volume = st.number_input("Monthly Invoice Volume", value=0, min_value=0)
#     num_ap_staff = st.number_input("Number of AP Staff", value=0, min_value=0)
#     hourly_wage = st.number_input("Average Hourly Wage ($)", value=0.0, min_value=0.0)
#     avg_hours_per_invoice = st.number_input("Average Hours per Invoice", value=0.0, min_value=0.0)
#     error_rate_manual = st.number_input("Manual Error Rate (%)", value=0.0, min_value=0.0)
#     error_cost = st.number_input("Error Correction Cost ($)", value=0.0, min_value=0.0)
#     time_horizon_months = st.number_input("Projection Period (Months)", value=0, min_value=0)
#     one_time_implementation_cost = st.number_input("One-Time Implementation Cost ($)", value=0.0, min_value=0.0)
    
#     submitted = st.form_submit_button("Run Simulation")

# # ------------------------
# # Validation
# # ------------------------
# def is_input_valid(inputs):
#     return all(f not in [None, "", 0] for f in inputs)

# if submitted:
#     user_inputs = {
#         "scenario_name": scenario_name,
#         "monthly_invoice_volume": monthly_invoice_volume,
#         "num_ap_staff": num_ap_staff,
#         "hourly_wage": hourly_wage,
#         "avg_hours_per_invoice": avg_hours_per_invoice,
#         "error_rate_manual": error_rate_manual,
#         "error_cost": error_cost,
#         "time_horizon_months": time_horizon_months,
#         "one_time_implementation_cost": one_time_implementation_cost,
#     }

#     if not is_input_valid(user_inputs):
#         st.warning("⚠️ Please fill in all business metrics with valid non-zero values before running the simulation.")
#     else:
#         results = compute_roi(user_inputs)
#         st.session_state["latest_inputs"] = user_inputs
#         st.session_state["latest_results"] = results

#         st.subheader("📈 ROI Results")
#         c1, c2, c3 = st.columns(3)
#         c1.metric("Monthly Savings", f"${results['monthly_savings']:,}")
#         c2.metric("Payback", f"{results['payback_months']} months")
#         c3.metric(f"ROI ({time_horizon_months} mo)", f"{results['roi_percent']}%")

#         with st.expander("See detailed calculations"):
#             st.json(results)

# # ------------------------
# # SCENARIO MANAGEMENT
# # ------------------------
# st.markdown("---")
# st.subheader("💾 Scenario Management")

# col1, col2, col3 = st.columns(3)
# with col1:
#     if st.button("Save Scenario"):
#         if "latest_inputs" in st.session_state and is_input_valid(st.session_state["latest_inputs"]):
#             save_scenario(st.session_state["latest_inputs"]["scenario_name"], st.session_state["latest_inputs"])
#             st.success("Scenario saved successfully!")
#         else:
#             st.warning("⚠️ Run a valid simulation before saving the scenario.")

# with col2:
#     if st.button("Load Scenario"):
#         options = load_scenarios()
#         if options:
#             choice = st.selectbox("Select Scenario", options)
#             if st.button("Load"):
#                 loaded = get_scenario(choice)
#                 st.write("Loaded Scenario:")
#                 st.json(loaded)
#         else:
#             st.info("No saved scenarios yet.")

# with col3:
#     if st.button("Delete Scenario"):
#         to_delete = st.text_input("Enter scenario name to delete")
#         if to_delete:
#             delete_scenario(to_delete)
#             st.warning(f"Deleted scenario: {to_delete}")

# # ------------------------
# # EMAIL-GATED REPORT
# # ------------------------
# st.markdown("---")
# st.subheader("📩 Generate ROI Report (Email Required)")
# email = st.text_input("Enter your email to download report")

# if st.button("Generate PDF Report"):
#     if not email or "@" not in email:
#         st.error("Please enter a valid email address.")
#     elif "latest_inputs" not in st.session_state or not is_input_valid(st.session_state["latest_inputs"]):
#         st.warning("⚠️ Run a valid simulation before generating a report.")
#     else:
#         save_lead(email, st.session_state["latest_inputs"]["scenario_name"])
#         path = generate_pdf(st.session_state["latest_inputs"]["scenario_name"], st.session_state["latest_inputs"], st.session_state["latest_results"])
#         with open(path, "rb") as f:
#             st.download_button("📄 Download Report", f, file_name=path)
#         st.success("Report generated! Check your downloads.")














import streamlit as st
import sqlite3
from datetime import datetime
import json
from fpdf import FPDF
import math

# ------------------------
# INTERNAL CONSTANTS
# ------------------------
AUTOMATED_COST_PER_INVOICE = 0.20
ERROR_RATE_AUTO = 0.001
TIME_SAVED_PER_INVOICE = 8 / 60  # 8 minutes per invoice converted to hours
MIN_ROI_BOOST_FACTOR = 1.1
DB_PATH = "roi_calculator.db"

# ------------------------
# DATABASE SETUP
# ------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS scenarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    data TEXT,
                    created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT,
                    scenario_name TEXT,
                    created_at TEXT)""")
    conn.commit()
    conn.close()

init_db()

def save_scenario(name, data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO scenarios (name, data, created_at) VALUES (?, ?, ?)",
              (name, json.dumps(data), datetime.now().isoformat()))
    conn.commit()
    conn.close()

def load_scenarios():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name FROM scenarios")
    rows = [r[0] for r in c.fetchall()]
    conn.close()
    return rows

def get_scenario(name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT data FROM scenarios WHERE name = ?", (name,))
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row else None

def delete_scenario(name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM scenarios WHERE name = ?", (name,))
    conn.commit()
    conn.close()

def save_lead(email, scenario_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO leads (email, scenario_name, created_at) VALUES (?, ?, ?)",
              (email, scenario_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# ------------------------
# INPUT VALIDATION
# ------------------------
def is_input_valid(inputs):
    must_be_positive = [
        "monthly_invoice_volume", "num_ap_staff",
        "hourly_wage", "avg_hours_per_invoice",
        "error_cost"
    ]
    for key in must_be_positive:
        try:
            if float(inputs[key]) <= 0:
                return False
        except:
            return False
    return True

# ------------------------
# ROI CALCULATION
# ------------------------
def compute_roi(inputs):
    monthly_invoice_volume = float(inputs["monthly_invoice_volume"])
    num_ap_staff = float(inputs["num_ap_staff"])
    hourly_wage = float(inputs["hourly_wage"])
    avg_hours_per_invoice = float(inputs["avg_hours_per_invoice"]) / 60.0  # convert mins → hrs
    error_cost = float(inputs["error_cost"])

    # Fixed manual error rate assumption (5%)
    manual_error_rate = 0.05

    # Step 1: Manual labor cost per month
    labor_cost_manual = monthly_invoice_volume * avg_hours_per_invoice * hourly_wage

    # Step 2: Automation cost per month
    auto_cost = monthly_invoice_volume * AUTOMATED_COST_PER_INVOICE

    # Step 3: Error savings
    error_savings = (manual_error_rate - ERROR_RATE_AUTO) * monthly_invoice_volume * error_cost

    # Step 4: Time savings (8 mins saved per invoice)
    time_savings_value = TIME_SAVED_PER_INVOICE * hourly_wage * monthly_invoice_volume

    # Step 5: Monthly savings before bias
    monthly_savings = (labor_cost_manual + error_savings + time_savings_value) - auto_cost
    monthly_savings *= MIN_ROI_BOOST_FACTOR
    monthly_savings = max(monthly_savings, 100)

    # Step 6: ROI and payback (assume automation setup = 6 months equivalent)
    implementation_cost = labor_cost_manual * 0.5
    net_savings = monthly_savings * 36 - implementation_cost  # 3-year ROI period
    roi_percentage = (net_savings / implementation_cost) * 100 if implementation_cost != 0 else float('inf')
    payback_months = implementation_cost / monthly_savings if monthly_savings > 0 else float('inf')

    return {
        "labor_cost_manual": round(labor_cost_manual, 2),
        "automation_cost": round(auto_cost, 2),
        "error_savings": round(error_savings, 2),
        "time_savings_value": round(time_savings_value, 2),
        "monthly_savings": round(monthly_savings, 2),
        "net_savings": round(net_savings, 2),
        "payback_months": round(payback_months, 1) if math.isfinite(payback_months) else "∞",
        "roi_percent": round(roi_percentage, 1) if math.isfinite(roi_percentage) else "∞"
    }

# ------------------------
# PDF REPORT GENERATOR
# ------------------------
def generate_pdf(scenario_name, inputs, results):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="ROI Report: Automated Invoicing", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, txt=f"Scenario: {scenario_name}", ln=True)
    pdf.cell(200, 10, txt=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt="Input Summary", ln=True)
    pdf.set_font("Arial", "", 12)
    for k, v in inputs.items():
        pdf.cell(200, 8, txt=f"{k}: {v}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt="Results", ln=True)
    pdf.set_font("Arial", "", 12)
    for k, v in results.items():
        pdf.cell(200, 8, txt=f"{k}: {v}", ln=True)

    file_path = f"report_{scenario_name}.pdf"
    pdf.output(file_path)
    return file_path

# ------------------------
# STREAMLIT UI
# ------------------------
st.set_page_config("ROI Calculator", layout="centered")
st.title("💰 Automated Invoicing ROI Calculator")
st.markdown("Estimate your **cost savings**, **payback period**, and **ROI** from switching to automation.")

with st.form("roi_form"):
    st.subheader("📊 Enter Your Business Metrics")

    scenario_name = st.text_input("Scenario Name", value="")
    monthly_invoice_volume = st.number_input("Monthly Invoice Volume", value=0, min_value=0)
    num_ap_staff = st.number_input("Number of AP Staff", value=0, min_value=0)
    hourly_wage = st.number_input("Average Hourly Wage ($)", value=0.0, min_value=0.0)
    avg_hours_per_invoice = st.number_input("Average Minutes per Invoice", value=0.0, min_value=0.0)
    error_cost = st.number_input("Error Correction Cost ($)", value=0.0, min_value=0.0)

    submitted = st.form_submit_button("Run Simulation")

# ------------------------
# SIMULATION RESULTS
# ------------------------
if submitted:
    user_inputs = {
        "scenario_name": scenario_name,
        "monthly_invoice_volume": monthly_invoice_volume,
        "num_ap_staff": num_ap_staff,
        "hourly_wage": hourly_wage,
        "avg_hours_per_invoice": avg_hours_per_invoice,
        "error_cost": error_cost
    }

    if not is_input_valid(user_inputs):
        st.warning("⚠️ Please fill in all fields with valid non-zero values.")
    else:
        results = compute_roi(user_inputs)
        st.session_state["latest_inputs"] = user_inputs
        st.session_state["latest_results"] = results

        st.subheader("📈 ROI Results")
        c1, c2, c3 = st.columns(3)
        c1.metric("Monthly Savings", f"${results['monthly_savings']:,}")
        c2.metric("Payback", f"{results['payback_months']} months")
        c3.metric(f"ROI (36 mo)", f"{results['roi_percent']}%")

        with st.expander("See detailed calculations"):
            st.json(results)

# ------------------------
# SCENARIO MANAGEMENT
# ------------------------
st.markdown("---")
st.subheader("💾 Scenario Management")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Save Scenario"):
        if "latest_inputs" in st.session_state and is_input_valid(st.session_state["latest_inputs"]):
            save_scenario(st.session_state["latest_inputs"]["scenario_name"], st.session_state["latest_inputs"])
            st.success("Scenario saved successfully!")
        else:
            st.warning("⚠️ Run a valid simulation before saving the scenario.")

with col2:
    if st.button("Load Scenario"):
        options = load_scenarios()
        if options:
            choice = st.selectbox("Select Scenario", options)
            if st.button("Load Selected"):
                loaded = get_scenario(choice)
                st.write("Loaded Scenario:")
                st.json(loaded)
        else:
            st.info("No saved scenarios yet.")

st.subheader("Delete Scenario")
options_delete = load_scenarios()
if options_delete:
    to_delete = st.selectbox("Select scenario to delete", options_delete)
    if st.button("Delete Selected Scenario"):
        delete_scenario(to_delete)
        st.warning(f"Deleted scenario: {to_delete}")
else:
    st.info("No saved scenarios yet.")

# ------------------------
# EMAIL-GATED PDF REPORT
# ------------------------
st.markdown("---")
st.subheader("📩 Generate ROI Report (Email Required)")
email = st.text_input("Enter your email to download report")

if st.button("Generate PDF Report"):
    if not email or "@" not in email:
        st.error("Please enter a valid email address.")
    elif "latest_inputs" not in st.session_state or not is_input_valid(st.session_state["latest_inputs"]):
        st.warning("⚠️ Run a valid simulation before generating a report.")
    else:
        save_lead(email, st.session_state["latest_inputs"]["scenario_name"])
        path = generate_pdf(st.session_state["latest_inputs"]["scenario_name"],
                            st.session_state["latest_inputs"],
                            st.session_state["latest_results"])
        with open(path, "rb") as f:
            st.download_button("📄 Download Report", f, file_name=path)
