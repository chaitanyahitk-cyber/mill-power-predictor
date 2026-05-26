import streamlit as st
import pandas as pd
import numpy as np
import re
import datetime
import time  
from io import BytesIO
import extra_streamlit_components as stx

st.set_page_config(page_title="Mill Power Predictor", layout="wide")

# --- INITIALIZE COOKIE MANAGER ---
cookie_manager = stx.CookieManager()

# --- ACCOUNT & LOGIN SYSTEM (WITH CLOUD SECURITY FIXES) ---
def login_system():
    # 1. Cloud Latency Sync (1.2s pause for internet lag)
    if "cookies_synced" not in st.session_state:
        st.session_state["cookies_synced"] = True
        time.sleep(1.2) 
        st.rerun()

    # 2. Check for the valid cookie
    auth_cookie = cookie_manager.get(cookie="tega_auth_user")
    
    if auth_cookie:
        st.session_state["logged_in"] = True
        st.session_state["username"] = auth_cookie
        return True

    # 3. Setup Session State fallback
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""

    # 4. Display Login Form
    if not st.session_state["logged_in"]:
        st.markdown("<br><br>", unsafe_allow_html=True) 
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("🔒 Gateway Access")
            st.write("Please log in to access the Industrial Mill Predictor.")
            
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login", use_container_width=True)
                
                if submit:
                    if username.strip() == "":
                        st.error("Please enter a username.")
                    elif password == "tegapower1258": 
                        formatted_name = username.strip().capitalize()
                        
                        # Set secure cloud cookie valid for 30 days
                        cookie_manager.set(
                            cookie="tega_auth_user", 
                            val=formatted_name, 
                            expires_at=datetime.datetime.now() + datetime.timedelta(days=30),
                            secure=True,          
                            same_site="none"      
                        )
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = formatted_name
                        
                        # Wait 1.2s for cloud network to physically save the cookie
                        time.sleep(1.2) 
                        st.rerun() 
                    else:
                        st.error("Incorrect Password.")
        return False
    return True

# Stop the app from rendering anything else if they aren't logged in
if not login_system():
    st.stop()


# --- CUSTOM UI COMPRESSION & PROFESSIONAL STYLING (CSS) ---
st.markdown("""
    <style>
        .stApp > header { background-color: transparent !important; }
        .block-container {
            padding-top: 3rem !important; 
            padding-bottom: 1rem !important; 
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important; 
        }
        h1 {
            color: #0E1117 !important;
            font-weight: 800 !important;
            padding-top: 0rem !important;
            padding-bottom: 0.5rem !important;
            border-bottom: 3px solid #1f77b4;
            margin-bottom: 1rem !important;
            margin-top: 0rem !important; 
        }
        .custom-metric-card {
            border: 1px solid #e0e6ed;
            border-radius: 8px;
            padding: 12px;
            background-color: #ffffff;
            border-left: 5px solid #1f77b4;
            box-shadow: 0 2px 4px rgba(0,0,0,0.04);
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .custom-metric-label {
            font-size: 0.85rem;
            color: #555555;
            font-weight: 500;
            margin-bottom: 4px;
        }
        .custom-metric-value {
            font-size: 1.3rem;
            font-weight: 800;
            color: #000000;
            word-break: break-word !important; 
            white-space: normal !important;
            line-height: 1.2;
        }
        .stButton>button {
            background-color: #1f77b4; color: white; border-radius: 6px; font-weight: 600; border: none; padding: 0.6rem 1.2rem; transition: all 0.3s;
        }
        .stButton>button:hover {
            background-color: #155a8a; color: white; box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        [data-testid="stVerticalBlock"] { gap: 0.4rem !important; }
        [data-testid="stExpander"] {
            margin-bottom: 0rem !important; border: 1px solid #e0e6ed !important; border-radius: 8px !important; background-color: #fafbfc;
        }
        @media (max-width: 767px) {
            [data-testid="collapsedControl"] {
                display: flex !important; position: fixed !important; top: 0.5rem !important; left: 0.5rem !important; z-index: 999999 !important; background-color: #ffffff; border: 1px solid #e0e6ed; border-radius: 4px; padding: 4px;
            }
        }
        @media (prefers-color-scheme: dark) {
            h1, h2 { color: #FAFAFA !important; }
            .custom-metric-card { background-color: #262730; border: 1px solid rgba(250, 250, 250, 0.1); border-left: 5px solid #1f77b4; }
            .custom-metric-label { color: #aaaaaa; }
            .custom-metric-value { color: #ffffff; }
            [data-testid="stExpander"] { background-color: #1e1e24; border: 1px solid #333 !important; }
            [data-testid="collapsedControl"] { background-color: #262730; border: 1px solid #555; }
        }
    </style>
""", unsafe_allow_html=True)

