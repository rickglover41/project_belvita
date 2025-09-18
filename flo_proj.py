import numpy as np
import streamlit as st

# START HERE FLORENCE initialize default parameter values
d_clc = None # contracted labor cost (dollars)
d_clh = None # contracted labor hours (hours)
d_cl_fte = None # contracted labor FTEs (two decimal place float)
d_slr= None # standard labor rate (dollars)
d_rn_share_cl = None # rn share of contract labor (estimator)
d_avg_fte_rn = None # average FTE per RN (usually expressed as 0.9 or 1.0)
d_flo_rn_fee = None # Florence RN fee (currently set at $50k)
d_system_name = None
d_data_sources = None

# last revision info (only UPDATE when sources and/or pricing change)
model_info = "Last revision on 9/16/2025"

# sources text (UPDATE and/or ADD as needed)
HCRIS_sources = "*Healthcare Cost Report Information System (HCRIS) FY2023 (https://tool.nashp.org/)"

# constants (only UPDATE if necessary)
rn_share_cl_constant = 0.80
avg_fte_rn_constant = 0.90
flo_rn_fee_constant = 50000.00

# instantiate Florence Calculation
class Florence:
    def __init__(self, clc, clh, cl_fte, slr, rn_share_cl, avg_fte_rn, flo_rn_fee, system_name, data_sources):
        self.clc = clc
        self.clh = clh
        self.cl_fte = cl_fte
        self.slr = slr
        self.rn_share_cl = rn_share_cl
        self.avg_fte_rn = avg_fte_rn
        self.flo_rn_fee = flo_rn_fee
        self.system_name = system_name
        self.data_sources = data_sources

# UPDATE class parameters as appropriate
huh = Florence(clc=22450115.00, clh=152801.00, cl_fte=73.46, slr=74.94, rn_share_cl=rn_share_cl_constant, avg_fte_rn=avg_fte_rn_constant, flo_rn_fee=flo_rn_fee_constant, system_name='Howard University Hospital', data_sources=HCRIS_sources)

nb = Florence(clc=9309771.00, clh=61030.00, cl_fte=152.54, slr=88.32, rn_share_cl=rn_share_cl_constant, avg_fte_rn=avg_fte_rn_constant, flo_rn_fee=flo_rn_fee_constant, system_name='NorthBay Health', data_sources=HCRIS_sources)

# functions
def contracted_hourly(clc, clh):
    contracted_hourly = clc/clh
    return contracted_hourly

def esimated_rn_needs(clh, rn_share_cl, avg_fte_rn):
    rn_contracted_hours_annually = clh * rn_share_cl
    rn_need_annually = rn_contracted_hours_annually * avg_fte_rn
    return rn_contracted_hours_annually, rn_need_annually

def default_values(flo_class):
    global d_clc, d_clh, d_cl_fte, d_slr, d_rn_share_cl, d_avg_fte_rn, d_flo_rn_fee, d_system_name, d_data_sources
    d_clc = flo_class.clc
    d_clh = flo_class.clh
    d_cl_fte = flo_class.cl_fte
    d_slr = flo_class.slr
    d_rn_share_cl = flo_class.rn_share_cl
    d_avg_fte_rn = flo_class.avg_fte_rn
    d_flo_rn_fee = flo_class.flo_rn_fee
    d_system_name = flo_class.system_name
    d_data_sources = flo_class.data_sources

# streamlit code
def main():
    st.title("Florence Financial Impact")    st.caption(model_info)
    st.sidebar.header("Staffing/Financial Information")
    selected_dept = st.sidebar.selectbox("Hospital/System:", ["Howard University Hospital", "NorthBay Health"])

    if selected_dept == "Howard University Hospital":
        default_values(huh)
    elif selected_dept == "NorthBay Health":
        default_values(nb)

    direct_clc = st.sidebar.number_input(label="Direct Patient Care Contracted Labor Cost*", min_value=0.00, max_value=999999999999.99, step=1.00, value=d_clc)
    direct_clh = st.sidebar.number_input(label="Direct Patient Care Contracted Labor Hours*", min_value=0.00, max_value=999999999999.99, step=1.00, value=d_clh)
    direct_cl_fte = st.sidebar.number_input(label="Direct Patient Care Contracted Labor FTE*", min_value=0.00, max_value=10000.00, step=1.00, value=d_cl_fte)
    direct_slr = st.sidebar.number_input(label="Direct Patient Care Labor Hourly Rate*", min_value=0.00, max_value=1000.00, step=1.00, value=d_slr)
    est_share_rn = st.sidebar.number_input(label="Estimated RN Share of Contract Labor", min_value = 0.00, max_value=1.00, step=0.01, value=d_rn_share_cl)
    average_fte_per_nurse = st.sidebar.number_input(label="Average FTE/Nurse", min_value=0.00, max_value=1.00, step=0.10, value=d_avg_fte_rn)
    # calculations for need - write these to the main page
    direct_patient_care_hourly_rate = direct_clc / direct_clh
    est_rn_contracted_labor_hrs_annually = direct_clh * est_share_rn
    est_rn_need_annually = est_rn_contracted_labor_hrs_annually / (2080 * average_fte_per_nurse)
    agency_hours_replaced = est_rn_contracted_labor_hrs_annually * 3
    agency_rn_hourly_diff = direct_patient_care_hourly_rate - direct_slr
    agency_rn_diff_3_yr = agency_hours_replaced * agency_rn_hourly_diff
    flo_placement_cost = d_flo_rn_fee
    total_flo_placement_cost = flo_placement_cost * est_rn_need_annually
    flo_hourly_diff = total_flo_placement_cost / agency_hours_replaced
    hourly_diff_agency_flo = agency_rn_hourly_diff - flo_hourly_diff
    total_savings_opp = agency_hours_replaced * hourly_diff_agency_flo
    st.sidebar.caption("Data entries are defaulted from data sources, but can be edited to change the projections")
    st.sidebar.caption(d_data_sources)

    st.header(d_system_name)
    st.write("")
    st.subheader("RN Needs and Agency Costs")
    st.write(f"Direct Patient Care Contracted Labor Hourly Rate: **${direct_patient_care_hourly_rate:,.2f}**")
    st.write(f"Estimated RN Contracted Labor Hours Annually: **{est_rn_contracted_labor_hrs_annually:,.2f}**")
    st.write(f"Estimated RN Need Annually: **{est_rn_need_annually:,.2f}**")
    st.write(f"Agency RN Hourly Differential Over Non-Contracted Direct Patient Care Rate: **${agency_rn_hourly_diff:,.2f}**")
    st.write(f"Agency Hours Used Over 3 Years (Flat): **{agency_hours_replaced:,.2f}**")
    st.write(f"Agency RN Cost Over 3 Years: **${agency_rn_diff_3_yr:,.2f}**")
    st.write("")
    st.subheader("How Florence Helps")
    st.write(f"Florence Placement Fee Per Nurse: **${flo_placement_cost:,.2f}**")
    st.write(f"Florence Hourly Differential (Fee Amortized) Over Non_Contracted Direct Patient Care Rate: **${flo_hourly_diff:,.2f}**")
    st.write(f"Florence RN Hourly Savings Over Agency RN: **${hourly_diff_agency_flo:,.2f}**")
    st.write("")
    st.subheader(f"Total Estimated RN Staffing Savings Opportunity: **${total_savings_opp:,.2f}**")
    

if __name__ == "__main__":
    main()