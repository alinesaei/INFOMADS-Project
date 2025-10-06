import streamlit as st
import pandas as pd
from core.data_models import Job, ParsedInstance
from core.scheduler import OnlineScheduler
from core.online_algorithms import ONLINE_POLICIES
from utils.parser import parse_test_instances
from utils.plotter import create_gantt_chart
import os

st.set_page_config(layout="wide")
st.title("Project: Scheduling to Save Your Life")
st.markdown("An interactive tool to simulate and visualize online scheduling algorithms.")


st.sidebar.header("⚙️ Controls")

st.sidebar.caption("Step 1: Select a test case from the project data file.")
data_file_path = os.path.join("data", "Test_Instances_Group10.txt")

try:
    with open(data_file_path, "r") as f:
        file_content = f.read()

    parsed_instances = parse_test_instances(file_content)

    if not parsed_instances:
        st.error(
            "The test instances file was found but could not be parsed. Please check the file format in `utils/parser.py`.")
        st.stop()

    instance_name = st.sidebar.selectbox(
        "Select a Test Instance", options=list(parsed_instances.keys())
    )
    instance = parsed_instances[instance_name]

    # --- 2. ALGORITHM SELECTION AND PARAMETERS ---
    st.sidebar.caption("Step 2: Choose an algorithm and configure its parameters.")
    policy_name = st.sidebar.selectbox("Select an Online Algorithm", options=list(ONLINE_POLICIES.keys()))
    policy_func = ONLINE_POLICIES[policy_name]

    params = {}
    if policy_name == "Profit-Aware EDF":
        with st.sidebar.expander("Algorithm Parameters"):
            params['w_profit'] = st.slider("Profit Weight", 0.1, 5.0, 1.0, 0.1,
                                           help="Higher values prioritize jobs with more profit/penalty potential.")
            params['w_deadline'] = st.slider("Deadline Urgency Weight", 0.0, 2.0, 0.1, 0.05,
                                             help="Higher values make the algorithm behave more like standard EDF.")

    # --- 3. RUN SIMULATION ---
    st.sidebar.caption("Step 3: Click the button to run the simulation.")
    if st.sidebar.button("🚀 Run Simulation", type="primary", use_container_width=True):
        # Store results in session state to persist them
        scheduler = OnlineScheduler(instance.jobs, policy_func, instance.T_max, params)
        st.session_state.result = scheduler.run()
        st.session_state.instance = instance
        st.session_state.policy_name = policy_name

    # --- 4. DISPLAY RESULTS ---
    if 'result' in st.session_state:
        # Retrieve results from session state
        result = st.session_state.result
        instance = st.session_state.instance
        policy_name = st.session_state.policy_name

        st.header(f"Results for `{instance.name}`")
        st.subheader(f"Algorithm: `{policy_name}`")

        tab1, tab2, tab3 = st.tabs(["📊 Visualization", "📈 Results Summary", "📋 Input Data"])

        with tab1:
            st.markdown("#### Schedule Gantt Chart")

            # --- NEW: Job Filter ---
            job_ids = [job.id for job in instance.jobs]
            visible_jobs = st.multiselect(
                "Filter Jobs to Display:",
                options=job_ids,
                default=job_ids,
                help="Select jobs to show in the chart to analyze specific interactions."
            )

            fig = create_gantt_chart(instance.jobs, result, instance.T_max, visible_jobs)
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.markdown("#### Performance Metrics")
            col1, col2, col3 = st.columns(3)
            col1.metric(
                "Total Profit",
                f"{result.total_profit}",
                f"{result.total_profit - instance.offline_profit:+} vs Offline Optimal",
                help="The final score of the online algorithm compared to the pre-calculated optimal score from the test file."
            )
            col2.metric("Jobs Completed", f"{len(result.completed_jobs)}")
            col3.metric("Jobs Failed", f"{len(result.failed_jobs)}")

            st.markdown("---")

            col_completed, col_failed = st.columns(2)
            with col_completed:
                st.success("Completed Job IDs")
                st.json(sorted(list(result.completed_jobs)))

            with col_failed:
                st.error("Failed Job IDs")
                st.json(sorted(list(result.failed_jobs)))

        with tab3:
            st.markdown("#### Job Data for Selected Instance")
            jobs_df = pd.DataFrame(instance.jobs)
            st.dataframe(jobs_df, use_container_width=True)

    else:
        st.info("Configure the settings in the sidebar and click 'Run Simulation' to see the results.")


except FileNotFoundError:
    st.error(f"Error: The data file was not found at '{data_file_path}'.")
    st.info(
        "Please make sure the 'Test_Instances_Group10.txt' file is located inside a 'data' folder in your project directory.")