st.title("Industrial Mill Power Predictor")

# --- NATIVE FORMULA RENDERER ---
def display_power_formula(mill_type):
    if mill_type == "Ball Mill":
        st.info(r"**Applied Power Model**" + "\n\n" + r"$$P_{ball} = 0.0607 \cdot D_{eff}^{2.434} \cdot L_{eff}^{1.0631} \cdot N^{0.869} \cdot J^{0.5457} \cdot TPH^{0.065} \cdot F_{80}^{0.0224} \cdot P_{80}^{-0.0589} \cdot W_L^{0.08}$$", icon="⚙️")
    else:
        st.info(r"**Applied Power Model**" + "\n\n" + r"$$P_{sag} = 0.0523 \cdot D_{eff}^{2.5996} \cdot L_{eff}^{0.9018} \cdot N^{0.8002} \cdot J^{0.3222} \cdot J_b^{0.3530} \cdot TPH^{0.029} \cdot F_{80}^{0.01} \cdot P_{80}^{-0.0104} \cdot W_L^{0.10}$$", icon="⚙️")

# --- CORE MATH ---
def calculate_ball_power(deff, leff, n, j, tph, f80, p80, wl):
    return 0.0607 * (deff**2.434) * (leff**1.0631) * (n**0.869) * (j**0.5457) * (tph**0.065) * (f80**0.0224) * (p80**-0.0589) * (wl**0.08)

def calculate_sag_mech_power(deff, leff, n, j, jb, tph, f80, p80, wl):
    return 0.0523 * (deff**2.5996) * (leff**0.9018) * (n**0.8002) * (j**0.3222) * (jb**0.3530) * (tph**0.029) * (f80**0.01) * (p80**-0.0104) * (wl**0.10)

def calculate_bond_power(bwi, tph, f80, p80):
    return 10 * bwi * ((1/np.sqrt(p80)) - (1/np.sqrt(f80))) * tph

def calculate_sag_grind_power(bwi, tph, f80, p80):
    base_bond = calculate_bond_power(bwi, tph, f80, p80)
    return base_bond * 1.25

# --- SMART COLUMN IDENTIFIER ---
def standardize_columns(dataframe):
    mapping = {}
    for col in dataframe.columns:
        c = str(col).lower()
        if re.search(r'deff', c): mapping[col] = 'DEFF(m)'
        elif re.search(r'leff', c): mapping[col] = 'LEFF(m)'
        elif re.search(r'tph|throughput', c): mapping[col] = 'TPH'
        elif re.search(r'f80', c): mapping[col] = 'F80'
        elif re.search(r'p80', c): mapping[col] = 'P80'
        elif re.search(r'wl|liner.*weight|weight.*liner', c): mapping[col] = 'WL (tons)'
        elif re.search(r'bwi|bond', c): mapping[col] = 'BWI'
        elif re.search(r'jb|ball.*charge', c): mapping[col] = 'Jb %'
        elif re.search(r'\bn\b|rpm|speed', c): mapping[col] = 'N (RPM)'
        elif re.search(r'\bj\b|fill', c) and not re.search(r'jb', c): mapping[col] = 'J %'
    return dataframe.rename(columns=mapping)

