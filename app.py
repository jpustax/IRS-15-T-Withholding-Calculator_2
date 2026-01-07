import streamlit as st

# ======================
# Page config
# ======================
st.set_page_config(
    page_title="IRS 15-T Withholding Calculator",
    page_icon="💰",
    layout="centered"
)

# ======================
# IRS 15-T (2024)
# Percentage Method
# Annual Basis
# ======================
def percentage_method_tax_annual(annual_wages, filing_status):

    if filing_status == "Single":
        brackets = [
            (0, 0),
            (11000, 1100),
            (44725, 5147),
            (95375, 16290),
            (182100, 37104),
            (231250, 52832),
            (578125, 174238)
        ]
        rates = [0.10, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]

    elif filing_status == "Married filing jointly":
        brackets = [
            (0, 0),
            (22000, 2200),
            (89450, 10294),
            (190750, 32580),
            (364200, 74208),
            (462500, 105664),
            (693750, 186601)
        ]
        rates = [0.10, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]

    else:  # Head of Household
        brackets = [
            (0, 0),
            (15700, 1570),
            (59850, 6868),
            (95350, 14678),
            (182100, 35498),
            (231250, 51226),
            (578100, 172623.50)
        ]
        rates = [0.10, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]

    for i in range(len(brackets) - 1, -1, -1):
        limit, base_tax = brackets[i]
        if annual_wages > limit:
            return base_tax + (annual_wages - limit) * rates[i]

    return 0


def calculate_annual_withholding(
    annual_salary,
    filing_status,
    step3_credit,
    step4a_other_income,
    step4b_deductions
):

    taxable_income = (
        annual_salary
        + step4a_other_income
        - step4b_deductions
    )
    taxable_income = max(0, taxable_income)

    federal_tax = percentage_method_tax_annual(
        taxable_income,
        filing_status
    )

    federal_tax = max(0, federal_tax - step3_credit)

    social_security = min(annual_salary, 168600) * 0.062
    medicare = annual_salary * 0.0145

    total_tax = federal_tax + social_security + medicare
    net_income = annual_salary - total_tax

    effective_rate = (
        total_tax / annual_salary * 100
        if annual_salary > 0 else 0
    )

    return (
        federal_tax,
        social_security,
        medicare,
        total_tax,
        net_income,
        effective_rate
    )

# ======================
# UI
# ======================
st.title("💰 IRS 15-T 연봉 원천징수 계산기 (2024)")
st.caption("IRS Publication 15-T · Percentage Method · Annual Basis")

st.markdown("---")

# Input section
with st.container():
    st.subheader("① 급여 및 W-4 정보 입력")

    col1, col2 = st.columns(2)

    with col1:
        annual_salary = st.number_input(
            "연봉 ($)",
            min_value=0.0,
            step=1000.0,
            format="%.0f"
        )

        filing_status = st.selectbox(
            "Filing Status (W-4 Step 1)",
            ["Single", "Married filing jointly", "Head of Household"]
        )

    with col2:
        step3_credit = st.number_input(
            "Dependents Credit (Step 3)",
            min_value=0.0,
            step=500.0,
            format="%.0f"
        )

        step4a_other_income = st.number_input(
            "Other Income (Step 4a)",
            min_value=0.0,
            step=1000.0,
            format="%.0f"
        )

        step4b_deductions = st.number_input(
            "Deductions (Step 4b)",
            min_value=0.0,
            step=1000.0,
            format="%.0f"
        )

st.markdown("---")

# Calculate
if st.button("📊 원천징수 계산하기", use_container_width=True):

    federal, ss, medicare, total, net, rate = calculate_annual_withholding(
        annual_salary,
        filing_status,
        step3_credit,
        step4a_other_income,
        step4b_deductions
    )

    st.subheader("② 연봉 기준 원천징수 결과")

    m1, m2, m3 = st.columns(3)
    m1.metric("연방 소득세", f"${federal:,.0f}")
    m2.metric("사회보장세", f"${ss:,.0f}")
    m3.metric("메디케어세", f"${medicare:,.0f}")

    st.markdown("")

    m4, m5, m6 = st.columns(3)
    m4.metric("총 세금", f"${total:,.0f}")
    m5.metric("실수령 연봉", f"${net:,.0f}")
    m6.metric("실효 원천징수율", f"{rate:.2f}%")

    st.markdown("---")
    st.caption(
        "※ 본 계산기는 IRS Publication 15-T (2024) 기준 참고용입니다. "
        "실제 급여 원천징수는 고용주의 급여 시스템을 따르십시오."
    )
