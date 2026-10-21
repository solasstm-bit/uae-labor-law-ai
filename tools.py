"""Tools tab: gratuity calculator, resignation letter, dispute guide (v2.3)."""
from datetime import datetime

import streamlit as st


def render():
    st.markdown("### 🧮 End-of-Service Gratuity Calculator")
    st.caption("Art. 51(2), FD-L 33/2021 — basic wage only; resignation before 5 years reduces the amount.")
    g1, g2, g3 = st.columns(3)
    basic = g1.number_input("Monthly basic salary (AED)", min_value=0.0, value=5000.0, step=100.0)
    years = g2.number_input("Years of service", min_value=0.0, value=3.0, step=0.25)
    rmode = g3.selectbox("Resignation status", ["No resignation / 5+ yrs", "Resigned 1–3 yrs", "Resigned 3–5 yrs"])

    def gratuity_math(b, y, rm):
        daily = b / 30
        total = min(y, 5) * daily * 21 + max(0, y - 5) * daily * 30
        note = "✅ Full gratuity applies."
        if y < 1:
            total = 0
            note = "❌ Under 1 year of service → no gratuity."
        elif rm.startswith("Resigned 1–3"):
            total /= 3
            note = "⚠️ Resigned after 1–3 years → ⅓ of gratuity (Art. 51(2))."
        elif rm.startswith("Resigned 3–5"):
            total = total * 2 / 3
            note = "⚠️ Resigned after 3–5 years → ⅔ of gratuity (Art. 51(2))."
        if b and total > b * 24:
            total = b * 24
            note += " Capped at 2 years' basic wage."
        return total, note

    total, note = gratuity_math(basic, years, rmode)
    st.success(f"**Estimated gratuity: AED {total:,.0f}**  \n{note}")

    st.markdown("---")
    st.markdown("### 📝 Resignation Letter Generator")
    with st.form("resign_form"):
        r1, r2 = st.columns(2)
        name = r1.text_input("Your full name")
        comp = r2.text_input("Company / HR name")
        job = st.text_input("Your position")
        notice = st.number_input("Notice period (days)", min_value=30, max_value=90, value=30)
        go = st.form_submit_button("Generate Letter")
    if go and name and comp:
        letter = f"""**RESIGNATION LETTER**

Date: {datetime.today().strftime('%d %B %Y')}

To: {comp}
Subject: Resignation — {job}

Dear {comp},

I am writing to formally resign from my position as {job}, in accordance with Article 42 of Federal Decree-Law No. 33 of 2021. My last working day will be {notice} days from the date of this letter, following my {notice}-day contractual notice period.

Kindly settle my end-of-service entitlements (gratuity, leave balance and accrued dues) within 14 days of my final working day, per Articles 51–53.

Yours sincerely,
**{name}**"""
        st.markdown(letter)
        st.download_button("⬇️ Download (TXT)", letter, "resignation_letter.txt")

    st.markdown("---")
    st.markdown("### 🛡️ Labour Dispute Guide + MOHRE Contacts")
    st.markdown("""
- ☎️ **MOHRE call centre:** 600 59 0000
- 📱 **MOHRE UAE app** — file complaints, view your contract
- 🌐 **mohre.gov.ae** — e-services, complaint tracking
- 🤝 MOHRE attempts settlement within 2 weeks, then referral to labour court
- ⚖️ Claims under AED 50,000: **exempt from court fees** (Art. 16)
- ⏰ Limitation period: **1 year** from when the right became due (Art. 54)
""")