# --- UI & CONFIGURATION ---
with st.sidebar:
    # User Greeting & Logout
    st.success(f"👋 Welcome, {st.session_state['username']}!")
    if st.button("Log Out", use_container_width=True):
        cookie_manager.delete("tega_auth_user") 
        time.sleep(1.2) # Let cloud browser physically delete the cookie
        st.session_state.clear() 
        st.rerun()
    
    st.divider()
    
    mode = st.radio("Mode:", ["Manual Input", "Excel Batch Upload"])
    mill_type = st.radio("Mill Type:", ["Ball Mill", "SAG Mill"])
    
    st.divider()
    st.markdown("### Output Parameters")
    st.caption("Select parameters to calculate:")
    
    with st.expander("Toggle Outputs", expanded=True):
        out_p_mech = st.checkbox("Predicted Power (kW)", value=True)
        out_p_bond = st.checkbox("Bond Power (kW)", value=True)
        out_se = st.checkbox("Sp. Energy (kWh/t)", value=True)
        out_eff = st.checkbox("Efficiency (%)", value=True)
        out_max_tph = st.checkbox("Max TPH (t/h)", value=True)
        out_rem = st.checkbox("Remarks", value=True)

selected_outputs = []
if out_p_mech: selected_outputs.append("Predicted Power (kW)")
if out_p_bond: selected_outputs.append("Bond Power (kW)")
if out_se: selected_outputs.append("Sp. Energy (kWh/t)")
if out_eff: selected_outputs.append("Efficiency (%)")
if out_max_tph: selected_outputs.append("Max TPH (t/h)")
if out_rem: selected_outputs.append("Remarks")

if not selected_outputs:
    st.warning("Please tick at least one output parameter in the sidebar.")
    st.stop()

# --- DYNAMIC DEPENDENCIES ---
needs_mech = any(o in selected_outputs for o in ["Predicted Power (kW)", "Sp. Energy (kWh/t)", "Efficiency (%)", "Max TPH (t/h)", "Remarks"])
needs_bond = any(o in selected_outputs for o in ["Bond Power (kW)", "Efficiency (%)", "Max TPH (t/h)", "Remarks"])

required_cols = ['TPH', 'F80', 'P80']
if needs_mech:
    required_cols.extend(['DEFF(m)', 'LEFF(m)', 'N (RPM)', 'J %', 'WL (tons)'])
    if mill_type == "SAG Mill": required_cols.append('Jb %')
if needs_bond:
    required_cols.append('BWI')


