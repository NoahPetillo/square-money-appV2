import pandas as pd
import altair as alt
import streamlit as st

#Sidebar -- Select
servers = ["Server 1", "Server 2", "Server 3", "Server 4", "Server 5"] # TODO Add names
bussers = ["Busser 1", "Busser 2", "Busser 3"]
runners = ["Runner 1", "Runner 2", "Runner 3"]

st.sidebar.header("Data")
servers_on = st.sidebar.multiselect("Servers on:", servers,)
tips = []
sales = []
for server in servers_on: #Makes sure inputs are a number, adds them to list tips which will be used for pd df
    tip = st.sidebar.text_input(f"{server} tips:").strip()
    sale = st.sidebar.text_input(f"{server} sales:").strip()
    try:
        tips.append(float(tip))
        sales.append(float(sale))
        # st.sidebar.text(f"Nice job {server}!")# TODO -- Shit on underperforming severs
    except:
        st.sidebar.text("Please enter server's tips in number format")

bussers_on = st.sidebar.multiselect("Bussers on:", bussers) 

runners_on = st.sidebar.multiselect("Runners on:", runners)

end_shift_time = st.sidebar.selectbox("What time did we close today?", ["9:00", "10:00"] )
if end_shift_time == "9:00":
    end_shift_time = 2100
else:
    end_shift_time = 2200


time_worked_servers = {}
for server in servers_on:
    time_worked_servers[server] = end_shift_time
    
earlybird_response = st.sidebar.multiselect("Did anyone leave early?", ["Server", "Busser"])
if "Server" in earlybird_response:
    earlybirds = st.sidebar.multiselect("Which server(s)?", servers_on)
    for earlybird in earlybirds:
        time = st.sidebar.text_input(f"Time {earlybird} left:").strip()
        try:
            time_worked_servers[earlybird] = int(time)  ##Make Dict pointing server:time left
        except:
            st.sidebar.text("Please enter time in 24hr format (ex. 7:30 = 1930)")
        
time_worked_bussers = {}
for busser in bussers_on:
    time_worked_bussers[busser] = end_shift_time
    
if "Busser" in earlybird_response:
    earlybirds = st.sidebar.multiselect("Which busser(s)?", bussers_on)
    for earlybird in earlybirds:
        time = st.sidebar.text_input(f"Time {earlybird} left:").strip()
        try:
            time_worked_bussers[earlybird] = int(time)  ##Make Dict pointing busser:time_4left
        except:
            st.sidebar.text("Please enter time in 24hr format (ex. 7:30 = 1930)") 
#     
##           
###
####
##### Mathy math time
total_tips = sum(tips)
total_sales = sum(sales)
runners_cut = len(servers_on)* len(runners_on) * 10 #runners get 10 dollars per server each
if bussers_on == 1:
    bussers_cut = 0.1 * total_tips
else:
    bussers_cut = 0.15 * total_tips

servers_cut = total_tips - runners_cut - bussers_cut


for server in time_worked_servers:
    time_worked_servers[server] -= 1700
for busser in time_worked_bussers:  # Now, instead of being {person : time they left}, it is {person : hours they worked}
    time_worked_bussers[busser] -= 1700


percentage_of_server_cut = {} #These are respective cut, so 15% is 15% of server cut, not total tips
percentage_of_busser_cut = {}

total_hours_worked_servers = sum(time_worked_servers.values())
total_hours_worked_bussers = sum(time_worked_bussers.values())
for server in servers_on:
    percentage = round(time_worked_servers[server] / total_hours_worked_servers, 3)
    percentage_of_server_cut[server] = percentage
#                                      # creates dictionaries like this: {person : percentage of respective cut}
for busser in bussers_on:
    percentage = round(time_worked_bussers[busser] / total_hours_worked_bussers, 3)
    percentage_of_busser_cut[busser] = percentage
# print(f"{percentage_of_server_cut} \n {percentage_of_busser_cut}")

money_earned_servers = {}
money_earned_bussers = {}

for server in servers_on:
    money_earned = round(percentage_of_server_cut[server] * servers_cut, 2)
    money_earned_servers[server] = money_earned
for busser in bussers_on:
    money_earned = round(percentage_of_busser_cut[busser] * bussers_cut, 2)
    money_earned_bussers[busser] = money_earned
    
# print(money_earned_bussers, money_earned_servers)

#
##
###
####
##### Constructing Dataframe
combined_names = list(money_earned_servers.keys()) + list(money_earned_bussers.keys())
combined_money_earned = list(money_earned_servers.values()) + list(money_earned_bussers.values())
combined_hours_worked = list(time_worked_servers.values()) + list(time_worked_bussers.values())


for busser in bussers_on:
    tips.append(0) #even out list
    sales.append(0)

type_of_employee = []
for server in servers_on:
    type_of_employee.append("SERVER") #For coloring purposes later
for busser in bussers_on:
    type_of_employee.append("BUSSER")
data = {
    "Name": combined_names,
    "Money Made": combined_money_earned,
    "Hours Worked": combined_hours_worked,
    "Tips Made": tips,
    "Sales Made": sales,
    "Type": type_of_employee
}

df = pd.DataFrame(data)
df["Ratio"] = round(df["Tips Made"] / df["Sales Made"], 2)

print(df)

df_servers = df[df["Type"] == "SERVER"]
df_servers = df_servers.sort_values("Ratio", ascending=False)
highest_tipped_ratio = df_servers.iloc[0]["Ratio"]
highest_tipped_ratio_person = df_servers.iloc[0]["Name"]

#
##
###
####
##### Main Dashboard:
st.title("Stats")
col1, col2, col3, col4= st.columns([1,1,1,1])
col1.metric(label = "Total sales", value = f"${total_sales}")
col2.metric(label = "Total tips", value =f"${total_tips}")
col3.metric(label = "Highest earner", value =f"{df_servers["Name"].iloc[0]}")
col4.metric(
    label="Highest percentage tipped",
    value=highest_tipped_ratio_person,
    delta=f"{highest_tipped_ratio * 100}%"
)
# First Graph, Who made the most:
st.subheader("Who brought in the most?")
if not df_servers.empty:
    
    most_made = alt.Chart(df_servers).mark_bar().encode(
        x = alt.X("Name:N", sort="-y", title="Servers"),
        y = alt.Y("Tips Made:Q", title="Tips Made ($)"),
        tooltip=["Name", "Tips Made", "Hours Worked"]
    ).properties(
        width = 600, height = 400
    )
    st.altair_chart(most_made, use_container_width=True)
else:
    st.info("Not enough data")
#
#
# Second graph, Total Tip Breakdown
st.subheader("How much everyone made")
if not df.empty:
    total_breakdown = alt.Chart(df).mark_bar().encode(
        x = alt.X("Name:N", sort = "-y", title = "Tip breakdown"),
        y = alt.Y("Money Made:Q", title= "Tips Made ($)"),
        color = alt.Color("Type:N", title="Role",),
        tooltip= ["Name", "Money Made", "Hours Worked" ]
    ).properties(
        width = 600, height = 400
    )
    st.altair_chart(total_breakdown, use_container_width=True)
else:
    st.info("Not enough data")
#
#
# Third graph, tips_earned to money made chart
