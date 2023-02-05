import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


DATA_URL = ("https://www.moh.gov.sg/docs/librariesprovider5/excel-uploads/"
"fee-publication-data-july19---dec20-(for-download1).xlsx")

@st.cache
def load_data():
	data = pd.read_excel(
		DATA_URL, 
		sheet_name=2,
		usecols= [x for x in range(1,11)],
		skiprows=[0,1,2,3])
	data = data[data['Ward Type'].str.contains("Day Surgery")]
	sub_rows = data["Setting"] == 'Public Hospitals/Centres (Subsidised)'
	data.loc[sub_rows, "Hospital"] = data.loc[sub_rows, "Hospital"] + " (SUB)"
	pte_rows = data["Setting"] == 'Public Hospitals/Centres (Unsubsidised)'
	data.loc[pte_rows, "Hospital"] = data.loc[pte_rows, "Hospital"] + " (PTE)"


	data['TOSP Description'] = data['TOSP code'] + ": " + data['TOSP Description']

	return data


st.title("Day Surgery Bill Sizes")

df = load_data()

proceduresList = df['TOSP Description'].unique()
proceduresList.sort()
proceduresList = np.insert(proceduresList, 0, "")

st.markdown("**Data Source:** https://www.moh.gov.sg/cost-financing/fee-benchmarks-and-bill-amount-information")


st.markdown("### Select your procedure")
procedure = st.selectbox("", proceduresList)

df = df[df['TOSP Description']==procedure]

if df.shape[0] != 0:

	fig, ax = plt.subplots()


	color_dict = {
				"Private Hospitals": "darkorange", 
				"Public Hospitals/Centres (Unsubsidised)": "forestgreen", 
				"Public Hospitals/Centres (Subsidised)": "dodgerblue"}

	for x in ["Private Hospitals", "Public Hospitals/Centres (Unsubsidised)", "Public Hospitals/Centres (Subsidised)"]:
		df2 = df[df['Setting'] == x]
		if df2.shape[0] == 0:
			continue
		label = df2['Hospital']
		bill_median = df2['P50 Bill']
		bars = ax.barh(label, bill_median, label=x, color = color_dict[x])
		ax.bar_label(bars, labels = "$"+np.round(bill_median).astype(int).astype(str), padding = 3)

	plt.xlim(0, df['P50 Bill'].max()*1.15)
	plt.xlabel("Historical Median Bill Size")
	plt.ylabel("Medical Instituions")
	plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15))
	st.pyplot(fig)
else: 
	st.write("No data is selected")

st.markdown("**Note:** Figures shown on this page include GST and are based on the median of "
	"actual transacted fees across the medical institutions, from **1 July 2019 to 31 December 2020**. " 
	"To ensure that there are adequate cases for meaningful comparisons, procedures at a specific MI with less than 10 cases will not be shown.")