# --- ANALYTICS PROCESSOR ---
def process_analytics(df, mill_type):
    def calc_row(r):
        out = {col: None for col in selected_outputs}
        try:
            tph = float(r.get('TPH', 0))
            f80 = float(r.get('F80', 0))
            p80 = float(r.get('P80', 0))
            
            if p80 >= f80 and f80 > 0:
                return pd.Series({c: "Error: P80 >= F80" if "Remarks" in c else 0 for c in selected_outputs})

            p_mech, p_bond, se, max_tph = 0, 0, 0, 0
            eff, rem = "N/A", "N/A"

            if needs_mech:
                deff, leff, n, j, wl = float(r['DEFF(m)']), float(r['LEFF(m)']), float(r['N (RPM)']), float(r['J %']), float(r['WL (tons)'])
                if mill_type == "Ball Mill":
                    p_mech = calculate_ball_power(deff, leff, n, j, tph, f80, p80, wl)
                else:
                    jb = float(r['Jb %'])
                    p_mech = calculate_sag_mech_power(deff, leff, n, j, jb, tph, f80, p80, wl)
                se = p_mech / tph if tph > 0 else 0

            if needs_bond:
                bwi = float(r['BWI'])
                if mill_type == "Ball Mill":
                    p_bond = calculate_bond_power(bwi, tph, f80, p80)
                else:
                    p_bond = calculate_sag_grind_power(bwi, tph, f80, p80)

            if needs_mech and needs_bond:
                if mill_type == "Ball Mill":
                    max_tph = max(0, (( (p_mech / (tph**0.065)) / (10 * bwi * ((1/np.sqrt(p80)) - (1/np.sqrt(f80)))) )**(1/0.935))) if tph > 0 and bwi > 0 else 0
                    eff_ratio = p_bond / p_mech if p_mech > 0 else 0
                    if eff_ratio > 1.0:
                        eff = f"{eff_ratio * 100:.1f}%"
                        rem = "OVERLOADED"
                    else:
                        eff = f"{eff_ratio * 100:.1f}%"
                        if max_tph < tph - 0.1: rem = f"REDUCE TPH to {max_tph:.1f}"
                        else: rem = "OK"
                else:
                    spec_energy_req = 10 * bwi * ((1/np.sqrt(p80)) - (1/np.sqrt(f80))) * 1.25 if f80 != p80 else 0
                    max_tph = p_mech / spec_energy_req if spec_energy_req > 0 else 0
                    eff_ratio = p_bond / p_mech if p_mech > 0 else 0
                    if eff_ratio > 1.0:
                        eff = f"{eff_ratio * 100:.1f}%"
                        rem = "OVERLOADED"
                    else:
                        eff = f"{eff_ratio * 100:.1f}%"
                        if max_tph < (0.4 * tph): rem = f"GRIND-OUT RISK: Limit {max_tph:.1f} t/h"
                        elif max_tph < tph - 0.1: rem = f"REDUCE TPH to {max_tph:.1f}"
                        else: rem = "OK"

            if "Predicted Power (kW)" in selected_outputs: out["Predicted Power (kW)"] = p_mech
            if "Bond Power (kW)" in selected_outputs: out["Bond Power (kW)"] = p_bond
            if "Sp. Energy (kWh/t)" in selected_outputs: out["Sp. Energy (kWh/t)"] = se
            if "Efficiency (%)" in selected_outputs: out["Efficiency (%)"] = eff
            if "Max TPH (t/h)" in selected_outputs: out["Max TPH (t/h)"] = max_tph if (needs_mech and needs_bond) else np.nan
            if "Remarks" in selected_outputs: out["Remarks"] = rem

            return pd.Series(out)
        except Exception as e: 
            err_dict = {col: "Error" if "%)" in col or "Remarks" in col else 0 for col in selected_outputs}
            if "Remarks" in selected_outputs: err_dict["Remarks"] = "Check Inputs"
            return pd.Series(err_dict)
    
    res = df.apply(calc_row, axis=1)
    
    all_possible_outputs = ["Predicted Power (kW)", "Bond Power (kW)", "Sp. Energy (kWh/t)", "Efficiency (%)", "Max TPH (t/h)", "Remarks"]
    cols_to_drop = [c for c in all_possible_outputs if c in df.columns]
    df = df.drop(columns=cols_to_drop)
    
    df[selected_outputs] = res
    return df


