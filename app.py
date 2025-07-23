import streamlit as st
import numpy as np
import nashpy as nash
import matplotlib.pyplot as plt
from matrices import matrices
from fpdf import FPDF
import tempfile, os

st.set_page_config(layout="centered")
st.title("🤝 Negotiation Strategy Solver using Game Theory")

# Select Mode
mode = st.radio("🔧 Mode:", ["Built-in Scenario", "Custom Matrix"])

if mode == "Built-in Scenario":
    option = st.selectbox("📌 Choose built-in scenario:", list(matrices.keys()))
    matrix_np = np.array(matrices[option])
    st.write("### 📊 Payoff Matrix (Player A):")
    st.table(matrix_np)
    scenario_name = option

else:
    st.write("### 🔢 Enter Your Custom Matrix")
    rows = st.number_input("Number of rows (Player A strategies):", min_value=2, max_value=5, value=2, step=1)
    cols = st.number_input("Number of cols (Player B strategies):", min_value=2, max_value=5, value=2, step=1)
    
    custom = []
    for i in range(rows):
        row_vals = st.columns(cols)
        with st.expander(f"Row {i+1} values (Player B)"):  # ✅ Colon fixed here
            row = []
            for j, col_ in enumerate(row_vals):
                val = col_.number_input(f"R{i+1}-C{j+1}", value=0.0, step=0.5, key=f"cell_{i}_{j}")
                row.append(val)
            custom.append(row)
    matrix_np = np.array(custom)
    scenario_name = "Custom Matrix"
    st.write("Your matrix:")
    st.table(matrix_np)

# Solve the game
game = nash.Game(matrix_np)
results = []

try:
    equilibria = list(game.support_enumeration())
    if not equilibria:
        equilibria = list(game.vertex_enumeration())

    if equilibria:
        st.write("### ✅ Nash Equilibrium Strategy Suggestions:")
        for i, eq in enumerate(equilibria):
            a_strategy = np.round(eq[0], 3)
            b_strategy = np.round(eq[1], 3)

            st.success(f"🎯 Equilibrium {i+1}")
            st.write(f"🧑‍💼 **Player A:** `{a_strategy}`")
            st.write(f"🏢 **Player B:** `{b_strategy}`")
            results.append((i+1, a_strategy.tolist(), b_strategy.tolist()))

            # Plot
            fig, ax = plt.subplots()
            x = np.arange(len(a_strategy))
            x2 = np.arange(len(b_strategy))
            ax.bar(x - 0.15, a_strategy, width=0.3, label="Player A")
            ax.bar(x2 + 0.15, b_strategy, width=0.3, label="Player B")
            ax.set_title("Strategy Probability Distribution")
            ax.set_xlabel("Strategies")
            ax.set_ylabel("Probability")
            ax.legend()
            st.pyplot(fig)
    else:
        st.warning("🚫 No equilibrium found.")
        st.info("Try adjusting your matrix or switch to built-in scenarios.")

except Exception as e:
    st.error(f"❌ Error solving the game:\n{str(e)}")

# PDF generation
def generate_pdf(results, scenario):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=f"Nash Equilibrium Report: {scenario}", ln=True, align='C')
    for i, a, b in results:
        pdf.multi_cell(0, 8, txt=f"\nEquilibrium {i}:\nPlayer A: {a}\nPlayer B: {b}")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    pdf.output(tmp)
    return tmp

# Download PDF
if results:
    if st.button("📥 Download Report as PDF"):
        tmp_path = generate_pdf(results, scenario_name)
        with open(tmp_path, "rb") as f:
            st.download_button("📝 Download PDF",
                               f, file_name=f"{scenario_name.replace(' ', '_')}_Nash.pdf",
                               mime="application/pdf")
        os.remove(tmp_path)