if mode == "Manual Input":
    st.header(f"{mill_type} - Manual Input")
    
    if out_p_mech:
        display_power_formula(mill_type)

    active_inputs = []
    
    if needs_mech:
        active_inputs.append(("deff", "DEFF: Effective dia of mill (m)", 8.0))
        active_inputs.append(("leff", "LEFF: Effective length of mill (m)", 12.0))
        active_inputs.append(("wl", "WL: Weight of liners (tons)", 150.0))
        active_inputs.append(("n", "N: Mill rotational speed (RPM)", 13.5))
        active_inputs.append(("j", "J: Mill filling degree (%)", 30.0))
        if mill_type == "SAG Mill":
            active_inputs.append(("jb", "Jb: Ball charge filling (%)", 10.0))
            
    active_inputs.append(("tph", "TPH: Fresh feed throughput (t/h)", 1000.0))
    active_inputs.append(("f80", "F80: 80% passing size of feed (µm)", 10000.0))
    active_inputs.append(("p80", "P80: Target product 80% passing size (µm)", 150.0))
    
    if needs_bond:
        active_inputs.append(("bwi", "BWI: Bond Work Index (kWh/t)", 15.0))

    input_data = {}
    num_cols = min(4, len(active_inputs))
    
    if num_cols > 0:
        cols = st.columns(num_cols)
        for i, (var_name, label, default_val) in enumerate(active_inputs):
            with cols[i % num_cols]:
                input_data[var_name] = st.number_input(label, value=default_val, step=0.0001, format="%.4f")
    
    st.divider()
    
    input_df_dict = {
        'TPH': input_data.get('tph', 1000.0), 
        'F80': input_data.get('f80', 10000.0), 
        'P80': input_data.get('p80', 150.0)
    }
    if needs_mech:
        input_df_dict.update({
            'DEFF(m)': input_data.get('deff', 8.0),
            'LEFF(m)': input_data.get('leff', 12.0),
            'N (RPM)': input_data.get('n', 13.5),
            'J %': input_data.get('j', 30.0),
            'WL (tons)': input_data.get('wl', 150.0)
        })
        if mill_type == "SAG Mill": 
            input_df_dict['Jb %'] = input_data.get('jb', 10.0)
    if needs_bond:
        input_df_dict['BWI'] = input_data.get('bwi', 15.0)
        
    temp_df = pd.DataFrame([input_df_dict])
    res_df = process_analytics(temp_df, mill_type)
    
    metrics_to_show = [m for m in selected_outputs if m != "Remarks"]
    if metrics_to_show:
        m_cols = st.columns(len(metrics_to_show))
        for i, metric in enumerate(metrics_to_show):
            val = res_df.iloc[0][metric]
            
            if "Power" in metric:
                display_val = f"{val:,.0f} kW"
                label = metric.replace(" (kW)", "")
            elif "Sp. Energy" in metric:
                display_val = f"{val:.2f} kWh/t"
                label = "Sp. Energy"
            elif "Max TPH" in metric:
                display_val = f"{val:,.1f} t/h" if not pd.isna(val) else "N/A"
                label = "Max TPH"
            else:
                display_val = str(val) if not pd.isna(val) else "N/A"
                label = metric.split(" ")[0]

            html_card = f"""
            <div class="custom-metric-card">
                <div class="custom-metric-label">{label}</div>
                <div class="custom-metric-value">{display_val}</div>
            </div>
            """
            m_cols[i].markdown(html_card, unsafe_allow_html=True)
    
    if "Remarks" in selected_outputs:
        rem = res_df.iloc[0]["Remarks"]
        if "OVERLOADED" in rem:
            st.error("OVERLOADED: Efficiency > 100%. Data conflict or massive overload.")
        elif "GRIND-OUT RISK" in rem:
            st.error(rem)
        elif "REDUCE TPH" in rem:
            st.warning(rem)
        elif rem == "OK":
            st.success("Mill operating smoothly within power limits.")


else:
    st.header(f"{mill_type} - Master Analytics Table")

    if out_p_mech:
        display_power_formula(mill_type)
            
    if 'current_file' not in st.session_state: st.session_state.current_file = None
    if 'last_config' not in st.session_state: st.session_state.last_config = None
    
    with st.expander("Excel Upload Instructions", expanded=True):
        st.markdown("<p style='margin-bottom: 0.5rem; font-weight: 600; font-size: 0.95rem; color: #1f77b4;'>Dynamically Required Columns:</p>", unsafe_allow_html=True)
        
        desc_map = {
            'DEFF(m)': 'DEFF(m) - Effective dia of mill (m)',
            'LEFF(m)': 'LEFF(m) - Effective length of mill (m)',
            'N (RPM)': 'N (RPM) - Mill rotational speed',
            'J %': 'J % - Mill filling degree',
            'Jb %': 'Jb % - Ball charge filling',
            'TPH': 'TPH - Fresh feed throughput (t/h)',
            'F80': 'F80 - 80% passing size of feed (µm)',
            'P80': 'P80 - Target product 80% passing size (µm)',
            'WL (tons)': 'WL (tons) - Weight of liners',
            'BWI': 'BWI - Bond Work Index (kWh/t)'
        }
        
        c1, c2 = st.columns(2)
        mid_idx = (len(required_cols) + 1) // 2
        
        def build_html_list(cols):
            html = "<ul style='margin-top: 0; margin-bottom: 0; padding-left: 1.2rem; font-size: 0.85rem; line-height: 1.4;'>"
            for c in cols:
                html += f"<li style='margin-bottom: 0.2rem;'><b>{desc_map.get(c, c)}</b></li>"
            html += "</ul>"
            return html
            
        c1.markdown(build_html_list(required_cols[:mid_idx]), unsafe_allow_html=True)
        if len(required_cols) > mid_idx:
            c2.markdown(build_html_list(required_cols[mid_idx:]), unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload Excel", type=["xlsx", "csv"])
    
    if uploaded_file:
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"
        if st.session_state.current_file != file_id:
            if 'df' in st.session_state: del st.session_state['df']
            st.session_state.current_file = file_id
            st.session_state.last_config = None
            
        raw_df = pd.read_excel(uploaded_file) if not uploaded_file.name.endswith('.csv') else pd.read_csv(uploaded_file)
        raw_df = standardize_columns(raw_df)
        
        check_df = st.session_state.df if 'df' in st.session_state else raw_df
        missing = [c for c in required_cols if c not in check_df.columns]
        
        current_config = (mill_type, tuple(selected_outputs))
        config_changed = st.session_state.last_config != current_config
        
        if missing:
            st.error(f"Cannot calculate selected outputs. Missing required input parameter(s) in your data: {', '.join(missing)}")
            st.warning("Please uncheck the output parameters that require this data in the sidebar, or upload an updated Excel file.")
        else:
            if 'df' not in st.session_state or config_changed:
                base_df = check_df.copy()
                if 'df' not in st.session_state: 
                    for col in base_df.columns:
                        try: base_df[col] = base_df[col].astype(float)
                        except: pass
                        
                st.session_state.df = process_analytics(base_df, mill_type)
                st.session_state.last_config = current_config

            config = {c: st.column_config.NumberColumn(format="%.4f", step=0.0001) for c in required_cols}
            if "Predicted Power (kW)" in selected_outputs: config["Predicted Power (kW)"] = st.column_config.NumberColumn(disabled=True, format="%.2f")
            if "Bond Power (kW)" in selected_outputs: config["Bond Power (kW)"] = st.column_config.NumberColumn(disabled=True, format="%.2f")
            if "Sp. Energy (kWh/t)" in selected_outputs: config["Sp. Energy (kWh/t)"] = st.column_config.NumberColumn(disabled=True, format="%.3f")
            if "Efficiency (%)" in selected_outputs: config["Efficiency (%)"] = st.column_config.TextColumn(disabled=True)
            if "Max TPH (t/h)" in selected_outputs: config["Max TPH (t/h)"] = st.column_config.NumberColumn(disabled=True, format="%.1f")
            if "Remarks" in selected_outputs: config["Remarks"] = st.column_config.TextColumn(disabled=True)
            
            edited_df = st.data_editor(st.session_state.df, column_config=config, num_rows="dynamic", use_container_width=True)
            
            if not edited_df.equals(st.session_state.df):
                st.session_state.df = process_analytics(edited_df, mill_type)
                st.rerun()
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer: st.session_state.df.to_excel(writer, index=False)
            st.download_button("Download Updated Excel", data=output.getvalue(), file_name="Updated_Analytics.xlsx")